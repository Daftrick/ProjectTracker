import csv
import io
import os
import re
import uuid
from datetime import date, datetime

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, session, url_for

from ..catalog import catalog_maps, catalog_name_key, hydrate_ldm, hydrate_ldm_item, safe_float
from ..consistency import pick_active_quote
from ..csv_import import parse_ldm_csv
from ..deletions import purge_deleted_catalog_items_from_record
from ..drive import active_drive_paths, folder_name, load_config, parse_csv_plano_filename
from ..form_models import ldm_from_form
from ..ldm_sync import append_missing_bundle_items_to_ldm, missing_ldm_items_from_bundles
from ..pdfs import build_ldm_pdf
from ..storage import load, new_id, save, today
from ..validators import validate_ldm_form

bp = Blueprint("materials_bp", __name__)


def _clean_form_text(value):
    return str(value or "").strip()


def _find_project(project_id):
    return next((item for item in load("projects") if item["id"] == project_id), None)


def _project_drive_folder(project):
    cfg = load_config()
    root = active_drive_paths(cfg)["projects"]
    if not root:
        return None
    return os.path.join(root, folder_name(project))


def _csv_path_for_project(project, filename):
    clean_name = os.path.basename(_clean_form_text(filename))
    if not clean_name.lower().endswith(".csv"):
        return clean_name, None
    if not parse_csv_plano_filename(clean_name, project.get("clave")):
        return clean_name, None
    folder = _project_drive_folder(project)
    if not folder:
        return clean_name, None
    csv_path = os.path.abspath(os.path.join(folder, clean_name))
    folder_path = os.path.abspath(folder)
    if not csv_path.startswith(folder_path + os.sep) or not os.path.isfile(csv_path):
        return clean_name, None
    return clean_name, csv_path


def _ldm_uses_csv(ldm, filename):
    clean_name = os.path.basename(_clean_form_text(filename)).lower()
    sources = []
    for key in ("csv_origen", "csv_origin", "csv_filename"):
        if ldm.get(key):
            sources.append(ldm.get(key))
    sources.extend(ldm.get("csv_sources", []) or [])
    return clean_name in {os.path.basename(str(source or "").strip()).lower() for source in sources}


def _csv_already_imported(project_id, filename):
    return next(
        (
            ldm
            for ldm in load("materiales")
            if ldm.get("project_id") == project_id and _ldm_uses_csv(ldm, filename)
        ),
        None,
    )


def _hydrate_import_items(items):
    catalog_by_id, catalog_by_name = catalog_maps()
    hydrated_items = []
    missing_catalog = []
    for item in items:
        hydrated = hydrate_ldm_item(item, catalog_by_id, catalog_by_name)
        hydrated["qty_csv"] = item.get("qty_csv", hydrated.get("qty", 0))
        hydrated["qty_editada"] = item.get("qty_editada", False)
        hydrated["origen"] = item.get("origen", "csv")
        hydrated_items.append(hydrated)
        if not hydrated.get("catalog_linked"):
            missing_catalog.append(hydrated.get("description", ""))
    return hydrated_items, missing_catalog


def _csv_item_lookup(items):
    lookup = {}
    for item in items:
        key = (catalog_name_key(item.get("description", "")), str(item.get("unit", "")).strip().lower())
        lookup.setdefault(key, []).append(item)
    return lookup


def _attach_csv_item_metadata(items, csv_items):
    lookup = _csv_item_lookup(csv_items)
    enriched = []
    for item in items:
        current = dict(item)
        key = (catalog_name_key(current.get("description", "")), str(current.get("unit", "")).strip().lower())
        source = lookup.get(key, []).pop(0) if lookup.get(key) else None
        if source:
            qty_csv = float(source.get("qty_csv", source.get("qty", current.get("qty", 0))) or 0)
            current["qty_csv"] = qty_csv
            current["qty_editada"] = round(float(current.get("qty", 0) or 0), 6) != round(qty_csv, 6)
            current["origen"] = "csv"
        else:
            current["qty_csv"] = None
            current["qty_editada"] = False
            current["origen"] = "manual"
        enriched.append(current)
    return enriched


