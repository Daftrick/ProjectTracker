from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..bundles import (
    activate_bundle_version,
    add_bundle_version,
    create_bundle,
    delete_bundle_version,
    get_active_bundle_version,
    normalize_bundle,
)
from ..catalog_search import filter_catalog, list_categories
from ..comparison_ignored import SCOPE_BOTH, SCOPE_COMMERCIAL, SCOPE_TECHNICAL, normalize_ignored_item
from ..comparison_rules import (
    DIRECTION_COT_TO_LDM,
    DIRECTION_LDM_TO_COT,
    ROUND_CEIL,
    ROUND_FLOOR,
    ROUND_NONE,
    ROUND_ROUND,
    normalize_rule,
)
from ..deletions import delete_catalog_items_data
from ..domain import TIPOS_FICHA
from ..storage import load, new_id, save, today

# Tope de resultados para autocompletado inline en COT y LDM. Se mantiene
# moderado para no devolver listas larguísimas; si se queda corto se puede
# subir aquí sin tocar la lógica de filtrado.
API_CATALOG_LIMIT = 50

bp = Blueprint("admin_bp", __name__)


def _clean(value):
    return str(value or "").strip()


def _parse_price(value):
    raw = _clean(value) or "0"
    try:
        price = float(raw.replace(",", "."))
    except ValueError:
        return None
    return price if price >= 0 else None


def _catalog_form(form=None):
    form = form or {}
    return {
        "nombre": _clean(form.get("nombre")),
        "descripcion": _clean(form.get("descripcion")),
        "unidad": _clean(form.get("unidad")) or "pza",
        "precio": _clean(form.get("precio")) or "0",
        "categoria": _clean(form.get("categoria")),
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


def _render_catalogo(items=None, q="", categoria="", form_state=None, field_errors=None, open_modal=None):
    full_catalog = items if items is not None else load("catalogo")
    categorias = list_categories(full_catalog)
    visible = filter_catalog(full_catalog, q=q, categoria=categoria)
    return render_template(
        "catalogo.html",
        items=visible,
        q=q or "",
        categoria=categoria or "",
        categorias=categorias,
        total_count=len(full_catalog),
        form_state=form_state or _catalog_form(),
        field_errors=field_errors or {},
        open_modal=open_modal,
    )


def _render_proveedores(proveedores_data=None, q="", form_state=None, field_errors=None, open_modal=None):
    query = (q or "").lower()
    if proveedores_data is None:
        proveedores_data = load("proveedores")
        if query:
            proveedores_data = [
                item
                for item in proveedores_data
                if query in item["nombre"].lower()
                or query in item.get("categoria", "").lower()
                or query in item.get("contacto", "").lower()
            ]
    return render_template(
        "proveedores.html",
        proveedores=proveedores_data,
        q=query,
        form_state=form_state or _proveedor_form(),
        field_errors=field_errors or {},
        open_modal=open_modal,
    )


def _render_fichas(form_state=None, field_errors=None, open_modal=None, filter_tipo=""):
    fichas_data = load("fichas")
    if filter_tipo:
        fichas_data = [item for item in fichas_data if item["tipo"] == filter_tipo]
    projects_by_id = {project["id"]: project for project in load("projects")}
    return render_template(
        "fichas.html",
        fichas=fichas_data,
        filter_tipo=filter_tipo,
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
            "created_at": today(),
        })
        save("catalogo", items)
        flash(f"Artículo '{form_state['nombre']}' agregado al catálogo.", "success")
        return redirect(url_for("catalogo"))
    return _render_catalogo(
        q=request.args.get("q", ""),
        categoria=request.args.get("categoria", ""),
    )


@bp.route("/catalogo/<item_id>/edit", methods=["POST"], endpoint="edit_catalogo")
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
        save("catalogo", items)
        if is_ajax:
            return jsonify({"ok": True, "item": item})
        flash("Artículo actualizado.", "success")
    elif is_ajax:
        return jsonify({"ok": False}), 404
    return redirect(url_for("catalogo"))


@bp.route("/catalogo/<item_id>/delete", methods=["POST"], endpoint="delete_catalogo")
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


@bp.route("/api/catalogo/bulk-delete", methods=["POST"], endpoint="bulk_delete_catalogo")
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
        "created_at": today(),
    }
    items.append(new_item)
    save("catalogo", items)
    return jsonify(new_item), 201


# ─────────────────────────────────────────────────────────────
# Bundles versionados y reglas de comparación COT/LDM
# ─────────────────────────────────────────────────────────────

