import os
from datetime import date, datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, request, url_for

from ..catalog import catalog_maps, hydrate_ldm
from ..drive import folder_name, load_config
from ..pdfs import build_ldm_pdf
from ..storage import load, new_id, save, today
from ..validators import validate_ldm_form

bp = Blueprint("materials_bp", __name__)


def _clean_form_text(value):
    return str(value or "").strip()


@bp.route("/projects/<project_id>/ldm/new", methods=["GET", "POST"], endpoint="new_ldm")
def new_ldm(project_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
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


@bp.route("/projects/<project_id>/ldm/<ldm_id>/edit", methods=["GET", "POST"], endpoint="edit_ldm")
def edit_ldm(project_id, ldm_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
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
