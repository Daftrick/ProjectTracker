import json
import os

import csv as _csv
import io
import zipfile

from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import current_user, logout_user

from ..auth import admin_required, AUTH_DB, init_db

from ..bundles import (
    activate_bundle_version,
    add_bundle_version,
    create_bundle,
    delete_bundle_version,
    get_active_bundle_version,
    normalize_bundle,
)
from ..admin_filters import filter_fichas, filter_proveedores, list_field_values
from ..catalog_search import filter_catalog, list_categories
from ..deletions import delete_catalog_items_data
from ..domain import TIPOS_FICHA
from ..storage import DATA_DIR, FILES, load, new_id, save, today
from ..utils import clean as _clean, parse_float as _parse_float

# Tope de resultados para autocompletado inline en COT y LDM. Se mantiene
# moderado para no devolver listas larguísimas; si se queda corto se puede
# subir aquí sin tocar la lógica de filtrado.
API_CATALOG_LIMIT = 50

DISCIPLINAS = ["instalaciones", "arquitectura", "estructura", "otros"]

bp = Blueprint("admin_bp", __name__)


def _require_admin_post(redirect_endpoint):
    """Returns a redirect Response if the current POST is not from an admin, else None."""
    if current_app.config.get("LOGIN_DISABLED"):
        return None
    if not current_user.is_authenticated or current_user.role != "admin":
        flash("Acceso restringido a administradores.", "danger")
        return redirect(url_for(redirect_endpoint))
    return None


def _parse_price(value):
    raw = _clean(value) or "0"
    try:
        price = float(raw.replace(",", "."))
    except ValueError:
        return None
    return price if price >= 0 else None


def _catalog_form(form=None):
    form = form or {}
    buy_size_raw = _clean(form.get("buy_unit_size"))
    return {
        "nombre": _clean(form.get("nombre")),
        "descripcion": _clean(form.get("descripcion")),
        "unidad": _clean(form.get("unidad")) or "pza",
        "precio": _clean(form.get("precio")) or "0",
        "categoria": _clean(form.get("categoria")),
        "disciplina": _clean(form.get("disciplina")) or "instalaciones",
        "marca": _clean(form.get("marca")),
        "is_fractional": form.get("is_fractional") == "1",
        "buy_unit_size": float(buy_size_raw) if buy_size_raw else None,
        "buy_unit_label": _clean(form.get("buy_unit_label")),
    }


def _proveedor_form(form=None):
    form = form or {}
    return {
        "nombre": _clean(form.get("nombre")),
        "contacto": _clean(form.get("contacto")),
        "email": _clean(form.get("email")),
        "telefono": _clean(form.get("telefono")),
        "categoria": _clean(form.get("categoria")),
        "notas": _clean(form.get("notas")),
    }


def _ficha_form(form=None):
    form = form or {}
    return {
        "tipo": (_clean(form.get("tipo")) or TIPOS_FICHA[0]).upper(),
        "marca": _clean(form.get("marca")),
        "modelo": _clean(form.get("modelo")),
        "descripcion": _clean(form.get("descripcion")),
        "filename": _clean(form.get("filename")),
        "notes": _clean(form.get("notes")),
    }


def _team_form(form=None):
    form = form or {}
    return {
        "name": _clean(form.get("name")),
        "role": _clean(form.get("role")),
        "email": _clean(form.get("email")),
        "phone": _clean(form.get("phone")),
        "notes": _clean(form.get("notes")),
    }


def _render_catalogo(items=None, q="", categoria="", disciplina_filter="", form_state=None, field_errors=None, open_modal=None):
    full_catalog = items if items is not None else load("catalogo")
    categorias = list_categories(full_catalog)
    visible = filter_catalog(full_catalog, q=q, categoria=categoria)
    if disciplina_filter:
        visible = [i for i in visible if (i.get("disciplina") or "instalaciones") == disciplina_filter]
    return render_template(
        "catalogo.html",
        items=visible,
        q=q or "",
        categoria=categoria or "",
        disciplina_filter=disciplina_filter or "",
        categorias=categorias,
        total_count=len(full_catalog),
        form_state=form_state or _catalog_form(),
        field_errors=field_errors or {},
        open_modal=open_modal,
    )


def _render_proveedores(proveedores_data=None, q="", categoria="", form_state=None, field_errors=None, open_modal=None):
    full_proveedores = proveedores_data if proveedores_data is not None else load("proveedores")
    visible = filter_proveedores(full_proveedores, q=q, categoria=categoria)
    return render_template(
        "proveedores.html",
        proveedores=visible,
        q=q or "",
        categoria=categoria or "",
        categorias=list_field_values(full_proveedores, "categoria"),
        total_count=len(full_proveedores),
        form_state=form_state or _proveedor_form(),
        field_errors=field_errors or {},
        open_modal=open_modal,
    )


def _render_fichas(form_state=None, field_errors=None, open_modal=None, filter_tipo="", q="", filter_vinculo=""):
    full_fichas = load("fichas")
    fichas_data = filter_fichas(full_fichas, q=q, tipo=filter_tipo, vinculo=filter_vinculo)
    projects_by_id = {project["id"]: project for project in load("projects")}
    return render_template(
        "fichas.html",
        fichas=fichas_data,
        total_count=len(full_fichas),
        q=q or "",
        filter_tipo=filter_tipo,
        filter_vinculo=filter_vinculo,
        projects_by_id=projects_by_id,
        tipos_ficha=TIPOS_FICHA,
        form_state=form_state or _ficha_form(),
        field_errors=field_errors or {},
        open_modal=open_modal,
    )


