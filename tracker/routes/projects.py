import os
import threading
import time
import zipfile
from datetime import date

from flask import Blueprint, abort, flash, redirect, render_template, request, send_from_directory, url_for

from ..catalog import catalog_maps, hydrate_ldm, hydrate_quote
from ..consistency import compute_consistency
from ..deletions import delete_project_data
from ..domain import ALCANCES, get_progress
from ..drive import active_drive_paths, create_project_folder, current_platform_key, find_delivery_files, folder_name, load_config, save_config, scan_drive_folder
from ..project_view import build_project_detail_context
from ..services import (
    apply_task_status_change,
    create_project_with_tasks,
    sync_project_alcances,
    update_observation_details,
    update_observation_checklist_item,
)
from ..storage import load, new_id, save, today
from ..validators import validate_project_form

bp = Blueprint("projects_bp", __name__)


def _blank_project_form_state():
    return {
        "fields": {
            "name": "",
            "client": "",
            "clave": "",
            "version": "V1",
            "fecha": "",
            "notes": "",
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
    bundles = load("bundles")
    comparison_rules = load("comparison_rules")
    comparison_ignored_items = load("comparison_ignored_items")
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
            bundles=bundles,
            comparison_rules=comparison_rules,
            comparison_ignored_items=comparison_ignored_items,
        )

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
        projects.append(project)
        save("projects", projects)
        save("tasks", tasks)
        # ── Crear carpeta en Drive automáticamente ──────────────────────────
        try:
            cfg = load_config()
            drive_root = active_drive_paths(cfg)["projects"]
            if drive_root and os.path.isdir(drive_root):
                new_folder = os.path.join(drive_root, folder_name(project))
                if not os.path.exists(new_folder):
                    os.makedirs(new_folder, exist_ok=True)
                    flash(
                        f"Carpeta creada en Drive: {folder_name(project)}",
                        "info",
                    )
                else:
                    flash(
                        f"La carpeta {folder_name(project)} ya existía en Drive.",
                        "info",
                    )
        except Exception as drive_exc:
            flash(f"Proyecto creado, pero no se pudo crear la carpeta en Drive: {drive_exc}", "warning")
        # ───────────────────────────────────────────────────────────────────
        flash(f"Proyecto '{project['name']}' creado con {len(selected)} alcance(s).", "success")
        return redirect(url_for("project_detail", project_id=project["id"]))
    return render_template("project_new.html", form_state=_blank_project_form_state())


@bp.route("/projects/<project_id>", endpoint="project_detail")
def project_detail(project_id):
    projects = load("projects")
    project = next((item for item in projects if item["id"] == project_id), None)
    if not project:
        flash("Proyecto no encontrado.", "danger")
        return redirect(url_for("dashboard"))
    return render_template("project_detail.html", **build_project_detail_context(project))


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


@bp.route("/settings", methods=["GET", "POST"], endpoint="settings")
def settings():
    cfg = load_config()
    platform_key = current_platform_key()
    if request.method == "POST":
        submitted_cfg = dict(cfg)
        projects_key = f"drive_projects_path_{platform_key}"
        fichas_key = f"drive_fichas_path_{platform_key}"
        submitted = {
            "drive_projects_path": request.form.get("drive_projects_path", "").strip(),
            "drive_fichas_path": request.form.get("drive_fichas_path", "").strip(),
        }
        submitted_cfg[projects_key] = submitted["drive_projects_path"]
        submitted_cfg[fichas_key] = submitted["drive_fichas_path"]
        if not submitted_cfg.get("drive_projects_path"):
            submitted_cfg["drive_projects_path"] = submitted["drive_projects_path"]
        if not submitted_cfg.get("drive_fichas_path"):
            submitted_cfg["drive_fichas_path"] = submitted["drive_fichas_path"]
        field_errors = {}
        if submitted["drive_projects_path"] and not os.path.isdir(submitted["drive_projects_path"]):
            field_errors["drive_projects_path"] = "La ruta de proyectos no existe en este equipo."
        if submitted["drive_fichas_path"] and not os.path.isdir(submitted["drive_fichas_path"]):
            field_errors["drive_fichas_path"] = "La ruta de fichas técnicas no existe en este equipo."
        if field_errors:
            for error in field_errors.values():
                flash(error, "warning")
            view_cfg = _settings_view_config(submitted_cfg)
            path_status = {
                "projects_ok": False,
                "projects_set": bool(submitted["drive_projects_path"]),
                "fichas_ok": False,
                "fichas_set": bool(submitted["drive_fichas_path"]),
            }
            return render_template("settings.html", cfg=view_cfg, field_errors=field_errors, path_status=path_status)
        save_config(submitted_cfg)
        flash("Configuración guardada.", "success")
        return redirect(url_for("settings"))
    view_cfg = _settings_view_config(cfg)
    path_status = {
        "projects_ok": bool(view_cfg["drive_projects_path"]) and os.path.isdir(view_cfg["drive_projects_path"]),
        "projects_set": bool(view_cfg["drive_projects_path"]),
        "fichas_ok": bool(view_cfg["drive_fichas_path"]) and os.path.isdir(view_cfg["drive_fichas_path"]),
        "fichas_set": bool(view_cfg["drive_fichas_path"]),
    }
    return render_template("settings.html", cfg=view_cfg, field_errors={}, path_status=path_status)


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
    drive_paths = active_drive_paths(cfg)
    projects_root = drive_paths["projects"]
    fichas_root = drive_paths["fichas"]
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


@bp.route("/projects/<project_id>/drive/create-folder", methods=["POST"], endpoint="create_drive_folder")
def create_drive_folder(project_id):
    """Crea la carpeta Drive del proyecto si aún no existe."""
    project = next((item for item in load("projects") if item["id"] == project_id), None)
    if not project:
        return redirect(url_for("dashboard"))
    cfg = load_config()
    drive_root = active_drive_paths(cfg)["projects"]
    fn = folder_name(project)
    created, error = create_project_folder(fn, drive_root)
    if error:
        flash(error, "danger")
    elif created:
        flash(f"Carpeta creada en Drive: {fn}", "success")
    else:
        flash(f"La carpeta {fn} ya existe en Drive.", "info")
    return redirect(url_for("project_detail", project_id=project_id) + "#tab-drive")


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
    root = active_drive_paths(cfg)["projects"]
    drive_folder = folder_name(project)
    project_folder = os.path.join(root, drive_folder) if root else None
    if not project_folder or not os.path.isdir(project_folder):
        abort(404)
    file_path = os.path.join(project_folder, filename)
    if not os.path.isfile(file_path):
        abort(404)
    as_attachment = request.args.get("dl") == "1"
    return send_from_directory(project_folder, filename, as_attachment=as_attachment)


def _settings_view_config(cfg):
    drive_paths = active_drive_paths(cfg)
    view_cfg = dict(cfg)
    view_cfg["current_platform"] = drive_paths["platform"]
    view_cfg["current_platform_label"] = drive_paths["platform_label"]
    view_cfg["drive_projects_path"] = drive_paths["projects"]
    view_cfg["drive_fichas_path"] = drive_paths["fichas"]
    return view_cfg


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
