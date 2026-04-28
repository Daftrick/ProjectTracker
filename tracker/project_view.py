from datetime import date

from .catalog import catalog_maps, hydrate_ldm, hydrate_quote
from .consistency import compute_consistency
from .domain import check_blocked, get_progress
from .drive import find_delivery_files, folder_name, load_config, scan_drive_folder
from .storage import load, today


def build_project_detail_context(project):
    project_id = project["id"]
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
        [
            hydrate_quote(quote, catalog_by_id, catalog_by_name)
            for quote in load("quotes")
            if quote["project_id"] == project_id
        ],
        key=lambda item: item.get("created_at", ""),
        reverse=True,
    )
    ldms = sorted(
        [
            hydrate_ldm(ldm, catalog_by_id, catalog_by_name)
            for ldm in load("materiales")
            if ldm["project_id"] == project_id
        ],
        key=lambda item: item.get("seq", 0),
    )

    all_fichas = load("fichas")
    linked_fichas = [ficha for ficha in all_fichas if project_id in ficha.get("projects", [])]
    unlinked_fichas = [ficha for ficha in all_fichas if project_id not in ficha.get("projects", [])]

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
        linked_fichas,
    )

    # Totales globales (incluyen todas las cotizaciones e IVA) para el header del proyecto.
    total_cotizado = round(sum(quote.get("total", 0) for quote in quotes), 2)
    costo_proveedor = round(sum(ldm.get("subtotal_cot", 0) for ldm in ldms), 2)
    margen = round(total_cotizado - costo_proveedor, 2)

    # Reporte de consistencia: compara la cotización General activa contra el
    # costo de proveedor agregado por catalog_item_id.
    consistency = compute_consistency(project, quotes, ldms, catalog_by_id)

    return {
        "project": project,
        "main_tasks": main_tasks,
        "subtasks": subtasks,
        "delete_preview": {
            "tasks": len(project_tasks),
            "deliveries": len(deliveries),
            "quotes": len(quotes),
            "ldms": len(ldms),
            "linked_fichas": len(linked_fichas),
        },
        "deliveries": deliveries,
        "scan": scan,
        "available": available,
        "quotes": quotes,
        "ldms": ldms,
        "linked_fichas": linked_fichas,
        "unlinked_fichas": unlinked_fichas,
        "prog": progress,
        "can_close": can_close,
        "team": load("team"),
        "today": today(),
        "today_short": date.today().strftime("%y%m%d"),
        "folder_name": drive_folder,
        "file_ie": f"IE-{project['clave']}-{project['version']}-{project['fecha']}",
        "file_xref": f"XREF-{project['clave']}-{project['version']}-{project['fecha']}",
        "total_cotizado": total_cotizado,
        "costo_proveedor": costo_proveedor,
        "margen": margen,
        "consistency": consistency,
    }