def _render_team(form_state=None, field_errors=None, open_modal=None):
    return render_template(
        "team.html",
        team=load("team"),
        form_state=form_state or _team_form(),
        field_errors=field_errors or {},
        open_modal=open_modal,
    )


@bp.route("/catalogo", methods=["GET", "POST"], endpoint="catalogo")
def catalogo():
    if request.method == "POST":
        guard = _require_admin_post("catalogo")
        if guard:
            return guard
        form_state = _catalog_form(request.form)
        field_errors = {}
        if not form_state["nombre"]:
            field_errors["nombre"] = "El nombre es requerido."
        price = _parse_price(form_state["precio"])
        if price is None:
            field_errors["precio"] = "Precio debe ser un número mayor o igual a 0."
        if field_errors:
            for error in field_errors.values():
                flash(error, "warning")
            return _render_catalogo(form_state=form_state, field_errors=field_errors, open_modal="modalNew")
        items = load("catalogo")
        items.append({
            "id": new_id(),
            "nombre": form_state["nombre"],
            "descripcion": form_state["descripcion"],
            "unidad": form_state["unidad"],
            "precio": price,
            "categoria": form_state["categoria"],
            "disciplina": form_state["disciplina"],
            "marca": form_state["marca"],
            "is_fractional": form_state["is_fractional"],
            "buy_unit_size": form_state["buy_unit_size"],
            "buy_unit_label": form_state["buy_unit_label"],
            "created_at": today(),
        })
        save("catalogo", items)
        flash(f"Artículo '{form_state['nombre']}' agregado al catálogo.", "success")
        return redirect(url_for("catalogo"))
    return _render_catalogo(
        q=request.args.get("q", ""),
        categoria=request.args.get("categoria", ""),
        disciplina_filter=request.args.get("disciplina", ""),
    )


@bp.route("/catalogo/<item_id>/edit", methods=["POST"], endpoint="edit_catalogo")
@admin_required
def edit_catalogo(item_id):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    items = load("catalogo")
    item = next((entry for entry in items if entry["id"] == item_id), None)
    if item:
        form_state = _catalog_form(request.form)
        price = _parse_price(form_state["precio"])
        if not form_state["nombre"] or price is None:
            if is_ajax:
                return jsonify({"ok": False, "error": "Datos inválidos"}), 400
            flash("Datos inválidos.", "warning")
            return redirect(url_for("catalogo"))
        item["nombre"] = form_state["nombre"]
        item["descripcion"] = form_state["descripcion"]
        item["unidad"] = form_state["unidad"]
        item["precio"] = price
        item["categoria"] = form_state["categoria"]
        item["disciplina"] = form_state["disciplina"]
        item["marca"] = form_state["marca"]
        item["is_fractional"] = form_state["is_fractional"]
        item["buy_unit_size"] = form_state["buy_unit_size"]
        item["buy_unit_label"] = form_state["buy_unit_label"]
        save("catalogo", items)
        if is_ajax:
            return jsonify({"ok": True, "item": item})
        flash("Artículo actualizado.", "success")
    elif is_ajax:
        return jsonify({"ok": False}), 404
    return redirect(url_for("catalogo"))


@bp.route("/catalogo/<item_id>/delete", methods=["POST"], endpoint="delete_catalogo")
@admin_required
def delete_catalogo(item_id):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    result = delete_catalog_items_data({item_id}, load("catalogo"), load("quotes"), load("materiales"))
    save("catalogo", result["catalogo"])
    save("quotes", result["quotes"])
    save("materiales", result["materiales"])
    if is_ajax:
        return jsonify({"ok": True, "counts": result["counts"]})
    refs = result["counts"]["quote_refs"] + result["counts"]["material_refs"]
    flash(f"Artículo eliminado. Se limpiaron {refs} referencia(s) en cotizaciones/LDMs.", "warning")
    return redirect(url_for("catalogo"))


@bp.route("/api/catalogo/migrate-marca", methods=["POST"], endpoint="migrate_catalog_marca")
@admin_required
def migrate_catalog_marca():
    """One-time migration: split 'Marca | Nombre' items into separate marca + nombre fields."""
    items = load("catalogo")
    migrated = 0
    for item in items:
        nombre = item.get("nombre", "")
        if "|" in nombre and not item.get("marca"):
            parts = nombre.split("|", 1)
            item["marca"] = parts[0].strip()
            item["nombre"] = parts[1].strip()
            migrated += 1
    if migrated:
        save("catalogo", items)
    return jsonify({"ok": True, "migrated": migrated})


@bp.route("/api/catalogo/bulk-edit", methods=["POST"], endpoint="bulk_edit_catalogo")
@admin_required
def bulk_edit_catalogo():
    data = request.get_json(force=True) or {}
    ids = set(str(i) for i in (data.get("ids") or []))
    fields = {k: str(v).strip() for k, v in (data.get("fields") or {}).items()}
    allowed = {"marca", "descripcion", "categoria", "unidad"}
    to_apply = {k: v for k, v in fields.items() if k in allowed and v}
    if not ids or not to_apply:
        return jsonify(ok=False, error="Nada que aplicar")
    items = load("catalogo")
    updated = 0
    for item in items:
        if str(item.get("id", "")) in ids:
            for k, v in to_apply.items():
                item[k] = v
            updated += 1
    if updated:
        save("catalogo", items)
    return jsonify(ok=True, updated=updated)


@bp.route("/api/catalogo/bulk-delete", methods=["POST"], endpoint="bulk_delete_catalogo")
@admin_required
def bulk_delete_catalogo():
    ids = set((request.get_json(force=True) or {}).get("ids", []))
    result = delete_catalog_items_data(ids, load("catalogo"), load("quotes"), load("materiales"))
    save("catalogo", result["catalogo"])
    save("quotes", result["quotes"])
    save("materiales", result["materiales"])
    return jsonify({
        "ok": True,
        "deleted": result["counts"]["catalogo"],
        "refs_cleared": result["counts"]["quote_refs"] + result["counts"]["material_refs"],
    })