def _catalog_by_id():
    return {str(item.get("id", "")).strip(): item for item in load("catalogo")}


def _catalog_sorted_by_name():
    return sorted(
        load("catalogo"),
        key=lambda item: str(item.get("nombre", "")).casefold(),
    )


def _catalog_name(item_id, catalog_by_id=None):
    catalog_by_id = catalog_by_id or _catalog_by_id()
    item = catalog_by_id.get(str(item_id or "").strip()) or {}
    return item.get("nombre") or str(item_id or "")


def _parse_float(value, default=0.0):
    raw = _clean(value).replace(",", ".")
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _parse_components(form):
    ids = form.getlist("component_catalog_item_id[]")
    qtys = form.getlist("component_qty[]")
    wastes = form.getlist("component_waste_pct[]")
    rules = form.getlist("component_comparison_rule_id[]")
    notes = form.getlist("component_notes[]")
    components = []
    max_len = max(len(ids), len(qtys), len(wastes), len(rules), len(notes), 0)
    for index in range(max_len):
        catalog_item_id = _clean(ids[index] if index < len(ids) else "")
        qty = _parse_float(qtys[index] if index < len(qtys) else "0")
        if not catalog_item_id and qty <= 0:
            continue
        components.append({
            "catalog_item_id": catalog_item_id,
            "qty": qty,
            "waste_pct": _parse_float(wastes[index] if index < len(wastes) else "0"),
            "comparison_rule_id": _clean(rules[index] if index < len(rules) else ""),
            "notes": _clean(notes[index] if index < len(notes) else ""),
        })
    return components


def _find_bundle(bundles, bundle_id):
    return next((bundle for bundle in bundles if bundle.get("id") == bundle_id), None)


def _find_version(bundle, version_number):
    target = int(version_number)
    current = normalize_bundle(bundle)
    return next((version for version in current.get("versions", []) if int(version.get("version", 0)) == target), None)


def _render_bundles(open_bundle_id=""):
    catalog = _catalog_sorted_by_name()
    catalog_by_id = {item["id"]: item for item in catalog if item.get("id")}
    bundles = [normalize_bundle(bundle) for bundle in load("bundles")]
    bundle_item_ids = {bundle.get("catalog_item_id") for bundle in bundles}
    comparison_rules = [normalize_rule(rule) for rule in load("comparison_rules")]
    return render_template(
        "bundles.html",
        bundles=bundles,
        catalog=catalog,
        catalog_by_id=catalog_by_id,
        bundle_item_ids=bundle_item_ids,
        comparison_rules=comparison_rules,
        open_bundle_id=open_bundle_id,
        get_active_bundle_version=get_active_bundle_version,
    )


@bp.route("/bundles", methods=["GET", "POST"], endpoint="bundles")
def bundles():
    if request.method == "POST":
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
def delete_bundle(bundle_id):
    before = load("bundles")
    after = [bundle for bundle in before if bundle.get("id") != bundle_id]
    save("bundles", after)
    flash("Bundle eliminado.", "warning")
    return redirect(url_for("bundles"))


@bp.route("/bundles/<bundle_id>/versions/<int:version_number>/update", methods=["POST"], endpoint="update_bundle_version")
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
def add_bundle_version_route(bundle_id):
    items = load("bundles")
    bundle = _find_bundle(items, bundle_id)
    if not bundle:
        flash("Bundle no encontrado.", "danger")
        return redirect(url_for("bundles"))
    source_version_number = int(_parse_float(request.form.get("source_version"), 0))
    source = _find_version(bundle, source_version_number) if source_version_number else get_active_bundle_version(bundle)
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


def _rule_form(form):
    direction = _clean(form.get("direction")) or DIRECTION_LDM_TO_COT
    if direction not in {DIRECTION_LDM_TO_COT, DIRECTION_COT_TO_LDM}:
        direction = DIRECTION_LDM_TO_COT
    rounding = _clean(form.get("rounding")) or ROUND_NONE
    if rounding not in {ROUND_NONE, ROUND_CEIL, ROUND_FLOOR, ROUND_ROUND}:
        rounding = ROUND_NONE
    return {
        "name": _clean(form.get("name")),
        "cot_catalog_item_id": _clean(form.get("cot_catalog_item_id")),
        "ldm_catalog_item_id": _clean(form.get("ldm_catalog_item_id")),
        "cot_unit": _clean(form.get("cot_unit")),
        "ldm_unit": _clean(form.get("ldm_unit")),
        "factor": _parse_float(form.get("factor"), 1.0) or 1.0,
        "direction": direction,
        "rounding": rounding,
        "tolerance_pct": _parse_float(form.get("tolerance_pct"), 5.0),
        "active": bool(form.get("active")),
        "notes": _clean(form.get("notes")),
    }


