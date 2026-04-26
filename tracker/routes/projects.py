import os
import threading
import time
import zipfile
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, send_from_directory, url_for

from ..catalog import catalog_maps, hydrate_ldm, hydrate_quote
from ..domain import ALCANCES, check_blocked, get_progress
from ..drive import find_delivery_files, folder_name, load_config, save_config, scan_drive_folder
from ..services import apply_task_status_change, create_project_with_tasks, sync_project_alcances
from ..storage import load, new_id, save, today
from ..validators import validate_project_form

bp = Blueprint("projects_bp", __name__)


@bp.route("/", endpoint="dashboard")
def dashboard():
    projects = load("projects")
    tasks = load("tasks")
    for project in projects:
        progress = get_progress(project["id"], tasks)
        project.update(progress)
        main_tasks = [task for task in tasks if task["project_id"] == project["id"] and not task.get("parent_task_id")]
        project["obs"] = sum(1 for task in main_tasks if task["status"] == "Observaciones")
        project["review"] = sum(1 for task in main_tasks if task["status"] == "Revisión")
    active = [project for project in projects if not project.get("closed_at") and project.get("status") != "Completado"]
    completed = [project for project in projects if not project.get("closed_at") and project.get("status") == "Completado"]
    closed = [project for project in projects if project.get("closed_at")]
    return render_template("dashboard.html", active=active, completed=completed, closed=closed)


@bp.route("/projects/new", methods=["GET", "POST"], endpoint="new_project")
def new_project():
    if request.method == "POST":
        selected = request.form.getlist("alcances")
        validation = validate_project_form(request.form, selected, set(alcance["id"] for alcance in ALCANCES))
        if not validation["ok"]:
            for error in validation["errors"]:
                flash(error, "warning")
            return redirect(url_for("new_project"))
        projects = load("projects")
        project, tasks = create_project_with_tasks(
            projects, load("tasks"), validation["fields"], validation["alcances"]
        )
        projects.append(project)
        save("projects", projects)
        save("tasks", tasks)
        flash(f"Proyecto '{project['name']}' creado con {len(selected)} alcance(s).", "success")
        return redirect(url_for("project_detail", project_id=project["id"]))
    return render_template("project_new.html")