def _safe_filename_token(value):
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "-", _clean_form_text(value)).strip("-._")
    return cleaned or "LDM"


def _csv_number(value):
    return f"{safe_float(value):g}"


def _ldm_csv_response(project, ldm):
    hydrated = hydrate_ldm(ldm, *catalog_maps())
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(["description", "unit", "qty", "catalog_item_id", "proveedor", "fecha", "ldm_number"])
    for item in hydrated.get("items", []):
        writer.writerow([
            item.get("description", ""),
            item.get("unit", "pza"),
            _csv_number(item.get("qty", 0)),
            item.get("catalog_item_id", ""),
            hydrated.get("proveedor", ""),
            hydrated.get("fecha", ""),
            hydrated.get("ldm_number", ""),
        ])

    filename = f"{_safe_filename_token(hydrated.get('ldm_number') or project.get('clave'))}.csv"
    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


def _render_ldm_form(project, ldm, field_errors=None):
    return render_template(
        "ldm_form.html",
        project=project,
        ldm=ldm,
        proveedores=load("proveedores"),
        today=today(),
        field_errors=field_errors or {},
    )


def _bundle_suggestion_ldm(project_id, project):
    catalog_by_id, catalog_by_name = catalog_maps()
    project_quotes = [
        quote
        for quote in load("quotes")
        if quote.get("project_id") == project_id
    ]
    active_quote = pick_active_quote(project_quotes)
    if not active_quote:
        return None, "No hay cotización base activa para sugerir materiales."

    project_ldms = [
        hydrate_ldm(item, catalog_by_id, catalog_by_name)
        for item in load("materiales")
        if item.get("project_id") == project_id
    ]
    suggestions = missing_ldm_items_from_bundles(
        active_quote,
        project_ldms,
        load("bundles"),
        catalog_by_id=catalog_by_id,
    )
    if not suggestions:
        return None, "No hay faltantes técnicos por sugerir desde bundles."

    return {
        "is_bundle_suggestion": True,
        "ldm_number": "Sugerida desde bundles",
        "proveedor": "",
        "fecha": today(),
        "notes": f"Sugerida desde {active_quote.get('quote_number') or 'cotización activa'}",
        "items": suggestions,
        "bundle_suggestion_count": len(suggestions),
        "source_quote_number": active_quote.get("quote_number", ""),
    }, None


@bp.route("/projects/<project_id>/ldm/new", methods=["GET", "POST"], endpoint="new_ldm")
def new_ldm(project_id):
    project = _find_project(project_id)
    if not project:
        return redirect(url_for("dashboard"))
    if request.method == "POST":
        validation = validate_ldm_form(request.form)
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return _render_ldm_form(
                project,
                ldm_from_form(request.form),
                field_errors=validation["field_errors"],
            )
        all_ldms = load("materiales")
        seq = len([item for item in all_ldms if item["project_id"] == project_id]) + 1
        ldm = {
            "id": new_id(),
            "project_id": project_id,
            "ldm_number": f"LDM-{project['clave']}-{seq:02d}",
            "seq": seq,
            "proveedor": validation["proveedor"],
            "fecha": validation["fecha"],
            "items": validation["items"],
            "subtotal_cot": validation["subtotal_cot"],
            "cot_proveedor": validation["cot_proveedor"],
            "notes": validation["notes"],
            "created_at": today(),
        }
        all_ldms.append(ldm)
        save("materiales", all_ldms)
        flash(f"Lista {ldm['ldm_number']} creada.", "success")
        return redirect(url_for("materials_bp.edit_ldm", project_id=project_id, ldm_id=ldm["id"]))
    if request.args.get("from_bundles") == "1":
        suggestion_ldm, message = _bundle_suggestion_ldm(project_id, project)
        if not suggestion_ldm:
            flash(message, "info")
            return _render_ldm_form(project, None)
        flash(f"Se precargaron {suggestion_ldm['bundle_suggestion_count']} material(es) sugeridos desde bundles.", "info")
        return _render_ldm_form(project, suggestion_ldm)
    return _render_ldm_form(project, None)