@bp.route("/api/catalogo/<item_id>/impact", methods=["GET"], endpoint="api_catalogo_impact")
def api_catalogo_impact(item_id):
    item_id = str(item_id).strip()
    quotes = load("quotes")
    materiales = load("materiales")
    quote_refs = sum(
        1
        for q in quotes
        for it in q.get("items", [])
        if str(it.get("catalog_item_id", "")).strip() == item_id
    )
    material_refs = sum(
        1
        for m in materiales
        for it in m.get("items", [])
        if str(it.get("catalog_item_id", "")).strip() == item_id
    )
    return jsonify({"quote_refs": quote_refs, "material_refs": material_refs})


@bp.route("/api/catalogo", endpoint="api_catalogo")
def api_catalogo():
    query = request.args.get("q", "")
    categoria = request.args.get("categoria", "")
    items = filter_catalog(load("catalogo"), q=query, categoria=categoria)
    return jsonify(items[:API_CATALOG_LIMIT])


@bp.route("/api/catalogo/categorias", endpoint="api_catalogo_categorias")
def api_catalogo_categorias():
    """Lista única de categorías existentes (para datalists/filtros)."""
    return jsonify(list_categories(load("catalogo")))


@bp.route("/api/catalogo/add", methods=["POST"], endpoint="api_catalogo_add")
@admin_required
def api_catalogo_add():
    data = request.get_json(force=True) or {}
    nombre = (data.get("nombre", "") or "").strip()
    if not nombre:
        return jsonify({"error": "Nombre requerido"}), 400
    items = load("catalogo")
    new_item = {
        "id": new_id(),
        "nombre": nombre,
        "descripcion": (data.get("descripcion", "") or "").strip(),
        "unidad": ((data.get("unidad", "") or "pza")).strip(),
        "precio": float(data.get("precio", 0) or 0),
        "categoria": (data.get("categoria", "") or "").strip(),
        "disciplina": (data.get("disciplina", "") or "instalaciones").strip(),
        "marca": (data.get("marca", "") or "").strip(),
        "is_fractional": False,
        "buy_unit_size": None,
        "buy_unit_label": "",
        "created_at": today(),
    }
    items.append(new_item)
    save("catalogo", items)
    return jsonify(new_item), 201


# ─────────────────────────────────────────────────────────────
# Bundles versionados para expansion directa COT -> LDM
# ─────────────────────────────────────────────────────────────

def _catalog_by_id():
    return {str(item.get("id", "")).strip(): item for item in load("catalogo")}


def _catalog_sorted_by_name():
    return sorted(
        load("catalogo"),
        key=lambda item: str(item.get("nombre", "")).casefold(),
    )


def _parse_components(form):
    ids = form.getlist("component_catalog_item_id[]")
    qtys = form.getlist("component_qty[]")
    wastes = form.getlist("component_waste_pct[]")
    notes = form.getlist("component_notes[]")
    components = []
    max_len = max(len(ids), len(qtys), len(wastes), len(notes), 0)
    for index in range(max_len):
        catalog_item_id = _clean(ids[index] if index < len(ids) else "")
        qty = _parse_float(qtys[index] if index < len(qtys) else "0")
        if not catalog_item_id and qty <= 0:
            continue
        components.append({
            "catalog_item_id": catalog_item_id,
            "qty": qty,
            "waste_pct": _parse_float(wastes[index] if index < len(wastes) else "0"),
            "notes": _clean(notes[index] if index < len(notes) else ""),
        })
    return components


def _find_bundle(bundles, bundle_id):
    return next((bundle for bundle in bundles if bundle.get("id") == bundle_id), None)


def _find_version(bundle, version_number):
    target = int(version_number)
    return next((version for version in (bundle or {}).get("versions", []) if int(version.get("version", 0)) == target), None)


def _render_bundles(open_bundle_id=""):
    catalog = _catalog_sorted_by_name()
    catalog_by_id = {item["id"]: item for item in catalog if item.get("id")}
    bundles = [normalize_bundle(bundle) for bundle in load("bundles")]
    bundle_item_ids = {bundle.get("catalog_item_id") for bundle in bundles}
    return render_template(
        "bundles.html",
        bundles=bundles,
        catalog=catalog,
        catalog_by_id=catalog_by_id,
        bundle_item_ids=bundle_item_ids,
        open_bundle_id=open_bundle_id,
        get_active_bundle_version=get_active_bundle_version,
    )


@bp.route("/bundles", methods=["GET", "POST"], endpoint="bundles")
def bundles():
    if request.method == "POST":
        guard = _require_admin_post("bundles")
        if guard:
            return guard
        catalog_item_id = _clean(request.form.get("catalog_item_id"))
        catalog_by_id = _catalog_by_id()
        item = catalog_by_id.get(catalog_item_id)
        if not item:
            flash("Selecciona un artículo válido del catálogo para crear el bundle.", "warning")
            return _render_bundles()
        existing = next((bundle for bundle in load("bundles") if bundle.get("catalog_item_id") == catalog_item_id), None)
        if existing:
            flash("Ese artículo ya tiene un bundle asociado.", "warning")
            return redirect(url_for("bundles") + f"#bundle-{existing.get('id')}")
        components = _parse_components(request.form)
        bundle = create_bundle(
            catalog_item_id,
            request.form.get("name") or item.get("nombre") or catalog_item_id,
            components,
            bundle_id=new_id(),
        )
        bundle["created_at"] = today()
        bundle["updated_at"] = today()
        items = load("bundles")
        items.append(bundle)
        save("bundles", items)
        flash("Bundle creado.", "success")
        return redirect(url_for("bundles") + f"#bundle-{bundle['id']}")
    return _render_bundles()