@bp.route("/projects/<project_id>", endpoint="project_detail")
def project_detail(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if not project:
        flash("Proyecto no encontrado.", "danger")
        return redirect(url_for("dashboard"))
    all_tasks = load("tasks")
    project_tasks = [task for task in all_tasks if task["project_id"] == project_id]
    main_tasks = [task for task in project_tasks if not task.get("parent_task_id")]
    for task in main_tasks:
        task["_blocked"] = check_blocked(task, main_tasks)
    subtasks = {}
    for task in project_tasks:
        if task.get("parent_task_id"):
            subtasks.setdefault(task["parent_task_id"], []).append(task)

    deliveries = sorted(
        [delivery for delivery in load("deliveries") if delivery["project_id"] == project_id],
        key=lambda item: item.get("date", ""),
        reverse=True,
    )
    catalog_by_id, catalog_by_name = catalog_maps()
    quotes = sorted(
        [hydrate_quote(quote, catalog_by_id, catalog_by_name) for quote in load("quotes") if quote["project_id"] == project_id],
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )
    ldms = sorted(
        [hydrate_ldm(ldm, catalog_by_id, catalog_by_name) for ldm in load("materiales") if ldm["project_id"] == project_id],
        key=lambda item: item.get("seq", 0),
    )
    all_fichas = load("fichas")
    linked = [ficha for ficha in all_fichas if project_id in ficha.get("projects", [])]
    unlinked = [ficha for ficha in all_fichas if project_id not in ficha.get("projects", [])]
    progress = get_progress(project_id, all_tasks)
    can_close = (
        progress["approved"] == progress["total"]
        and progress["total"] > 0
        and any(delivery.get("dtype") == "completa" for delivery in deliveries)
    )
    cfg = load_config()
    drive_folder = folder_name(project)
    scan = scan_drive_folder(drive_folder, cfg.get("drive_projects_path", ""), ldms, clave=project["clave"])
    available = find_delivery_files(
        drive_folder,
        project["clave"],
        project.get("version", "V1"),
        project.get("fecha", ""),
        cfg.get("drive_projects_path", ""),
        cfg.get("drive_fichas_path", ""),
        linked,
    )
    total_cotizado = round(sum(quote.get("total", 0) for quote in quotes), 2)
    costo_proveedor = round(sum(ldm.get("subtotal_cot", 0) for ldm in ldms), 2)
    margen = round(total_cotizado - costo_proveedor, 2)
    return render_template(
        "project_detail.html",
        project=project,
        main_tasks=main_tasks,
        subtasks=subtasks,
        deliveries=deliveries,
        scan=scan,
        available=available,
        quotes=quotes,
        ldms=ldms,
        linked_fichas=linked,
        unlinked_fichas=unlinked,
        prog=progress,
        can_close=can_close,
        team=load("team"),
        today=today(),
        today_short=date.today().strftime("%y%m%d"),
        folder_name=drive_folder,
        file_ie=f"IE-{project['clave']}-{project['version']}-{project['fecha']}",
        file_xref=f"XREF-{project['clave']}-{project['version']}-{project['fecha']}",
        total_cotizado=total_cotizado,
        costo_proveedor=costo_proveedor,
        margen=margen,
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
    save("projects", [item for item in load("projects") if item["id"] != project_id])
    save("tasks", [item for item in load("tasks") if item["project_id"] != project_id])
    save("deliveries", [item for item in load("deliveries") if item["project_id"] != project_id])
    save("quotes", [item for item in load("quotes") if item["project_id"] != project_id])
    save("materiales", [item for item in load("materiales") if item["project_id"] != project_id])
    flash("Proyecto eliminado.", "warning")
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
    return redirect(url_for("project_detail", project_id=project_id))


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


@bp.route("/settings", methods=["GET", "POST"], endpoint="settings")
def settings():
    cfg = load_config()
    if request.method == "POST":
        cfg["drive_projects_path"] = request.form.get("drive_projects_path", "").strip()
        cfg["drive_fichas_path"] = request.form.get("drive_fichas_path", "").strip()
        save_config(cfg)
        flash("Configuración guardada.", "success")
        return redirect(url_for("settings"))
    return render_template("settings.html", cfg=cfg)


@bp.route("/projects/<project_id>/alcances/update", methods=["POST"], endpoint="update_project_alcances")
def update_project_alcances(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    new_alcances = request.form.getlist("alcances")
    result = sync_project_alcances(project, load("tasks"), new_alcances)
    save("projects", projects)
    save("tasks", result["tasks"])
    if result["added"] or result["removed"]:
        flash(
            f"Alcances actualizados ({len(result['added'])} agregado(s), {len(result['removed'])} eliminado(s)).",
            "success",
        )
    return redirect(url_for("project_detail", project_id=project_id))


@bp.route("/projects/<project_id>/deliveries/create", methods=["POST"], endpoint="create_delivery")
def create_delivery(project_id):
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    cfg = load_config()
    projects_root = cfg.get("drive_projects_path", "")
    fichas_root = cfg.get("drive_fichas_path", "")
    drive_folder = folder_name(project)
    delivery_type = request.form.get("dtype", "completa")
    notes = request.form.get("notes", "").strip()
    linked = [ficha for ficha in load("fichas") if project_id in ficha.get("projects", [])]
    available = find_delivery_files(
        drive_folder,
        project["clave"],
        project.get("version", "V1"),
        project.get("fecha", ""),
        projects_root,
        fichas_root,
        linked,
    )
    file_keys = ["ie_dwg", "ie_pdf", "mem_pdf", "cot_pdf"]
    if delivery_type == "parcial":
        selected_keys = [key for key in file_keys if request.form.get(f"inc_{key}")]
        include_fichas = bool(request.form.get("inc_fichas"))
    else:
        selected_keys = file_keys
        include_fichas = True
    today_token = date.today().strftime("%y%m%d")
    zip_name = f"Entrega-{project['clave']}-{project.get('version', 'V1')}-{today_token}.zip"
    project_folder = os.path.join(projects_root, drive_folder) if projects_root else None
    if not project_folder or not os.path.isdir(project_folder):
        flash("Carpeta del proyecto no encontrada en Drive. Verifica Ajustes.", "danger")
        return redirect(url_for("project_detail", project_id=project_id) + "#tab-docs")
    zip_path = os.path.join(project_folder, zip_name)
    files_included = []
    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as handle:
            for key in selected_keys:
                filename = available.get(key)
                if not filename:
                    continue
                source = os.path.join(project_folder, filename)
                if os.path.isfile(source):
                    handle.write(source, filename)
                    files_included.append(filename)
            if include_fichas:
                for ficha in available.get("fichas", []):
                    handle.write(ficha["path"], os.path.join("Fichas", ficha["name"]))
                    files_included.append(f"Fichas/{ficha['name']}")
        deliveries = load("deliveries")
        deliveries.append({
            "id": new_id(),
            "project_id": project_id,
            "date": today(),
            "version": project.get("version", "V1"),
            "dtype": delivery_type,
            "zip_name": zip_name,
            "zip_path": zip_path,
            "files_included": files_included,
            "notes": notes,
        })
        save("deliveries", deliveries)
        flash(f"Entrega generada: {zip_name}", "success")
    except Exception as exc:
        flash(f"Error al generar ZIP: {exc}", "danger")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-docs")


@bp.route("/projects/<project_id>/deliveries/<delivery_id>/delete", methods=["POST"], endpoint="delete_delivery")
def delete_delivery(project_id, delivery_id):
    save("deliveries", [item for item in load("deliveries") if item["id"] != delivery_id])
    flash("Registro de entrega eliminado.", "warning")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-docs")


@bp.route("/projects/<project_id>/files/<path:filename>", endpoint="serve_project_file")
def serve_project_file(project_id, filename):
    if not filename or filename in {".", ".."}:
        abort(400)
    if "/" in filename or "\\" in filename:
        abort(400)
    if os.path.basename(filename) != filename:
        abort(400)
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    if not project:
        abort(404)
    cfg = load_config()
    root = cfg.get("drive_projects_path", "")
    drive_folder = folder_name(project)
    project_folder = os.path.join(root, drive_folder) if root else None
    if not project_folder or not os.path.isdir(project_folder):
        abort(404)
    file_path = os.path.join(project_folder, filename)
    if not os.path.isfile(file_path):
        abort(404)
    as_attachment = request.args.get("dl") == "1"
    return send_from_directory(project_folder, filename, as_attachment=as_attachment)


@bp.route("/shutdown", methods=["POST"], endpoint="shutdown")
def shutdown():
    def stop_process():
        time.sleep(0.4)
        os._exit(0)

    threading.Thread(target=stop_process, daemon=True).start()
    return """<!doctype html><html><head><meta charset="utf-8">
    <title>Cerrando…</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/bootstrap-icons/1.11.3/font/bootstrap-icons.min.css">
    <style>
      body { margin:0; background:#060a14; color:#8a96ae;
             display:flex; align-items:center; justify-content:center; height:100vh;
             font-family:'Inconsolata',monospace; }
      .icon { font-size:2.8rem; color:#4a5060; }
      h5    { margin:.9rem 0 .35rem; font-size:1rem; color:#c0c8d8; font-weight:600; }
      p     { font-size:.88rem; color:#606878; margin:0; }
    </style>
    </head><body>
    <div style="text-align:center">
      <i class="bi bi-power icon"></i>
      <h5>Servidor detenido</h5>
      <p>Puedes cerrar esta ventana.</p>
    </div>
    </body></html>"""
