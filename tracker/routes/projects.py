from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for

from ..catalog import catalog_maps, hydrate_ldm, hydrate_quote
from ..consistency import compute_consistency
from ..deletions import delete_project_data
from ..domain import project_semaphore
from ..project_view import build_project_detail_context
from ..services import create_project
from ..pdfs import build_progress_pdf
from ..auth import admin_required
from ..storage import load, new_id, save, today
from ..templates_config import get_project_templates
from ..validators import validate_project_form

bp = Blueprint("projects_bp", __name__)


def _find_project(project_id):
    return next((item for item in load("projects") if item["id"] == project_id), None)


def _blank_project_form_state():
    return {
        "fields": {
            "name": "",
            "client": "",
            "clave": "",
            "version": "V1",
            "fecha": "",
            "notes": "",
            "disciplina": "",
            "drive_url": "",
        },
        "field_errors": {},
    }


@bp.route("/", endpoint="dashboard")
def dashboard():
    projects = load("projects")
    catalog_by_id, catalog_by_name = catalog_maps()
    raw_quotes = load("quotes")
    raw_materiales = load("materiales")
    hydrated_quotes = [hydrate_quote(q, catalog_by_id, catalog_by_name) for q in raw_quotes]
    hydrated_ldms = [hydrate_ldm(m, catalog_by_id, catalog_by_name) for m in raw_materiales]

    for project in projects:
        project["consistency"] = compute_consistency(
            project, hydrated_quotes, hydrated_ldms, catalog_by_id,
        )
        project["semaphore"] = project_semaphore(project, today())

    active = [p for p in projects if not p.get("closed_at") and p.get("status") not in ("Entregado", "Archivado")]
    delivered = [p for p in projects if not p.get("closed_at") and p.get("status") == "Entregado"]
    closed = [p for p in projects if p.get("closed_at") or p.get("status") == "Archivado"]

    today_date = date.today()
    deadline_alerts = []
    for p in active:
        if p.get("deadline"):
            try:
                dl = date.fromisoformat(p["deadline"])
                if dl < today_date:
                    deadline_alerts.append({
                        "id": p["id"],
                        "name": p["name"],
                        "clave": p["clave"],
                        "days_overdue": (today_date - dl).days,
                    })
            except Exception:
                pass
    return render_template("dashboard.html", active=active, delivered=delivered, closed=closed, deadline_alerts=deadline_alerts)


@bp.route("/projects/new", methods=["GET", "POST"], endpoint="new_project")
@admin_required
def new_project():
    if request.method == "POST":
        validation = validate_project_form(request.form)
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return render_template(
                "project_new.html",
                form_state={
                    "fields": validation["fields"],
                    "field_errors": validation["field_errors"],
                },
            )
        projects = load("projects")
        project = create_project(projects, validation["fields"])
        project["deadline"] = request.form.get("deadline", "").strip() or None
        project["drive_url"] = request.form.get("drive_url", "").strip() or ""
        project["updated_at"] = today()
        projects.append(project)
        save("projects", projects)
        flash(f"Proyecto '{project['name']}' creado.", "success")
        return redirect(url_for("project_detail", project_id=project["id"]))
    return render_template("project_new.html", form_state=_blank_project_form_state())


@bp.route("/projects/<project_id>", endpoint="project_detail")
def project_detail(project_id):
    project = _find_project(project_id)
    if not project:
        flash("Proyecto no encontrado.", "danger")
        return redirect(url_for("dashboard"))
    templates_map = {t["id"]: t for t in get_project_templates()}
    tmpl = templates_map.get(project.get("template_id", ""))
    stage_budget = project.get("stage_budget") or {}
    stage_budget_totals = {"planned": 0.0, "actual": 0.0}
    if tmpl:
        for stage in tmpl["stages"]:
            bd = stage_budget.get(stage, {})
            stage_budget_totals["planned"] += float(bd.get("planned") or 0)
            stage_budget_totals["actual"] += float(bd.get("actual") or 0)
    return render_template(
        "project_detail.html",
        **build_project_detail_context(project),
        templates_map=templates_map,
        stage_budget_totals=stage_budget_totals,
    )


