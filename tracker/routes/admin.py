from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..domain import TIPOS_FICHA
from ..storage import load, new_id, save, today

bp = Blueprint("admin_bp", __name__)


@bp.route("/catalogo", methods=["GET", "POST"], endpoint="catalogo")
def catalogo():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es requerido.", "warning")
            return redirect(url_for("catalogo"))
        items = load("catalogo")
        items.append({
            "id": new_id(),
            "nombre": nombre,
            "descripcion": request.form.get("descripcion", "").strip(),
            "unidad": request.form.get("unidad", "pza").strip() or "pza",
            "precio": float(request.form.get("precio", 0) or 0),
            "created_at": today(),
        })
        save("catalogo", items)
        flash(f"Artículo '{nombre}' agregado al catálogo.", "success")
        return redirect(url_for("catalogo"))
    query = request.args.get("q", "").lower()
    items = load("catalogo")
    if query:
        items = [item for item in items if query in item["nombre"].lower() or query in item.get("descripcion", "").lower()]
    items.sort(key=lambda item: item["nombre"].lower())
    return render_template("catalogo.html", items=items, q=query)


@bp.route("/catalogo/<item_id>/edit", methods=["POST"], endpoint="edit_catalogo")
def edit_catalogo(item_id):
    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
    items = load("catalogo")
    item = next((entry for entry in items if entry["id"] == item_id), None)
    if item:
        item["nombre"] = request.form.get("nombre", item["nombre"]).strip()
        item["descripcion"] = request.form.get("descripcion", "").strip()
        item["unidad"] = request.form.get("unidad", "pza").strip() or "pza"
        item["precio"] = float(request.form.get("precio", 0) or 0)
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
    save("catalogo", [item for item in load("catalogo") if item["id"] != item_id])
    if is_ajax:
        return jsonify({"ok": True})
    flash("Artículo eliminado.", "warning")
    return redirect(url_for("catalogo"))


@bp.route("/api/catalogo/bulk-delete", methods=["POST"], endpoint="bulk_delete_catalogo")
def bulk_delete_catalogo():
    ids = set((request.get_json(force=True) or {}).get("ids", []))
    items = [item for item in load("catalogo") if item["id"] not in ids]
    save("catalogo", items)
    return jsonify({"ok": True, "deleted": len(ids)})


@bp.route("/api/catalogo", endpoint="api_catalogo")
def api_catalogo():
    query = request.args.get("q", "").lower()
    items = load("catalogo")
    if query:
        items = [item for item in items if query in item["nombre"].lower() or query in item.get("descripcion", "").lower()]
    items.sort(key=lambda item: item["nombre"].lower())
    return jsonify(items[:30])


@bp.route("/api/catalogo/add", methods=["POST"], endpoint="api_catalogo_add")
def api_catalogo_add():
    data = request.get_json(force=True) or {}
    nombre = data.get("nombre", "").strip()
    if not nombre:
        return jsonify({"error": "Nombre requerido"}), 400
    items = load("catalogo")
    new_item = {
        "id": new_id(),
        "nombre": nombre,
        "descripcion": data.get("descripcion", "").strip(),
        "unidad": (data.get("unidad", "") or "pza").strip(),
        "precio": float(data.get("precio", 0) or 0),
        "created_at": today(),
    }
    items.append(new_item)
    save("catalogo", items)
    return jsonify(new_item), 201


@bp.route("/proveedores", methods=["GET", "POST"], endpoint="proveedores")
def proveedores():
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not nombre:
            flash("El nombre es requerido.", "warning")
            return redirect(url_for("proveedores"))
        proveedores_data = load("proveedores")
        proveedores_data.append({
            "id": new_id(),
            "nombre": nombre,
            "contacto": request.form.get("contacto", "").strip(),
            "email": request.form.get("email", "").strip(),
            "telefono": request.form.get("telefono", "").strip(),
            "categoria": request.form.get("categoria", "").strip(),
            "notas": request.form.get("notas", "").strip(),
            "created_at": today(),
        })
        save("proveedores", proveedores_data)
        flash(f"Proveedor '{nombre}' registrado.", "success")
        return redirect(url_for("proveedores"))
    query = request.args.get("q", "").lower()
    proveedores_data = load("proveedores")
    if query:
        proveedores_data = [
            item
            for item in proveedores_data
            if query in item["nombre"].lower()
            or query in item.get("categoria", "").lower()
            or query in item.get("contacto", "").lower()
        ]
    return render_template("proveedores.html", proveedores=proveedores_data, q=query)


@bp.route("/proveedores/<prov_id>/edit", methods=["POST"], endpoint="edit_proveedor")
def edit_proveedor(prov_id):
    proveedores_data = load("proveedores")
    proveedor = next((item for item in proveedores_data if item["id"] == prov_id), None)
    if proveedor:
        proveedor["nombre"] = request.form.get("nombre", proveedor["nombre"]).strip()
        proveedor["contacto"] = request.form.get("contacto", "").strip()
        proveedor["email"] = request.form.get("email", "").strip()
        proveedor["telefono"] = request.form.get("telefono", "").strip()
        proveedor["categoria"] = request.form.get("categoria", "").strip()
        proveedor["notas"] = request.form.get("notas", "").strip()
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
        tipo = request.form.get("tipo", "").strip().upper()
        marca = request.form.get("marca", "").strip().upper().replace(" ", "-")
        modelo = request.form.get("modelo", "").strip().upper().replace(" ", "-")
        fichas_data = load("fichas")
        fichas_data.append({
            "id": new_id(),
            "code": f"{tipo}-{marca}-{modelo}",
            "tipo": tipo,
            "marca": marca,
            "modelo": modelo,
            "descripcion": request.form.get("descripcion", "").strip(),
            "filename": request.form.get("filename", "").strip(),
            "projects": [],
            "notes": request.form.get("notes", "").strip(),
            "created_at": today(),
        })
        save("fichas", fichas_data)
        flash(f"Ficha {tipo}-{marca}-{modelo} registrada.", "success")
        return redirect(url_for("fichas"))
    fichas_data = load("fichas")
    filter_tipo = request.args.get("tipo", "")
    if filter_tipo:
        fichas_data = [item for item in fichas_data if item["tipo"] == filter_tipo]
    projects_by_id = {project["id"]: project for project in load("projects")}
    return render_template("fichas.html", fichas=fichas_data, filter_tipo=filter_tipo, projects_by_id=projects_by_id, tipos_ficha=TIPOS_FICHA)


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
        team_data = load("team")
        team_data.append({
            "id": new_id(),
            "name": request.form["name"].strip(),
            "role": request.form.get("role", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip(),
            "notes": request.form.get("notes", "").strip(),
            "created_at": today(),
        })
        save("team", team_data)
        flash("Miembro agregado.", "success")
        return redirect(url_for("team"))
    return render_template("team.html", team=load("team"))


@bp.route("/team/<member_id>/delete", methods=["POST"], endpoint="delete_member")
def delete_member(member_id):
    save("team", [item for item in load("team") if item["id"] != member_id])
    flash("Miembro eliminado.", "warning")
    return redirect(url_for("team"))