@bp.route("/bundles/<bundle_id>/update", methods=["POST"], endpoint="update_bundle")
@admin_required
def update_bundle(bundle_id):
    items = load("bundles")
    bundle = _find_bundle(items, bundle_id)
    if not bundle:
        flash("Bundle no encontrado.", "danger")
        return redirect(url_for("bundles"))
    catalog_item_id = _clean(request.form.get("catalog_item_id")) or bundle.get("catalog_item_id")
    catalog_by_id = _catalog_by_id()
    if catalog_item_id not in catalog_by_id:
        flash("Selecciona un artículo de catálogo válido.", "warning")
        return redirect(url_for("bundles") + f"#bundle-{bundle_id}")
    duplicate = next((b for b in items if b.get("id") != bundle_id and b.get("catalog_item_id") == catalog_item_id), None)
    if duplicate:
        flash("Otro bundle ya usa ese artículo de catálogo.", "warning")
        return redirect(url_for("bundles") + f"#bundle-{bundle_id}")
    bundle["catalog_item_id"] = catalog_item_id
    bundle["name"] = _clean(request.form.get("name")) or catalog_by_id[catalog_item_id].get("nombre") or catalog_item_id
    bundle["updated_at"] = today()
    save("bundles", items)
    flash("Bundle actualizado.", "success")
    return redirect(url_for("bundles") + f"#bundle-{bundle_id}")


@bp.route("/bundles/<bundle_id>/delete", methods=["POST"], endpoint="delete_bundle")
@admin_required
def delete_bundle(bundle_id):
    before = load("bundles")
    after = [bundle for bundle in before if bundle.get("id") != bundle_id]
    save("bundles", after)
    flash("Bundle eliminado.", "warning")
    return redirect(url_for("bundles"))


@bp.route("/bundles/<bundle_id>/versions/<int:version_number>/update", methods=["POST"], endpoint="update_bundle_version")
@admin_required
def update_bundle_version(bundle_id, version_number):
    items = load("bundles")
    bundle = _find_bundle(items, bundle_id)
    if not bundle:
        flash("Bundle no encontrado.", "danger")
        return redirect(url_for("bundles"))
    current = normalize_bundle(bundle)
    version = _find_version(current, version_number)
    if not version:
        flash("Versión no encontrada.", "danger")
        return redirect(url_for("bundles") + f"#bundle-{bundle_id}")
    version["label"] = _clean(request.form.get("label")) or f"Versión {version_number}"
    version["notes"] = _clean(request.form.get("notes"))
    version["components"] = _parse_components(request.form)
    current["updated_at"] = today()
    items[items.index(bundle)] = current
    save("bundles", items)
    flash("Versión de bundle actualizada.", "success")
    return redirect(url_for("bundles") + f"#bundle-{bundle_id}")


@bp.route("/bundles/<bundle_id>/versions/add", methods=["POST"], endpoint="add_bundle_version_route")
@admin_required
def add_bundle_version_route(bundle_id):
    items = load("bundles")
    bundle = _find_bundle(items, bundle_id)
    if not bundle:
        flash("Bundle no encontrado.", "danger")
        return redirect(url_for("bundles"))
    source_version_number = int(_parse_float(request.form.get("source_version"), 0))
    source = _find_version(normalize_bundle(bundle), source_version_number) if source_version_number else get_active_bundle_version(bundle)
    components = [dict(component) for component in (source or {}).get("components", [])]
    make_active = bool(request.form.get("make_active"))
    updated = add_bundle_version(
        bundle,
        components=components,
        label=_clean(request.form.get("label")),
        notes=_clean(request.form.get("notes")),
        make_active=make_active,
    )
    updated["updated_at"] = today()
    items[items.index(bundle)] = updated
    save("bundles", items)
    flash("Nueva versión creada.", "success")
    return redirect(url_for("bundles") + f"#bundle-{bundle_id}")


@bp.route("/bundles/<bundle_id>/versions/<int:version_number>/activate", methods=["POST"], endpoint="activate_bundle_version_route")
@admin_required
def activate_bundle_version_route(bundle_id, version_number):
    items = load("bundles")
    bundle = _find_bundle(items, bundle_id)
    if bundle:
        try:
            updated = activate_bundle_version(bundle, version_number)
            updated["updated_at"] = today()
            items[items.index(bundle)] = updated
            save("bundles", items)
            flash("Versión activada.", "success")
        except ValueError as exc:
            flash(str(exc), "warning")
    return redirect(url_for("bundles") + f"#bundle-{bundle_id}")


@bp.route("/bundles/<bundle_id>/versions/<int:version_number>/delete", methods=["POST"], endpoint="delete_bundle_version_route")
@admin_required
def delete_bundle_version_route(bundle_id, version_number):
    items = load("bundles")
    bundle = _find_bundle(items, bundle_id)
    if bundle:
        try:
            updated = delete_bundle_version(bundle, version_number)
            updated["updated_at"] = today()
            items[items.index(bundle)] = updated
            save("bundles", items)
            flash("Versión eliminada.", "warning")
        except ValueError as exc:
            flash(str(exc), "warning")
    return redirect(url_for("bundles") + f"#bundle-{bundle_id}")


