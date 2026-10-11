"""Authorization for routes and project-scoped documents, including legacy URLs."""
from flask import abort, current_app, flash, redirect, request, url_for
from flask_login import current_user

from .auth import user_has_permission


def can(permission):
    return current_app.config.get("LOGIN_DISABLED", False) or user_has_permission(current_user, permission)


PROJECT_EDITS = {
    "new_project", "update_project", "update_project_status", "close_project",
    "reopen_project", "update_stage_budget",
}
TASK_EDITS = {
    "update_stage_status", "toggle_doc_checklist", "add_doc_checklist", "delete_doc_checklist",
}
QUOTE_READS = {
    "all_quotes", "all_payments", "view_quote", "quote_pdf", "quote_excel",
    "quote_resumen", "quote_resumen_pdf", "quote_resumen_excel", "quote_csv_export",
    "audit_deleted_catalog",
}
DOWNLOADS = {
    "quote_pdf", "quote_excel", "quote_resumen_pdf", "quote_resumen_excel",
    "quote_csv_export", "ldm_pdf", "ldm_csv", "project_progress_pdf", "mobile_generate_pdf",
}
UPLOADS = {"import_quote_csv", "import_ldm_csv", "import_ldm_pdf_upload", "import_ldm_pdf_map", "import_ldm_pdf_create"}


def required_permissions(endpoint, method):
    """Six user switches map to server-side operations, independent of the UI."""
    blueprint, _, name = endpoint.rpartition(".")
    permissions = set()
    if name in PROJECT_EDITS:
        permissions.add("edit_projects")
    if name in TASK_EDITS or name == "delete_delivery":
        permissions.add("manage_tasks")
    if name == "api_catalogo_impact":
        permissions.add("view_quotes")
    if blueprint == "admin_bp" and method == "POST" and (
        "catalogo" in name or "bundle" in name or name == "migrate_catalog_marca"
    ):
        permissions.add("edit_quotes")
    if name == "project_templates_admin" and method == "POST":
        permissions.update({"edit_projects", "manage_tasks"})
    if name == "alcances_api_save":
        permissions.add("edit_projects")
    if name == "disciplinas_api_save":
        permissions.add("edit_quotes")
    if blueprint in {"quotes_bp", "quotes_mobile_bp", "materials_bp"}:
        permissions.add("view_quotes")
        if method not in {"GET", "HEAD", "OPTIONS"} or (
            blueprint == "quotes_bp" and name not in QUOTE_READS
        ) or (blueprint == "materials_bp" and name not in {"ldm_pdf", "ldm_csv"}) or (
            blueprint == "quotes_mobile_bp" and name != "mobile_projects"
        ):
            permissions.add("edit_quotes")
    if name in DOWNLOADS:
        permissions.add("download_files")
    if name in UPLOADS or (name in {"fichas", "link_ficha", "unlink_ficha", "delete_ficha"} and method == "POST"):
        permissions.add("upload_files")
    if name == "import_json":
        permissions.add("upload_files")
        if method == "POST":
            for key in request.files:
                if key in {"quotes", "materiales", "catalogo", "bundles"}:
                    permissions.update({"view_quotes", "edit_quotes"})
                elif key == "tasks":
                    permissions.add("manage_tasks")
                elif key in {"projects", "deliveries", "team"}:
                    permissions.add("edit_projects")
    return permissions


def check_access():
    endpoint = request.endpoint or ""
    if any(not can(p) for p in required_permissions(endpoint, request.method)):
        abort(403, description="No tienes permiso para realizar esta acción.")


def check_document_access(load):
    # Validate ownership once for ALL actions on a scoped document, including
    # exports, approval, item repair, and deletion.
    args = request.view_args or {}
    project_id = args.get("project_id")
    if project_id:
        for id_key, collection in (("quote_id", "quotes"), ("ldm_id", "materiales")):
            if id_key not in args:
                continue
            belongs = any(item.get("id") == args[id_key] and item.get("project_id") == project_id
                          for item in load(collection))
            project_exists = any(item.get("id") == project_id for item in load("projects"))
            if not belongs or not project_exists:
                label = "Cotización" if id_key == "quote_id" else "Lista"
                flash(f"{label} no encontrada en este proyecto.", "danger")
                return redirect(url_for("dashboard"))
