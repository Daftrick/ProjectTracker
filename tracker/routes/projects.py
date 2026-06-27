import os
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, send_file, url_for

from ..catalog import catalog_maps, hydrate_ldm, hydrate_quote
from ..consistency import compute_consistency
from ..deletions import delete_project_data
from ..domain import STAGES, get_alcances, get_progress, project_semaphore, project_stage
from ..project_view import build_project_detail_context
from ..services import (
    apply_task_status_change,
    create_project_with_tasks,
    sync_project_alcances,
    update_observation_details,
    update_observation_checklist_item,
)
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
            "template_id": "",
            "drive_url": "",
        },
        "alcances": ["cotizacion"],
        "field_errors": {},
    }


@bp.route("/", endpoint="dashboard")
def dashboard():
    projects = load("projects")
    tasks = load("tasks")
    # Cargar quotes y LDMs hidratados una sola vez para reutilizar entre todos
    # los proyectos (evita N+1 lecturas de catálogo).
    catalog_by_id, catalog_by_name = catalog_maps()
    raw_quotes = load("quotes")
    raw_materiales = load("materiales")
    hydrated_quotes = [hydrate_quote(q, catalog_by_id, catalog_by_name) for q in raw_quotes]
    hydrated_ldms = [hydrate_ldm(m, catalog_by_id, catalog_by_name) for m in raw_materiales]

    for project in projects:
        progress = get_progress(project["id"], tasks)
        project.update(progress)
        main_tasks = [task for task in tasks if task["project_id"] == project["id"] and not task.get("parent_task_id")]
        project["obs"] = sum(
            1
            for task in tasks
            if task["project_id"] == project["id"]
            and task.get("parent_task_id")
            and task.get("status") != "Aprobado"
        )
        project["review"] = sum(1 for task in main_tasks if task["status"] == "Revisión")
        # KPI de consistencia COT vs LDM.
        project["consistency"] = compute_consistency(
            project,
            hydrated_quotes,
            hydrated_ldms,
            catalog_by_id,
        )
        project["semaphore"] = project_semaphore(project, today())

    active = [project for project in projects if not project.get("closed_at") and project.get("status") != "Completado"]
    completed = [project for project in projects if not project.get("closed_at") and project.get("status") == "Completado"]
    closed = [project for project in projects if project.get("closed_at")]
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
    return render_template("dashboard.html", active=active, completed=completed, closed=closed, deadline_alerts=deadline_alerts)


@bp.route("/kanban", endpoint="kanban")
def kanban():
    projects = load("projects")
    tasks = load("tasks")
    open_projects = [p for p in projects if not p.get("closed_at")]
    for p in open_projects:
        progress = get_progress(p["id"], tasks)
        p.update(progress)
        p["stage"] = project_stage(p, tasks)
        p["semaphore"] = project_semaphore(p, today())
    by_stage = {stage: [] for stage in STAGES}
    for p in open_projects:
        by_stage[p["stage"]].append(p)
    return render_template("kanban.html", by_stage=by_stage)


@bp.route("/projects/<project_id>/toggle_obra", methods=["POST"], endpoint="toggle_obra")
@admin_required
def toggle_obra(project_id):
    projects = load("projects")
    project = next((p for p in projects if p["id"] == project_id), None)
    if not project or project.get("closed_at"):
        abort(404)
    project["in_obra"] = not project.get("in_obra", False)
    save("projects", projects)
    return redirect(url_for("kanban"))


@bp.route("/projects/new", methods=["GET", "POST"], endpoint="new_project")
@admin_required
def new_project():
    if request.method == "POST":
        selected = request.form.getlist("alcances")
        validation = validate_project_form(request.form, selected, set(alcance["id"] for alcance in get_alcances()))
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return render_template(
                "project_new.html",
                form_state={
                    "fields": validation["fields"],
                    "alcances": validation["alcances"],
                    "field_errors": validation["field_errors"],
                },
            )
        projects = load("projects")
        project, tasks = create_project_with_tasks(
            projects, load("tasks"), validation["fields"], validation["alcances"]
        )
        project["deadline"] = request.form.get("deadline", "").strip() or None
        project["template_id"] = request.form.get("template_id", "").strip() or ""
        project["drive_url"] = request.form.get("drive_url", "").strip() or ""
        project["updated_at"] = today()
        projects.append(project)
        save("projects", projects)
        save("tasks", tasks)
        flash(f"Proyecto '{project['name']}' creado con {len(selected)} alcance(s).", "success")
        return redirect(url_for("project_detail", project_id=project["id"]))
    return render_template(
        "project_new.html",
        form_state=_blank_project_form_state(),
        project_templates=get_project_templates(),
    )


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
        project["updated_at"] = today()
        save("projects", projects)
        flash("Proyecto actualizado.", "success")
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