@bp.route("/proveedores", methods=["GET", "POST"], endpoint="proveedores")
def proveedores():
    if request.method == "POST":
        guard = _require_admin_post("proveedores")
        if guard:
            return guard
        form_state = _proveedor_form(request.form)
        field_errors = {}
        if not form_state["nombre"]:
            field_errors["nombre"] = "El nombre es requerido."
        if field_errors:
            for error in field_errors.values():
                flash(error, "warning")
            return _render_proveedores(form_state=form_state, field_errors=field_errors, open_modal="modalNew")
        proveedores_data = load("proveedores")
        proveedores_data.append({
            "id": new_id(),
            "nombre": form_state["nombre"],
            "contacto": form_state["contacto"],
            "email": form_state["email"],
            "telefono": form_state["telefono"],
            "categoria": form_state["categoria"],
            "notas": form_state["notas"],
            "created_at": today(),
        })
        save("proveedores", proveedores_data)
        flash(f"Proveedor '{form_state['nombre']}' registrado.", "success")
        return redirect(url_for("proveedores"))
    return _render_proveedores(
        q=request.args.get("q", ""),
        categoria=request.args.get("categoria", ""),
    )


@bp.route("/proveedores/<prov_id>/edit", methods=["POST"], endpoint="edit_proveedor")
@admin_required
def edit_proveedor(prov_id):
    proveedores_data = load("proveedores")
    proveedor = next((item for item in proveedores_data if item["id"] == prov_id), None)
    if proveedor:
        form_state = _proveedor_form(request.form)
        if not form_state["nombre"]:
            flash("El nombre es requerido.", "warning")
            return redirect(url_for("proveedores"))
        proveedor["nombre"] = form_state["nombre"]
        proveedor["contacto"] = form_state["contacto"]
        proveedor["email"] = form_state["email"]
        proveedor["telefono"] = form_state["telefono"]
        proveedor["categoria"] = form_state["categoria"]
        proveedor["notas"] = form_state["notas"]
        save("proveedores", proveedores_data)
        flash("Proveedor actualizado.", "success")
    return redirect(url_for("proveedores"))


@bp.route("/proveedores/<prov_id>/delete", methods=["POST"], endpoint="delete_proveedor")
@admin_required
def delete_proveedor(prov_id):
    save("proveedores", [item for item in load("proveedores") if item["id"] != prov_id])
    flash("Proveedor eliminado.", "warning")
    return redirect(url_for("proveedores"))


@bp.route("/fichas", methods=["GET", "POST"], endpoint="fichas")
def fichas():
    if request.method == "POST":
        guard = _require_admin_post("fichas")
        if guard:
            return guard
        form_state = _ficha_form(request.form)
        field_errors = {}
        if form_state["tipo"] not in TIPOS_FICHA:
            field_errors["tipo"] = "Tipo de ficha no reconocido."
        if not form_state["marca"]:
            field_errors["marca"] = "Marca es requerida."
        if not form_state["modelo"]:
            field_errors["modelo"] = "Modelo es requerido."
        if field_errors:
            for error in field_errors.values():
                flash(error, "warning")
            return _render_fichas(form_state=form_state, field_errors=field_errors, open_modal="modalFicha")
        tipo = form_state["tipo"]
        marca = form_state["marca"].upper().replace(" ", "-")
        modelo = form_state["modelo"].upper().replace(" ", "-")
        fichas_data = load("fichas")
        fichas_data.append({
            "id": new_id(),
            "code": f"{tipo}-{marca}-{modelo}",
            "tipo": tipo,
            "marca": marca,
            "modelo": modelo,
            "descripcion": form_state["descripcion"],
            "filename": form_state["filename"],
            "projects": [],
            "notes": form_state["notes"],
            "created_at": today(),
        })
        save("fichas", fichas_data)
        flash(f"Ficha {tipo}-{marca}-{modelo} registrada.", "success")
        return redirect(url_for("fichas"))
    filter_tipo = request.args.get("tipo", "")
    return _render_fichas(
        filter_tipo=filter_tipo,
        q=request.args.get("q", ""),
        filter_vinculo=request.args.get("vinculo", ""),
    )


@bp.route("/fichas/<ficha_id>/link/<project_id>", methods=["POST"], endpoint="link_ficha")
def link_ficha(ficha_id, project_id):
    fichas_data = load("fichas")
    ficha = next((item for item in fichas_data if item["id"] == ficha_id), None)
    if ficha and project_id not in ficha.get("projects", []):
        ficha.setdefault("projects", []).append(project_id)
        save("fichas", fichas_data)
        flash("Ficha vinculada.", "success")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-fichas")


@bp.route("/fichas/<ficha_id>/unlink/<project_id>", methods=["POST"], endpoint="unlink_ficha")
def unlink_ficha(ficha_id, project_id):
    fichas_data = load("fichas")
    ficha = next((item for item in fichas_data if item["id"] == ficha_id), None)
    if ficha and project_id in ficha.get("projects", []):
        ficha["projects"].remove(project_id)
        save("fichas", fichas_data)
        flash("Ficha desvinculada.", "info")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-fichas")


@bp.route("/fichas/<ficha_id>/delete", methods=["POST"], endpoint="delete_ficha")
@admin_required
def delete_ficha(ficha_id):
    save("fichas", [item for item in load("fichas") if item["id"] != ficha_id])
    flash("Ficha eliminada.", "warning")
    return redirect(url_for("fichas"))