@bp.route("/projects/<project_id>/update", methods=["POST"], endpoint="update_project")
def update_project(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if project:
        project["name"] = request.form.get("name", project["name"]).strip()
        project["client"] = request.form.get("client", project.get("client", "")).strip()
        project["clave"] = request.form.get("clave", project["clave"]).strip()
        project["version"] = request.form.get("version", project["version"]).strip()
        project["fecha"] = request.form.get("fecha", project["fecha"]).strip()
        project["notes"] = request.form.get("notes", "").strip()
        project["deadline"] = request.form.get("deadline", "").strip() or None
        project["drive_url"] = request.form.get("drive_url", "").strip() or ""
        project["disciplina"] = request.form.get("disciplina", "").strip()
        project["updated_at"] = today()
        save("projects", projects)
        flash("Proyecto actualizado.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@bp.route("/projects/<project_id>/status", methods=["POST"], endpoint="update_project_status")
def update_project_status(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if project:
        new_status = request.form.get("status", "").strip()
        if new_status in ("Activo", "Entregado", "Archivado"):
            project["status"] = new_status
            if new_status == "Archivado":
                project["closed_at"] = project.get("closed_at") or today()
            else:
                project["closed_at"] = None
            project["updated_at"] = today()
            save("projects", projects)
            flash(f"Estado actualizado a '{new_status}'.", "success")
    return redirect(url_for("project_detail", project_id=project_id))


@bp.route("/projects/<project_id>/close", methods=["POST"], endpoint="close_project")
def close_project(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if project:
        project["closed_at"] = today()
        save("projects", projects)
        flash("Proyecto cerrado.", "success")
    return redirect(url_for("dashboard"))


@bp.route("/projects/<project_id>/reopen", methods=["POST"], endpoint="reopen_project")
def reopen_project(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if project:
        project["closed_at"] = None
        save("projects", projects)
        flash("Proyecto reabierto.", "info")
    return redirect(url_for("project_detail", project_id=project_id))


@bp.route("/projects/<project_id>/delete", methods=["POST"], endpoint="delete_project")
def delete_project(project_id):
    result = delete_project_data(
        project_id,
        load("projects"),
        load("tasks"),
        load("deliveries"),
        load("quotes"),
        load("materiales"),
        load("fichas"),
    )
    save("projects", result["projects"])
    save("tasks", result["tasks"])
    save("deliveries", result["deliveries"])
    save("quotes", result["quotes"])
    save("materiales", result["materiales"])
    save("fichas", result["fichas"])
    counts = result["counts"]
    flash(
        "Proyecto eliminado. "
        f"Se limpiaron {counts['tasks']} tarea(s), {counts['quotes']} cotización(es), "
        f"{counts['materiales']} LDM(s), {counts['deliveries']} entrega(s) y "
        f"{counts['ficha_refs']} vínculo(s) a fichas.",
        "warning",
    )
    return redirect(url_for("dashboard"))





@bp.route("/projects/<project_id>/deliveries/<delivery_id>/delete", methods=["POST"], endpoint="delete_delivery")
def delete_delivery(project_id, delivery_id):
    save("deliveries", [item for item in load("deliveries") if item["id"] != delivery_id])
    flash("Registro de entrega eliminado.", "warning")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-docs")



@bp.route("/projects/<project_id>/stage-status", methods=["POST"], endpoint="update_stage_status")
def update_stage_status(project_id):
    projects = load("projects")
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    stage = request.form.get("stage", "").strip()
    status = request.form.get("status", "pending")
    stage_date = request.form.get("date", "").strip() or None
    if stage:
        stage_status = project.get("stage_status") or {}
        stage_status[stage] = {"status": status, "date": stage_date}
        project["stage_status"] = stage_status
        project["updated_at"] = today()
        save("projects", projects)
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-avance")


@bp.route("/projects/<project_id>/docs-checklist/toggle", methods=["POST"], endpoint="toggle_doc_checklist")
def toggle_doc_checklist(project_id):
    projects = load("projects")
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    item_id = request.form.get("item_id", "")
    checklist = project.get("docs_checklist") or []
    for item in checklist:
        if item["id"] == item_id:
            item["done"] = not item.get("done", False)
            break
    project["docs_checklist"] = checklist
    project["updated_at"] = today()
    save("projects", projects)
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-avance")


@bp.route("/projects/<project_id>/docs-checklist/add", methods=["POST"], endpoint="add_doc_checklist")
def add_doc_checklist(project_id):
    projects = load("projects")
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    name = request.form.get("name", "").strip()
    if name:
        checklist = project.get("docs_checklist") or []
        checklist.append({"id": new_id(), "name": name, "done": False})
        project["docs_checklist"] = checklist
        project["updated_at"] = today()
        save("projects", projects)
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-avance")


@bp.route("/projects/<project_id>/docs-checklist/delete/<item_id>", methods=["POST"], endpoint="delete_doc_checklist")
def delete_doc_checklist(project_id, item_id):
    projects = load("projects")
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    project["docs_checklist"] = [i for i in (project.get("docs_checklist") or []) if i["id"] != item_id]
    project["updated_at"] = today()
    save("projects", projects)
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-avance")


@bp.route("/projects/<project_id>/stage-budget", methods=["POST"], endpoint="update_stage_budget")
def update_stage_budget(project_id):
    projects = load("projects")
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    templates_map = {t["id"]: t for t in get_project_templates()}
    tmpl = templates_map.get(project.get("template_id", ""))
    if tmpl:
        stage_budget = {}
        def _safe_float(value):
            try:
                return float(value or 0)
            except (ValueError, TypeError):
                return 0.0

        for stage in tmpl["stages"]:
            key = stage.replace(" ", "_").replace("-", "_")
            planned = _safe_float(request.form.get(f"planned_{key}"))
            actual = _safe_float(request.form.get(f"actual_{key}"))
            stage_budget[stage] = {"planned": planned, "actual": actual}
        project["stage_budget"] = stage_budget
        project["updated_at"] = today()
        save("projects", projects)
        flash("Presupuesto por etapa actualizado.", "success")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-avance")


@bp.route("/projects/<project_id>/reporte.pdf", endpoint="project_progress_pdf")
def project_progress_pdf(project_id):
    project = _find_project(project_id)
    if not project:
        abort(404)
    templates_map = {t["id"]: t for t in get_project_templates()}
    tmpl = templates_map.get(project.get("template_id", ""))
    try:
        from io import BytesIO
        pdf_bytes = build_progress_pdf(project, tmpl)
        return send_file(
            BytesIO(pdf_bytes),
            as_attachment=True,
            download_name=f"Reporte-{project['clave']}-{today()}.pdf",
            mimetype="application/pdf",
        )
    except Exception as exc:
        flash(f"Error al generar reporte: {exc}", "danger")
        return redirect(url_for("project_detail", project_id=project_id))