@bp.route("/projects/<project_id>/tasks/<task_id>/status", methods=["POST"], endpoint="update_task_status")
def update_task_status(project_id, task_id):
    tasks = load("tasks")
    result = apply_task_status_change(
        tasks,
        project_id,
        task_id,
        request.form.get("status"),
        request.form.get("note", "").strip(),
        request.form.get("checklist", "").strip(),
    )
    if not result["task"]:
        return redirect(url_for("project_detail", project_id=project_id))
    if result["blocked"]:
        flash("⚠ Este alcance está bloqueado por dependencias sin aprobar.", "warning")
        return redirect(url_for("project_detail", project_id=project_id))
    if result["created_observation"]:
        obs_num = sum(1 for item in result["tasks"] if item.get("parent_task_id") == task_id)
        flash(f"Subtarea de seguimiento #{obs_num} creada.", "info")
    save("tasks", result["tasks"])
    flash(f"Estado → '{result['task']['status']}'.", "success")
    open_task = task_id if result["created_observation"] else None
    target = url_for("project_detail", project_id=project_id)
    if open_task:
        target = f"{target}?open={open_task}"
    return redirect(target + "#tab-alcances")


@bp.route(
    "/projects/<project_id>/observations/<observation_id>/checklist/<item_id>",
    methods=["POST"],
    endpoint="update_observation_checklist",
)
def update_observation_checklist(project_id, observation_id, item_id):
    tasks = load("tasks")
    result = update_observation_checklist_item(
        tasks,
        project_id,
        observation_id,
        item_id,
        bool(request.form.get("done")),
    )
    if result["task"]:
        save("tasks", result["tasks"])
    parent_id = result["task"].get("parent_task_id") if result["task"] else None
    target = url_for("project_detail", project_id=project_id)
    if parent_id:
        target = f"{target}?open={parent_id}"
    return redirect(target + "#tab-alcances")


@bp.route(
    "/projects/<project_id>/observations/<observation_id>/update",
    methods=["POST"],
    endpoint="update_observation",
)
def update_observation(project_id, observation_id):
    tasks = load("tasks")
    result = update_observation_details(
        tasks,
        project_id,
        observation_id,
        request.form.get("notes", ""),
        request.form.get("checklist", ""),
    )
    if result["task"]:
        save("tasks", result["tasks"])
        flash("Observación actualizada.", "success")
    parent_id = result["task"].get("parent_task_id") if result["task"] else None
    target = url_for("project_detail", project_id=project_id)
    if parent_id:
        target = f"{target}?open={parent_id}"
    return redirect(target + "#tab-alcances")


@bp.route("/projects/<project_id>/tasks/<task_id>/info", methods=["POST"], endpoint="update_task_info")
def update_task_info(project_id, task_id):
    tasks = load("tasks")
    task = next((item for item in tasks if item["id"] == task_id), None)
    if task:
        task["source"] = request.form.get("source", task.get("source", "propia"))
        task["external_dep"] = request.form.get("external_dep", "").strip() or None
        task["info_status"] = request.form.get("info_status", "Pendiente") if task["source"] == "externa" else None
        save("tasks", tasks)
    return redirect(url_for("project_detail", project_id=project_id))


@bp.route("/projects/<project_id>/tasks/<task_id>/note", methods=["POST"], endpoint="save_task_note")
def save_task_note(project_id, task_id):
    tasks = load("tasks")
    task = next((item for item in tasks if item["id"] == task_id), None)
    if task:
        task["notes"] = request.form.get("notes", "").strip()
        save("tasks", tasks)
    return redirect(url_for("project_detail", project_id=project_id))



@bp.route("/projects/<project_id>/alcances/update", methods=["POST"], endpoint="update_project_alcances")
def update_project_alcances(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    new_alcances = request.form.getlist("alcances")
    result = sync_project_alcances(project, load("tasks"), new_alcances)
    project["updated_at"] = today()
    save("projects", projects)
    save("tasks", result["tasks"])
    if result["added"] or result["removed"]:
        flash(
            f"Alcances actualizados ({len(result['added'])} agregado(s), {len(result['removed'])} eliminado(s)).",
            "success",
        )
    return redirect(url_for("project_detail", project_id=project_id))



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