@bp.route("/team", methods=["GET", "POST"], endpoint="team")
def team():
    if request.method == "POST":
        guard = _require_admin_post("team")
        if guard:
            return guard
        form_state = _team_form(request.form)
        field_errors = {}
        if not form_state["name"]:
            field_errors["name"] = "El nombre es requerido."
        if field_errors:
            for error in field_errors.values():
                flash(error, "warning")
            return _render_team(form_state=form_state, field_errors=field_errors, open_modal="modalMember")
        team_data = load("team")
        team_data.append({
            "id": new_id(),
            "name": form_state["name"],
            "role": form_state["role"],
            "email": form_state["email"],
            "phone": form_state["phone"],
            "notes": form_state["notes"],
            "created_at": today(),
        })
        save("team", team_data)
        flash("Miembro agregado.", "success")
        return redirect(url_for("team"))
    return _render_team()


@bp.route("/team/<member_id>/delete", methods=["POST"], endpoint="delete_member")
@admin_required
def delete_member(member_id):
    save("team", [item for item in load("team") if item["id"] != member_id])
    flash("Miembro eliminado.", "warning")
    return redirect(url_for("team"))


# ─────────────────────────────────────────────────────────────
# Empresa — perfil de empresa y logo
# ─────────────────────────────────────────────────────────────

import os as _os

from werkzeug.utils import secure_filename as _secure_filename

_ALLOWED_LOGO_EXT = {"png", "jpg", "jpeg"}
_LOGO_MAX_BYTES = 2 * 1024 * 1024  # 2 MB


def _logo_ext_from_filename(filename):
    safe_filename = _secure_filename(filename or "")
    ext = safe_filename.rsplit(".", 1)[-1].lower() if "." in safe_filename else ""
    return "jpg" if ext == "jpeg" else ext


def _detect_logo_ext(content):
    if content.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if content.startswith(b"\xff\xd8\xff"):
        return "jpg"
    return ""


def _logo_upload_dir():
    return _os.path.join(DATA_DIR, "uploads")


def _company_logo_version(company):
    logo_rel = (company or {}).get("logo") or ""
    if not logo_rel:
        return ""
    logo_path = _os.path.join(DATA_DIR, "uploads", _os.path.basename(logo_rel))
    try:
        return str(int(_os.path.getmtime(logo_path)))
    except OSError:
        return ""


@bp.route("/empresa/logo-file", endpoint="empresa_logo_file")
def empresa_logo_file():
    from flask import send_from_directory, abort
    from ..company_config import get_company
    company = get_company()
    logo_rel = company.get("logo") or ""
    if not logo_rel:
        abort(404)
    filename = _os.path.basename(logo_rel)
    uploads_dir = _os.path.join(DATA_DIR, "uploads")
    return send_from_directory(uploads_dir, filename)


@bp.route("/empresa", methods=["GET", "POST"], endpoint="empresa")
@admin_required
def empresa():
    from ..company_config import get_company, save_company
    errors = {}
    if request.method == "POST":
        current = get_company()
        portada_color = (request.form.get("portada_color", "") or "").strip()
        if not portada_color.startswith("#") or len(portada_color) != 7:
            portada_color = current.get("portada_color", "#000000") or "#000000"
        data = {
            "name":          (request.form.get("name", "") or "").strip(),
            "prefix":        (request.form.get("prefix", "") or "").strip(),
            "address":       (request.form.get("address", "") or "").strip(),
            "rut":           (request.form.get("rut", "") or "").strip(),
            "logo":          current.get("logo", ""),
            "portada_color": portada_color,
        }
        if not data["name"]:
            errors["name"] = "El nombre de la empresa es obligatorio."
        if not errors:
            save_company(data)
            flash("Perfil de empresa guardado.", "success")
            return redirect(url_for("admin_bp.empresa"))
    company = get_company()
    return render_template(
        "empresa.html",
        company=company,
        field_errors=errors,
        logo_version=_company_logo_version(company),
    )


@bp.route("/empresa/logo", methods=["POST"], endpoint="empresa_logo")
@admin_required
def empresa_logo():
    from ..company_config import get_company, save_company
    file = request.files.get("logo")
    if not file or not file.filename:
        flash("No se seleccionó archivo.", "warning")
        return redirect(url_for("admin_bp.empresa"))
    ext = _logo_ext_from_filename(file.filename)
    if ext not in _ALLOWED_LOGO_EXT:
        flash("Formato no permitido. Usa PNG o JPG.", "danger")
        return redirect(url_for("admin_bp.empresa"))
    content = file.read()
    if not content:
        flash("El archivo esta vacio.", "danger")
        return redirect(url_for("admin_bp.empresa"))
    if len(content) > _LOGO_MAX_BYTES:
        flash("El archivo supera 2 MB.", "danger")
        return redirect(url_for("admin_bp.empresa"))
    detected_ext = _detect_logo_ext(content)
    if detected_ext != ext:
        flash("El archivo no parece ser un PNG/JPG valido.", "danger")
        return redirect(url_for("admin_bp.empresa"))
    uploads_dir = _logo_upload_dir()
    _os.makedirs(uploads_dir, exist_ok=True)
    filename = f"logo.{detected_ext}"
    with open(_os.path.join(uploads_dir, filename), "wb") as f:
        f.write(content)
    # Read raw file without merging COMPANY_DEFAULTS so we don't
    # overwrite user-entered fields (name, address, rut, portada_color)
    # with defaults when company.json is missing or partial.
    from ..company_config import save_company
    raw = load("company")
    if not isinstance(raw, dict):
        raw = {}
    raw["logo"] = f"uploads/{filename}"
    save_company(raw)
    flash("Logo actualizado.", "success")
    return redirect(url_for("admin_bp.empresa"))


# ─────────────────────────────────────────────────────────────
# Tipos de proyecto (project templates)
# ─────────────────────────────────────────────────────────────

