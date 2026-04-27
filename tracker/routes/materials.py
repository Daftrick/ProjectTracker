import os
from datetime import date, datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..catalog import catalog_maps, catalog_name_key, hydrate_ldm, hydrate_ldm_item
from ..csv_import import parse_ldm_csv
from ..drive import folder_name, load_config, parse_csv_plano_filename
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
    root = cfg.get("drive_projects_path", "")
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
            return redirect(url_for("materials_bp.new_ldm", project_id=project_id))
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
    return render_template("ldm_form.html", project=project, ldm=None, proveedores=load("proveedores"), today=today())


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

    parsed = parse_ldm_csv(csv_path)
    if parsed["errors"]:
        for error in parsed["errors"]:
            flash(error, "warning")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-documentos")

    if request.method == "POST":
        validation = validate_ldm_form(request.form)
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return redirect(url_for("materials_bp.import_ldm_csv", project_id=project_id, filename=clean_name))
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
    return render_template(
        "ldm_form.html",
        project=project,
        ldm=preview,
        proveedores=load("proveedores"),
        today=today(),
    )


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
            return redirect(url_for("materials_bp.edit_ldm", project_id=project_id, ldm_id=ldm_id))
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
    return render_template("ldm_form.html", project=project, ldm=hydrated, proveedores=load("proveedores"), today=today())


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


@bp.route("/projects/<project_id>/ldm/<ldm_id>/delete", methods=["POST"], endpoint="delete_ldm")
def delete_ldm(project_id, ldm_id):
    save("materiales", [item for item in load("materiales") if item["id"] != ldm_id])
    flash("Lista eliminada.", "warning")
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
    root = cfg.get("drive_projects_path", "")
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