def _ignored_form(form):
    scope = _clean(form.get("scope")) or SCOPE_BOTH
    if scope not in {SCOPE_BOTH, SCOPE_COMMERCIAL, SCOPE_TECHNICAL}:
        scope = SCOPE_BOTH
    return {
        "catalog_item_id": _clean(form.get("catalog_item_id")),
        "scope": scope,
        "active": bool(form.get("active")),
        "notes": _clean(form.get("notes")),
    }


def _ignored_items_sorted():
    return sorted(
        [normalize_ignored_item(item) for item in load("comparison_ignored_items")],
        key=lambda item: (item.get("scope", ""), _catalog_name(item.get("catalog_item_id")).casefold()),
    )


def _render_comparison_rules(open_rule_id=""):
    catalog = _catalog_sorted_by_name()
    catalog_by_id = {item["id"]: item for item in catalog if item.get("id")}
    rules = [normalize_rule(rule) for rule in load("comparison_rules")]
    return render_template(
        "comparison_rules.html",
        rules=rules,
        catalog=catalog,
        catalog_by_id=catalog_by_id,
        open_rule_id=open_rule_id,
        directions=[DIRECTION_LDM_TO_COT, DIRECTION_COT_TO_LDM],
        roundings=[ROUND_NONE, ROUND_CEIL, ROUND_FLOOR, ROUND_ROUND],
        ignored_items=_ignored_items_sorted(),
        ignored_scopes=[SCOPE_BOTH, SCOPE_COMMERCIAL, SCOPE_TECHNICAL],
    )


@bp.route("/comparison-rules", methods=["GET", "POST"], endpoint="comparison_rules")
def comparison_rules():
    if request.method == "POST":
        form_state = _rule_form(request.form)
        catalog_by_id = _catalog_by_id()
        if form_state["cot_catalog_item_id"] not in catalog_by_id or form_state["ldm_catalog_item_id"] not in catalog_by_id:
            flash("Selecciona artículos válidos para COT y LDM.", "warning")
            return _render_comparison_rules()
        rule = normalize_rule({
            "id": new_id(),
            **form_state,
            "created_at": today(),
            "updated_at": today(),
        })
        rules = load("comparison_rules")
        rules.append(rule)
        save("comparison_rules", rules)
        flash("Regla de comparación creada.", "success")
        return redirect(url_for("comparison_rules") + f"#rule-{rule['id']}")
    return _render_comparison_rules()


@bp.route("/comparison-rules/<rule_id>/edit", methods=["POST"], endpoint="edit_comparison_rule")
def edit_comparison_rule(rule_id):
    rules = load("comparison_rules")
    rule = next((item for item in rules if item.get("id") == rule_id), None)
    if not rule:
        flash("Regla no encontrada.", "danger")
        return redirect(url_for("comparison_rules"))
    form_state = _rule_form(request.form)
    catalog_by_id = _catalog_by_id()
    if form_state["cot_catalog_item_id"] not in catalog_by_id or form_state["ldm_catalog_item_id"] not in catalog_by_id:
        flash("Selecciona artículos válidos para COT y LDM.", "warning")
        return redirect(url_for("comparison_rules") + f"#rule-{rule_id}")
    rule.update(form_state)
    rule["updated_at"] = today()
    save("comparison_rules", rules)
    flash("Regla actualizada.", "success")
    return redirect(url_for("comparison_rules") + f"#rule-{rule_id}")


@bp.route("/comparison-rules/<rule_id>/toggle", methods=["POST"], endpoint="toggle_comparison_rule")
def toggle_comparison_rule(rule_id):
    rules = load("comparison_rules")
    rule = next((item for item in rules if item.get("id") == rule_id), None)
    if rule:
        rule["active"] = not bool(rule.get("active", True))
        rule["updated_at"] = today()
        save("comparison_rules", rules)
        flash("Estado de regla actualizado.", "info")
    return redirect(url_for("comparison_rules") + f"#rule-{rule_id}")