@bp.route("/project-templates", methods=["GET", "POST"], endpoint="project_templates_admin")
@admin_required
def project_templates_admin():
    from ..templates_config import get_project_templates, save_project_templates
    templates = get_project_templates()
    if request.method == "POST":
        action = request.form.get("action", "")
        if action == "add":
            name = (request.form.get("name", "") or "").strip()
            stages_raw = request.form.get("stages", "") or ""
            stages = [s.strip() for s in stages_raw.split(",") if s.strip()]
            if name and stages:
                templates.append({
                    "id": new_id().lower(),
                    "name": name,
                    "stages": stages,
                })
                save_project_templates(templates)
                flash(f"Tipo de proyecto '{name}' agregado.", "success")
            else:
                flash("El nombre y al menos una etapa son requeridos.", "warning")
        elif action == "delete":
            tid = request.form.get("template_id", "")
            templates = [t for t in templates if t["id"] != tid]
            save_project_templates(templates)
            flash("Tipo de proyecto eliminado.", "success")
        return redirect(url_for("admin_bp.project_templates_admin"))
    return render_template("project_templates.html", templates=templates)


# ─────────────────────────────────────────────────────────────
# Plantillas de cotización por tipo
# ─────────────────────────────────────────────────────────────

_QUOTE_TYPES = ("Proyecto", "Obra", "Servicio")
_SPECS_FIELDS = ("condiciones_pago", "exclusiones", "validez", "forma_entrega", "contacto")


@bp.route("/quote-templates", methods=["GET", "POST"], endpoint="quote_templates")
@admin_required
def quote_templates():
    from ..pdfs import QUOTE_TERMS_DEFAULTS
    from ..quote_templates_config import get_quote_templates, save_quote_templates
    current = get_quote_templates()
    if request.method == "POST":
        for qtype in _QUOTE_TYPES:
            sections_raw = request.form.get(f"{qtype}_sections", "")
            current[qtype]["sections_default"] = [
                s.strip() for s in sections_raw.splitlines() if s.strip()
            ]
            current[qtype]["notes_default"] = request.form.get(f"{qtype}_notes", "").strip()
            for field in _SPECS_FIELDS:
                current[qtype]["specs_default"][field] = request.form.get(f"{qtype}_{field}", "").strip()
            current[qtype]["terms_default"] = [
                {
                    "key": key,
                    "title": title,
                    "body": request.form.get(f"{qtype}_term_{key}_body", "").strip() or default_body,
                    "enabled": bool(request.form.get(f"{qtype}_term_{key}_enabled")),
                }
                for key, title, default_body in QUOTE_TERMS_DEFAULTS
            ]
        save_quote_templates(current)
        flash("Plantillas de cotización guardadas.", "success")
        return redirect(url_for("admin_bp.quote_templates"))
    return render_template("quote_templates.html", templates=current, quote_types=_QUOTE_TYPES, specs_fields=_SPECS_FIELDS)


_IMPORTABLE = {
    "catalogo":    "Catálogo",
    "proveedores": "Proveedores",
    "fichas":      "Fichas técnicas",
    "bundles":     "Bundles",
}


@bp.route("/import-json", methods=["GET", "POST"], endpoint="import_json")
@admin_required
def import_json():
    if request.method == "POST":
        imported = []
        errors = []
        for key, label in _IMPORTABLE.items():
            file = request.files.get(key)
            if not file or not file.filename:
                continue
            try:
                data = json.loads(file.read().decode("utf-8-sig"))
            except Exception as exc:
                errors.append(f"{label}: JSON inválido — {exc}")
                continue
            if not isinstance(data, list):
                errors.append(f"{label}: se esperaba una lista, no {type(data).__name__}")
                continue
            save(key, data)
            imported.append(f"{label} ({len(data)} registros)")
        if imported:
            flash("Importado correctamente: " + ", ".join(imported) + ".", "success")
        if errors:
            for err in errors:
                flash(err, "danger")
        if not imported and not errors:
            flash("No se seleccionó ningún archivo.", "warning")
        return redirect(url_for("admin_bp.import_json"))
    return render_template("import_json.html", importable=_IMPORTABLE)