@bp.route("/projects/<project_id>/ldm/import/<path:filename>", methods=["GET", "POST"], endpoint="import_ldm_csv")
def import_ldm_csv(project_id, filename):
    project = _find_project(project_id)
    if not project:
        return redirect(url_for("dashboard"))
    if project.get("closed_at"):
        flash("El proyecto está cerrado. Reábrelo para importar una LDM.", "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    clean_name, csv_path = _csv_path_for_project(project, filename)
    if not csv_path:
        flash("CSV de plano no encontrado o con nombre inválido para este proyecto.", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-documentos")

    existing = _csv_already_imported(project_id, clean_name)
    if existing:
        flash(f"{clean_name} ya está vinculado a {existing.get('ldm_number', 'una LDM')}.", "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    parsed = parse_ldm_csv(csv_path, catalog=load("catalogo"))
    if parsed["errors"]:
        for error in parsed["errors"]:
            flash(error, "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-documentos")

    if request.method == "POST":
        validation = validate_ldm_form(request.form)
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            fallback = {
                "is_import_preview": True,
                "ldm_number": f"CSV: {clean_name}",
                "csv_origen": clean_name,
            }
            return _render_ldm_form(
                project,
                ldm_from_form(request.form, fallback_ldm=fallback),
                field_errors=validation["field_errors"],
            )
        all_ldms = load("materiales")
        seq = len([item for item in all_ldms if item["project_id"] == project_id]) + 1
        items = _attach_csv_item_metadata(validation["items"], parsed["items"])
        ldm = {
            "id": new_id(),
            "project_id": project_id,
            "ldm_number": f"LDM-{project['clave']}-{seq:02d}",
            "seq": seq,
            "proveedor": validation["proveedor"],
            "fecha": validation["fecha"],
            "items": items,
            "subtotal_cot": validation["subtotal_cot"],
            "cot_proveedor": validation["cot_proveedor"],
            "notes": validation["notes"],
            "csv_origen": clean_name,
            "csv_sources": [clean_name],
            "created_at": today(),
        }
        all_ldms.append(ldm)
        save("materiales", all_ldms)
        flash(f"Lista {ldm['ldm_number']} importada desde {clean_name}.", "success")
        return redirect(url_for("materials_bp.edit_ldm", project_id=project_id, ldm_id=ldm["id"]))

    items, missing_catalog = _hydrate_import_items(parsed["items"])
    metadata = parsed["metadata"]
    preview = {
        "is_import_preview": True,
        "ldm_number": f"CSV: {clean_name}",
        "proveedor": metadata.get("proveedor", ""),
        "fecha": metadata.get("fecha", today()),
        "notes": f"Importada desde {clean_name}",
        "items": items,
        "csv_origen": clean_name,
    }
    if metadata.get("proyecto_clave") and metadata["proyecto_clave"] != project.get("clave"):
        flash("La clave de proyecto indicada en el CSV no coincide con este proyecto.", "warning")
    if missing_catalog:
        flash(f"{len(missing_catalog)} artículo(s) no tienen coincidencia exacta en catálogo.", "warning")
    return _render_ldm_form(project, preview)


@bp.route("/projects/<project_id>/ldm/<ldm_id>/edit", methods=["GET", "POST"], endpoint="edit_ldm")
def edit_ldm(project_id, ldm_id):
    project = _find_project(project_id)
    all_ldms = load("materiales")
    ldm = next((item for item in all_ldms if item["id"] == ldm_id), None)
    if not project or not ldm:
        return redirect(url_for("project_detail", project_id=project_id))
    if request.method == "POST":
        validation = validate_ldm_form(request.form)
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return _render_ldm_form(
                project,
                ldm_from_form(request.form, fallback_ldm=ldm),
                field_errors=validation["field_errors"],
            )
        ldm["proveedor"] = validation["proveedor"]
        ldm["fecha"] = validation["fecha"]
        ldm["items"] = validation["items"]
        ldm["subtotal_cot"] = validation["subtotal_cot"]
        ldm["cot_proveedor"] = validation["cot_proveedor"]
        ldm["notes"] = validation["notes"]
        save("materiales", all_ldms)
        flash("Lista de materiales actualizada.", "success")
        return redirect(url_for("materials_bp.edit_ldm", project_id=project_id, ldm_id=ldm_id))
    hydrated = hydrate_ldm(ldm, *catalog_maps())
    return _render_ldm_form(project, hydrated)


@bp.route("/api/ldm/<ldm_id>/costo", methods=["POST"], endpoint="api_ldm_set_costo")
def api_ldm_set_costo(ldm_id):
    data = request.get_json(force=True) or {}
    try:
        subtotal = round(float(data.get("subtotal_cot", 0)), 2)
    except (TypeError, ValueError):
        return jsonify({"error": "Valor inválido"}), 400
    all_ldms = load("materiales")
    ldm = next((item for item in all_ldms if item["id"] == ldm_id), None)
    if not ldm:
        return jsonify({"error": "LDM no encontrada"}), 404
    ldm["subtotal_cot"] = subtotal
    save("materiales", all_ldms)
    return jsonify({"ok": True, "subtotal_cot": subtotal})


@bp.route("/projects/<project_id>/ldm/<ldm_id>/csv", endpoint="ldm_csv")
def ldm_csv(project_id, ldm_id):
    project = _find_project(project_id)
    ldm = next(
        (
            item
            for item in load("materiales")
            if item.get("id") == ldm_id and item.get("project_id") == project_id
        ),
        None,
    )
    if not project or not ldm:
        flash("Lista no encontrada.", "danger")
        return redirect(url_for("dashboard"))
    return _ldm_csv_response(project, ldm)


@bp.route("/projects/<project_id>/ldm/<ldm_id>/sync-bundles", methods=["POST"], endpoint="sync_ldm_bundles")
def sync_ldm_bundles(project_id, ldm_id):
    project = _find_project(project_id)
    all_ldms = load("materiales")
    ldm = next((item for item in all_ldms if item.get("id") == ldm_id and item.get("project_id") == project_id), None)
    if not project or not ldm:
        flash("Lista no encontrada.", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")
    if project.get("closed_at"):
        flash("El proyecto está cerrado. Reábrelo para sincronizar materiales.", "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    catalog_by_id, catalog_by_name = catalog_maps()
    project_quotes = [
        quote
        for quote in load("quotes")
        if quote.get("project_id") == project_id
    ]
    active_quote = pick_active_quote(project_quotes)
    project_ldms = [
        hydrate_ldm(item, catalog_by_id, catalog_by_name)
        for item in all_ldms
        if item.get("project_id") == project_id
    ]
    updated_ldm, additions = append_missing_bundle_items_to_ldm(
        ldm,
        active_quote,
        project_ldms,
        load("bundles"),
        catalog_by_id=catalog_by_id,
    )
    if not additions:
        flash("No hay faltantes técnicos por sincronizar desde bundles.", "info")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    ldm.update(updated_ldm)
    save("materiales", all_ldms)
    flash(f"Se agregaron {len(additions)} material(es) faltante(s) a {ldm.get('ldm_number', 'la LDM')}.", "success")
    return redirect(url_for("materials_bp.edit_ldm", project_id=project_id, ldm_id=ldm_id))


@bp.route("/projects/<project_id>/ldm/<ldm_id>/delete", methods=["POST"], endpoint="delete_ldm")
def delete_ldm(project_id, ldm_id):
    save("materiales", [item for item in load("materiales") if item["id"] != ldm_id])
    flash("Lista eliminada.", "warning")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")


@bp.route(
    "/projects/<project_id>/ldm/<ldm_id>/purge-deleted-catalog",
    methods=["POST"],
    endpoint="purge_ldm_deleted_catalog_items",
)
def purge_ldm_deleted_catalog_items(project_id, ldm_id):
    all_ldms = load("materiales")
    ldm = next((item for item in all_ldms if item["id"] == ldm_id and item["project_id"] == project_id), None)
    if not ldm:
        flash("Lista no encontrada.", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    updated_ldm, removed = purge_deleted_catalog_items_from_record(ldm)
    if any("precio_cot" in item or "total_cot" in item for item in updated_ldm.get("items", [])):
        updated_ldm["subtotal_cot"] = round(
            sum(
                safe_float(item.get("total_cot"))
                or safe_float(item.get("qty", 0)) * safe_float(item.get("precio_cot", 0))
                for item in updated_ldm.get("items", [])
            ),
            2,
        )
    ldm.update(updated_ldm)
    save("materiales", all_ldms)
    flash(f"Se eliminaron {removed} artículo(s) con catálogo eliminado de la LDM.", "warning")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")


@bp.route("/projects/<project_id>/ldm/<ldm_id>/set_cot", methods=["POST"], endpoint="set_ldm_cot")
def set_ldm_cot(project_id, ldm_id):
    all_ldms = load("materiales")
    ldm = next((item for item in all_ldms if item["id"] == ldm_id), None)
    if ldm:
        ldm["cot_proveedor"] = _clean_form_text(request.form.get("cot_proveedor")) or None
        save("materiales", all_ldms)
        flash("Número de cotización del proveedor guardado.", "success")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")


@bp.route("/projects/<project_id>/ldm/<ldm_id>/pdf", endpoint="ldm_pdf")
def ldm_pdf(project_id, ldm_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    ldm = next((item for item in load("materiales") if item["id"] == ldm_id), None)
    if not project or not ldm:
        flash("Lista no encontrada.", "danger")
        return redirect(url_for("dashboard"))
    hydrated = hydrate_ldm(ldm, *catalog_maps())
    cfg = load_config()
    root = active_drive_paths(cfg)["projects"]
    drive_folder = folder_name(project)
    project_folder = os.path.join(root, drive_folder) if root else None
    if not project_folder or not os.path.isdir(project_folder):
        flash("Carpeta del proyecto no encontrada en Drive. Verifica Ajustes.", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")
    try:
        date_token = datetime.strptime(hydrated.get("fecha", ""), "%Y-%m-%d").strftime("%y%m%d")
    except Exception:
        date_token = date.today().strftime("%y%m%d")
    pdf_name = f"LDM-{project['clave']}-{hydrated.get('seq', 1):02d}-{date_token}.pdf"
    pdf_path = os.path.join(project_folder, pdf_name)
    try:
        build_ldm_pdf(project, hydrated, pdf_path)
        flash(f"PDF generado en Drive: {pdf_name}", "success")
    except Exception as exc:
        flash(f"Error al generar PDF: {exc}", "danger")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")


# ── Importación de LDM desde PDF de proveedor ────────────────────────────────

import json as _json
import tempfile as _tempfile

from ..pdf_ldm_import import extract_items_from_pdf


def _pdf_import_session_key(project_id):
    return f"pdf_import_{project_id}"


def _pdf_import_dir():
    path = os.path.join(_tempfile.gettempdir(), "projecttracker_pdf_imports")
    os.makedirs(path, exist_ok=True)
    return path


def _pdf_import_path(token):
    safe_token = re.sub(r"[^a-f0-9]", "", str(token or "").lower())
    if not safe_token:
        return None
    return os.path.join(_pdf_import_dir(), f"{safe_token}.json")


def _clear_pdf_import(project_id):
    entry = session.pop(_pdf_import_session_key(project_id), None)
    token = entry.get("token") if isinstance(entry, dict) else None
    path = _pdf_import_path(token)
    if path and os.path.isfile(path):
        os.unlink(path)


def _store_pdf_import(project_id, payload):
    _clear_pdf_import(project_id)
    token = uuid.uuid4().hex
    path = _pdf_import_path(token)
    with open(path, "w", encoding="utf-8") as handle:
        _json.dump(payload, handle, ensure_ascii=False)
    session[_pdf_import_session_key(project_id)] = {"token": token}


def _load_pdf_import(project_id):
    entry = session.get(_pdf_import_session_key(project_id))
    if not entry:
        return None
    if isinstance(entry, dict) and "items" in entry:
        return entry
    token = entry.get("token") if isinstance(entry, dict) else None
    path = _pdf_import_path(token)
    if not path or not os.path.isfile(path):
        _clear_pdf_import(project_id)
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return _json.load(handle)


def _redirect_closed_pdf_import(project_id):
    flash("El proyecto está cerrado. Reábrelo para importar una LDM.", "warning")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")


@bp.route("/projects/<project_id>/ldm/import-pdf", methods=["POST"], endpoint="import_ldm_pdf_upload")
def import_ldm_pdf_upload(project_id):
    """Recibe el PDF, extrae ítems y redirige a la vista de mapeo."""
    project = _find_project(project_id)
    if not project:
        return redirect(url_for("dashboard"))
    if project.get("closed_at"):
        return _redirect_closed_pdf_import(project_id)

    pdf_file = request.files.get("pdf_file")
    if not pdf_file or not pdf_file.filename:
        flash("Selecciona un archivo PDF.", "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    if not pdf_file.filename.lower().endswith(".pdf"):
        flash("El archivo debe ser un PDF.", "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    # Guardar temporalmente para que pdfplumber pueda leerlo
    with _tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_file.save(tmp.name)
        tmp_path = tmp.name

    try:
        result = extract_items_from_pdf(tmp_path)
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    if result.get("error"):
        flash(f"Error al leer el PDF: {result['error']}", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    if not result["items"]:
        flash(
            f"No se encontraron ítems en el PDF ({result['page_count']} página(s)). "
            "Verifica que sea una lista de materiales con tabla o texto estructurado.",
            "warning",
        )
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    _store_pdf_import(project_id, {
        "items": result["items"],
        "method": result["method"],
        "page_count": result["page_count"],
        "filename": pdf_file.filename,
        "meta": result.get("meta", {}),
    })

    flash(
        f"{len(result['items'])} ítem(s) detectado(s) con método '{result['method']}'. "
        "Revisa y asigna cada uno a un artículo del catálogo.",
        "info",
    )
    return redirect(url_for("materials_bp.import_ldm_pdf_map", project_id=project_id))


@bp.route("/projects/<project_id>/ldm/import-pdf/map", methods=["GET"], endpoint="import_ldm_pdf_map")
def import_ldm_pdf_map(project_id):
    """Muestra la vista de mapeo ítem-PDF → catálogo."""
    project = _find_project(project_id)
    if not project:
        return redirect(url_for("dashboard"))
    if project.get("closed_at"):
        _clear_pdf_import(project_id)
        return _redirect_closed_pdf_import(project_id)

    session_data = _load_pdf_import(project_id)
    if not session_data:
        flash("Sesión de importación expirada. Sube el PDF de nuevo.", "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    catalog_by_id, catalog_by_name = catalog_maps()
    catalog_list = sorted(load("catalogo"), key=lambda c: c.get("nombre", "").lower())

    return render_template(
        "ldm_pdf_import.html",
        project=project,
        session_data=session_data,
        catalog_list=catalog_list,
        proveedores=load("proveedores"),
        today=today(),
    )


@bp.route("/projects/<project_id>/ldm/import-pdf/create", methods=["POST"], endpoint="import_ldm_pdf_create")
def import_ldm_pdf_create(project_id):
    """Recibe el mapeo del usuario y crea la LDM."""
    project = _find_project(project_id)
    if not project:
        return redirect(url_for("dashboard"))
    if project.get("closed_at"):
        _clear_pdf_import(project_id)
        return _redirect_closed_pdf_import(project_id)

    session_data = _load_pdf_import(project_id)
    if not session_data:
        flash("Sesión de importación expirada. Sube el PDF de nuevo.", "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-materiales")

    form = request.form
    proveedor = form.get("proveedor", "").strip()
    cot_proveedor = form.get("cot_proveedor", "").strip()
    fecha = form.get("fecha", "").strip() or today()
    notes = form.get("notes", "").strip()

    if not proveedor:
        flash("Indica el nombre del proveedor.", "warning")
        return redirect(url_for("materials_bp.import_ldm_pdf_map", project_id=project_id))

    catalog_by_id, _ = catalog_maps()
    raw_items = session_data["items"]
    built_items = []

    for i, raw in enumerate(raw_items):
        catalog_item_id = form.get(f"catalog_id_{i}", "").strip()
        if catalog_item_id == "__ignore__" or not catalog_item_id:
            continue

        # Si es un ID nuevo que el usuario quiere agregar al catálogo
        if catalog_item_id == "__new__":
            new_nombre = form.get(f"new_nombre_{i}", "").strip()
            new_unidad = form.get(f"new_unidad_{i}", "pza").strip() or "pza"
            if not new_nombre:
                continue
            new_cat_item = {
                "id": new_id(),
                "nombre": new_nombre,
                "descripcion": "",
                "unidad": new_unidad,
                "precio": 0.0,
                "created_at": today(),
                "categoria": "",
            }
            catalogo = load("catalogo")
            catalogo.append(new_cat_item)
            save("catalogo", catalogo)
            catalog_item_id = new_cat_item["id"]
            catalog_by_id[catalog_item_id] = new_cat_item

        cat = catalog_by_id.get(catalog_item_id)
        description = cat["nombre"] if cat else raw.get("description", "")

        qty_raw = form.get(f"qty_{i}", str(raw.get("qty", 1.0)))
        unit_raw = form.get(f"unit_{i}", raw.get("unit", "pza"))
        price_raw = form.get(f"precio_{i}", str(raw.get("precio_unit", 0.0)))

        try:
            qty = float(qty_raw.replace(",", ".")) if qty_raw else raw.get("qty", 1.0)
        except ValueError:
            qty = raw.get("qty", 1.0)
        try:
            price = float(price_raw.replace(",", ".")) if price_raw else raw.get("precio_unit", 0.0)
        except ValueError:
            price = raw.get("precio_unit", 0.0)
        unit = unit_raw or cat.get("unidad", "pza") if cat else unit_raw or "pza"
        total = round(qty * price, 2)

        built_items.append({
            "catalog_item_id": catalog_item_id,
            "description": description,
            "unit": unit,
            "qty": qty,
            "precio_cot": price,
            "total_cot": total,
        })

    if not built_items:
        flash("No se seleccionó ningún artículo del catálogo. Asigna al menos uno.", "warning")
        return redirect(url_for("materials_bp.import_ldm_pdf_map", project_id=project_id))

    subtotal = round(sum(it["total_cot"] for it in built_items), 2)
    all_ldms = load("materiales")
    seq = len([m for m in all_ldms if m["project_id"] == project_id]) + 1
    ldm = {
        "id": new_id(),
        "project_id": project_id,
        "ldm_number": f"LDM-{project['clave']}-{seq:02d}",
        "seq": seq,
        "proveedor": proveedor,
        "fecha": fecha,
        "items": built_items,
        "subtotal_cot": subtotal,
        "cot_proveedor": cot_proveedor,
        "notes": notes,
        "created_at": today(),
    }
    all_ldms.append(ldm)
    save("materiales", all_ldms)

    _clear_pdf_import(project_id)

    flash(
        f"LDM {ldm['ldm_number']} creada con {len(built_items)} artículo(s) desde PDF. "
        "Revisa y ajusta si es necesario.",
        "success",
    )
    return redirect(url_for("materials_bp.edit_ldm", project_id=project_id, ldm_id=ldm["id"]))