@bp.route("/comparison-rules/<rule_id>/delete", methods=["POST"], endpoint="delete_comparison_rule")
def delete_comparison_rule(rule_id):
    save("comparison_rules", [rule for rule in load("comparison_rules") if rule.get("id") != rule_id])
    flash("Regla eliminada.", "warning")
    return redirect(url_for("comparison_rules"))


@bp.route("/comparison-ignored", methods=["POST"], endpoint="add_comparison_ignored")
def add_comparison_ignored():
    form_state = _ignored_form(request.form)
    catalog_by_id = _catalog_by_id()
    if form_state["catalog_item_id"] not in catalog_by_id:
        flash("Selecciona un artículo válido para ignorar.", "warning")
        return redirect(url_for("comparison_rules") + "#ignored-items")
    items = load("comparison_ignored_items")
    duplicate = next(
        (item for item in items if item.get("catalog_item_id") == form_state["catalog_item_id"] and item.get("scope", SCOPE_BOTH) == form_state["scope"]),
        None,
    )
    if duplicate:
        flash("Ese artículo ya está configurado para ese alcance de comparación.", "warning")
        return redirect(url_for("comparison_rules") + "#ignored-items")
    ignored = normalize_ignored_item({
        "id": new_id(),
        **form_state,
        "created_at": today(),
        "updated_at": today(),
    })
    items.append(ignored)
    save("comparison_ignored_items", items)
    flash("Artículo ignorado agregado.", "success")
    return redirect(url_for("comparison_rules") + "#ignored-items")


@bp.route("/comparison-ignored/<ignored_id>/edit", methods=["POST"], endpoint="edit_comparison_ignored")
def edit_comparison_ignored(ignored_id):
    items = load("comparison_ignored_items")
    ignored = next((item for item in items if item.get("id") == ignored_id), None)
    if not ignored:
        flash("Configuración no encontrada.", "danger")
        return redirect(url_for("comparison_rules") + "#ignored-items")
    form_state = _ignored_form(request.form)
    if form_state["catalog_item_id"] not in _catalog_by_id():
        flash("Selecciona un artículo válido.", "warning")
        return redirect(url_for("comparison_rules") + "#ignored-items")
    ignored.update(form_state)
    ignored["updated_at"] = today()
    save("comparison_ignored_items", items)
    flash("Artículo ignorado actualizado.", "success")
    return redirect(url_for("comparison_rules") + "#ignored-items")


@bp.route("/comparison-ignored/<ignored_id>/toggle", methods=["POST"], endpoint="toggle_comparison_ignored")
def toggle_comparison_ignored(ignored_id):
    items = load("comparison_ignored_items")
    ignored = next((item for item in items if item.get("id") == ignored_id), None)
    if ignored:
        ignored["active"] = not bool(ignored.get("active", True))
        ignored["updated_at"] = today()
        save("comparison_ignored_items", items)
        flash("Estado de artículo ignorado actualizado.", "info")
    return redirect(url_for("comparison_rules") + "#ignored-items")


@bp.route("/comparison-ignored/<ignored_id>/delete", methods=["POST"], endpoint="delete_comparison_ignored")
def delete_comparison_ignored(ignored_id):
    save("comparison_ignored_items", [item for item in load("comparison_ignored_items") if item.get("id") != ignored_id])
    flash("Artículo ignorado eliminado.", "warning")
    return redirect(url_for("comparison_rules") + "#ignored-items")


@bp.route("/proveedores", methods=["GET", "POST"], endpoint="proveedores")
def proveedores():
    if request.method == "POST":
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
    return _render_proveedores(q=request.args.get("q", ""))


@bp.route("/proveedores/<prov_id>/edit", methods=["POST"], endpoint="edit_proveedor")
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
def delete_proveedor(prov_id):
    save("proveedores", [item for item in load("proveedores") if item["id"] != prov_id])
    flash("Proveedor eliminado.", "warning")
    return redirect(url_for("proveedores"))


@bp.route("/fichas", methods=["GET", "POST"], endpoint="fichas")
def fichas():
    if request.method == "POST":
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
    return _render_fichas(filter_tipo=filter_tipo)


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
def delete_ficha(ficha_id):
    save("fichas", [item for item in load("fichas") if item["id"] != ficha_id])
    flash("Ficha eliminada.", "warning")
    return redirect(url_for("fichas"))


@bp.route("/team", methods=["GET", "POST"], endpoint="team")
def team():
    if request.method == "POST":
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
def delete_member(member_id):
    save("team", [item for item in load("team") if item["id"] != member_id])
    flash("Miembro eliminado.", "warning")
    return redirect(url_for("team"))