@bp.route("/export", methods=["GET"], endpoint="export_data")
@admin_required
def export_data():
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font
    from ..catalog import catalog_maps, hydrate_ldm, hydrate_quote
    from ..pdfs import build_ldm_pdf, build_quote_pdf
    from .quotes import _build_quote_workbook

    projects  = load("projects")
    quotes    = load("quotes")
    ldms      = load("materiales")
    cat_maps  = catalog_maps()

    quotes_by_project = {}
    for q in quotes:
        quotes_by_project.setdefault(q.get("project_id"), []).append(q)
    ldms_by_project = {}
    for ldm in ldms:
        ldms_by_project.setdefault(ldm.get("project_id"), []).append(ldm)

    zip_buf = io.BytesIO()
    date_tag = today()
    prefix = f"export-{date_tag}"
    errors = []

    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # ── 1. Raw JSON backup ──────────────────────────────────────────────
        for key, path in FILES.items():
            if os.path.exists(path):
                zf.write(path, f"{prefix}/datos/{os.path.basename(path)}")

        # ── 2. Cotizaciones: PDF + Excel por proyecto ───────────────────────
        for project in projects:
            pid   = project["id"]
            clave = project.get("clave", pid)
            folder = f"{prefix}/cotizaciones/{clave}/"
            for quote in quotes_by_project.get(pid, []):
                hydrated = hydrate_quote(quote, *cat_maps)
                qnum = hydrated.get("quote_number", quote["id"])
                try:
                    pdf_bytes = build_quote_pdf(project, hydrated)
                    zf.writestr(f"{folder}{qnum}.pdf", pdf_bytes)
                except Exception as exc:
                    errors.append(f"PDF {qnum}: {exc}")
                try:
                    wb, fname = _build_quote_workbook(project, quote, Workbook, Alignment, Font)
                    xbuf = io.BytesIO()
                    wb.save(xbuf)
                    zf.writestr(f"{folder}{fname}", xbuf.getvalue())
                except Exception as exc:
                    errors.append(f"Excel {qnum}: {exc}")

        # ── 3. LDMs: PDF + CSV por proyecto ────────────────────────────────
        for project in projects:
            pid   = project["id"]
            clave = project.get("clave", pid)
            folder = f"{prefix}/listas/{clave}/"
            for ldm in ldms_by_project.get(pid, []):
                hydrated = hydrate_ldm(ldm, *cat_maps)
                lnum = hydrated.get("ldm_number", ldm["id"])
                try:
                    pdf_bytes = build_ldm_pdf(project, hydrated)
                    zf.writestr(f"{folder}{lnum}.pdf", pdf_bytes)
                except Exception as exc:
                    errors.append(f"PDF {lnum}: {exc}")
                try:
                    csv_io = io.StringIO()
                    writer = _csv.writer(csv_io)
                    writer.writerow(["description", "unit", "qty", "catalog_item_id",
                                     "proveedor", "fecha", "ldm_number"])
                    for item in hydrated.get("items", []):
                        writer.writerow([
                            item.get("description", ""), item.get("unit", "pza"),
                            item.get("qty", 0), item.get("catalog_item_id", ""),
                            hydrated.get("proveedor", ""), hydrated.get("fecha", ""), lnum,
                        ])
                    zf.writestr(f"{folder}{lnum}.csv", "﻿" + csv_io.getvalue())
                except Exception as exc:
                    errors.append(f"CSV {lnum}: {exc}")

        if errors:
            zf.writestr(f"{prefix}/errores.txt", "\n".join(errors))

    zip_buf.seek(0)
    return send_file(
        zip_buf,
        as_attachment=True,
        download_name=f"{prefix}.zip",
        mimetype="application/zip",
    )


@bp.route("/alcances", endpoint="alcances_admin")
@admin_required
def alcances_admin():
    from ..domain import get_alcances
    return render_template("alcances_admin.html", alcances=get_alcances())


@bp.route("/api/alcances/save", methods=["POST"], endpoint="alcances_api_save")
@admin_required
def alcances_api_save():
    import re as _re
    from ..domain import get_alcances
    data = request.get_json(force=True) or []
    if not isinstance(data, list):
        return jsonify(ok=False, error="Formato inválido")
    clean = []
    ids_seen = set()
    for item in data:
        if not isinstance(item, dict):
            continue
        a_id = _re.sub(r"[^a-z0-9_]", "_", (item.get("id") or "").strip().lower()).strip("_")
        nombre = (item.get("nombre") or "").strip()
        if not a_id or not nombre:
            return jsonify(ok=False, error="Cada alcance necesita ID y Nombre.")
        if a_id in ids_seen:
            return jsonify(ok=False, error=f"ID duplicado: {a_id}")
        ids_seen.add(a_id)
        dep_label = (item.get("dep_label") or "").strip() or None
        blocked_by = [str(x).strip() for x in (item.get("blocked_by") or []) if str(x).strip()]
        clean.append({
            "id": a_id,
            "nombre": nombre,
            "source": item.get("source", "propia") if item.get("source") in ("propia", "externa") else "propia",
            "dep_label": dep_label,
            "blocked_by": blocked_by,
            "info_ext": bool(item.get("info_ext", True)),
        })
    save("alcances", clean)
    return jsonify(ok=True, count=len(clean))


@bp.route("/disciplinas", endpoint="disciplinas_admin")
@admin_required
def disciplinas_admin():
    from ..domain import get_disciplinas
    return render_template("disciplinas_admin.html", disciplinas=get_disciplinas())


@bp.route("/api/disciplinas/save", methods=["POST"], endpoint="disciplinas_api_save")
@admin_required
def disciplinas_api_save():
    import re as _re
    data = request.get_json(force=True) or []
    if not isinstance(data, list):
        return jsonify(ok=False, error="Formato inválido")
    clean = []
    ids_seen = set()
    for item in data:
        if not isinstance(item, dict):
            continue
        d_id = _re.sub(r"[^A-Z0-9]", "", (item.get("id") or "").strip().upper())
        nombre = (item.get("nombre") or "").strip()
        if not d_id or not nombre:
            return jsonify(ok=False, error="Cada disciplina necesita ID y Nombre.")
        if d_id in ids_seen:
            return jsonify(ok=False, error=f"ID duplicado: {d_id}")
        ids_seen.add(d_id)
        clean.append({"id": d_id, "nombre": nombre})
    save("disciplinas", clean)
    return jsonify(ok=True, count=len(clean))


@bp.route("/reset-data", methods=["GET", "POST"], endpoint="reset_data")
@admin_required
def reset_data():
    if request.method == "POST":
        if request.form.get("confirm") != "REINICIAR":
            flash("Confirmación incorrecta. Escribe exactamente: REINICIAR", "danger")
            return redirect(url_for("admin_bp.reset_data"))
        for path in FILES.values():
            try:
                os.remove(path)
            except FileNotFoundError:
                pass
        for extra in ("config.json", "documents.json"):
            try:
                os.remove(os.path.join(DATA_DIR, extra))
            except FileNotFoundError:
                pass
        try:
            os.remove(AUTH_DB)
        except FileNotFoundError:
            pass
        init_db()
        logout_user()
        flash("Aplicación reiniciada. Inicia sesión con las credenciales por defecto.", "success")
        return redirect(url_for("auth_bp.login"))
    return render_template("reset_data.html")
