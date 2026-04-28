from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..catalog_search import filter_catalog, list_categories
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
