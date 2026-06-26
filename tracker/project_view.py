from datetime import date

from .catalog import catalog_maps, hydrate_ldm, hydrate_quote
from .catalog import APPROVAL_ACTIVE, is_base_quote_type
from .consistency import compute_consistency, pick_active_quote
from .domain import check_blocked, get_progress
from .utils import folder_name
from .storage import load, today


STATUS_COLOR_MAP = {
    "ok": "success",
    "warning": "warning",
    "critical": "danger",
    "no_data": "secondary",
}
STATUS_ICON_MAP = {
    "ok": "check-circle-fill",
    "warning": "exclamation-triangle-fill",
    "critical": "x-octagon-fill",
    "no_data": "info-circle",
}
def _status_color(status):
    return STATUS_COLOR_MAP.get(status or "no_data", "secondary")


def _status_icon(status):
    return STATUS_ICON_MAP.get(status or "no_data", "info-circle")



def _deleted_catalog_items(record):
    return [
        item
        for item in (record or {}).get("items", [])
        if item.get("catalog_deleted")
    ]


def _filename_extension(name):
    parts = (name or "").rsplit(".", 1)
    return f".{parts[1].lower()}" if len(parts) > 1 else ""


    return view


def build_ldm_row_views(ldms):
    rows = []
    for ldm in ldms or []:
        items = ldm.get("items", []) or []
        deleted_catalog_items = _deleted_catalog_items(ldm)
        rows.append({
            "ldm": ldm,
            "items": items,
            "item_count": len(items),
            "deleted_catalog_items": deleted_catalog_items,
            "deleted_catalog_count": len(deleted_catalog_items),
        })
    return rows


def build_quote_row_views(quotes):
    from .catalog import (
        APPROVAL_ACTIVE, APPROVAL_DRAFT, APPROVAL_OBSOLETE,
        is_base_quote_type,
    )
    rows = []
    for quote in quotes or []:
        items = quote.get("items", []) or []
        deleted_catalog_items = _deleted_catalog_items(quote)
        approval = quote.get("approval_status", APPROVAL_DRAFT)
        is_extra = not is_base_quote_type(quote.get("quote_type"))

        # Badge visual
        if approval == APPROVAL_ACTIVE:
            approval_badge = "success"
            approval_label = "Aprobada" if not is_extra else "Activa"
            approval_icon  = "check-circle"
        elif approval == APPROVAL_OBSOLETE:
            approval_badge = "secondary"
            approval_label = "Obsoleta" if not is_extra else "Inactiva"
            approval_icon  = "slash-circle"
        else:  # draft
            approval_badge = "warning"
            approval_label = "Borrador"
            approval_icon  = "pencil-square"

        rows.append({
            "quote": quote,
            "items": items,
            "item_count": len(items),
            "deleted_catalog_items": deleted_catalog_items,
            "deleted_catalog_count": len(deleted_catalog_items),
            "approval": approval,
            "approval_badge": approval_badge,
            "approval_label": approval_label,
            "approval_icon": approval_icon,
            "is_extra": is_extra,
        })
    return rows


def _observation_view(observation):
    checklist = observation.get("checklist", []) or []
    return {
        "task": observation,
        "checklist": checklist,
        "checklist_text": "\n".join(item.get("text", "") for item in checklist),
        "done_count": sum(1 for item in checklist if item.get("done")),
        "checklist_count": len(checklist),
    }


def build_task_row_views(main_tasks, subtasks):
    rows = []
    for task in main_tasks or []:
        task_subtasks = (subtasks or {}).get(task.get("id"), []) or []
        rows.append({
            "task": task,
            "blocked": bool(task.get("_blocked") and task.get("status") == "Pendiente"),
            "source": task.get("source") or "propia",
            "info_status": task.get("info_status") or "Pendiente",
            "last_history": task.get("history", [])[-1] if task.get("history") else None,
            "active_observations": [
                _observation_view(subtask)
                for subtask in task_subtasks
                if subtask.get("status") != "Aprobado"
            ],
            "has_detail": bool(task.get("history") or task_subtasks),
        })
    return rows


def build_consistency_view(consistency):
    cn = consistency or {}
    status = cn.get("status", "no_data")
    coverage = cn.get("coverage") or {}
    quote_coverage = coverage.get("quote_catalog_coverage_pct")
    ldm_coverage = coverage.get("ldm_catalog_coverage_pct")
    return {
        "raw": cn,
        "badge_color": _status_color(status),
        "badge_icon": _status_icon(status),
        "visual_warnings": cn.get("visual_warnings") or [],
        "has_visual_warnings": bool(cn.get("visual_warnings")),
        "quote_coverage_color": _coverage_color(quote_coverage),
        "ldm_coverage_color": _coverage_color(ldm_coverage),
        "has_unlinked_rows": bool(
            (cn.get("quote_unlinked") or {}).get("count")
            or (cn.get("ldm_unlinked") or {}).get("count")
        ),
    }


def _coverage_color(value):
    if value is None:
        return "secondary"
    if value < 80:
        return "warning"
    return "success"


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

    drive_folder = folder_name(project)

    # Totales para el header del proyecto.
    # Se suma: la cotización base aprobada (General/Preliminar con approval_status='active')
    # más todas las Extraordinarias con approval_status='active'.
    # Fallback: si ninguna tiene estado explícito se comporta igual que antes (suma todo).
    _active_base = pick_active_quote(quotes)
    _active_extras = [
        q for q in quotes
        if not is_base_quote_type(q.get("quote_type"))
        and q.get("approval_status", APPROVAL_ACTIVE) == APPROVAL_ACTIVE
    ]
    if _active_base is not None:
        total_cotizado = round(
            _active_base.get("total", 0) + sum(q.get("total", 0) for q in _active_extras), 2
        )
    else:
        total_cotizado = round(sum(q.get("total", 0) for q in _active_extras), 2)
    costo_proveedor = round(sum(ldm.get("subtotal_cot", 0) for ldm in ldms), 2)
    margen = round(total_cotizado - costo_proveedor, 2)

    # Reporte de consistencia: compara la cotización General activa contra el
    # costo de proveedor agregado por catalog_item_id.
    consistency = compute_consistency(
        project,
        quotes,
        ldms,
        catalog_by_id,
    )

    _ie_fallback = f"IE-{project['clave']}-{project['version']}-{project['fecha']}.dwg"
    _xref_fallback = f"XREF-{project['clave']}-{project['version']}-{project['fecha']}.dwg"

    return {
        "project": project,
        "main_tasks": main_tasks,
        "task_rows": build_task_row_views(main_tasks, subtasks),
        "subtasks": subtasks,
        "delete_preview": {
            "tasks": len(project_tasks),
            "deliveries": len(deliveries),
            "quotes": len(quotes),
            "ldms": len(ldms),
            "linked_fichas": len(linked_fichas),
        },
        "deliveries": deliveries,
        "quotes": quotes,
        "quote_rows": build_quote_row_views(quotes),
        "ldms": ldms,
        "ldm_rows": build_ldm_row_views(ldms),
        "linked_fichas": linked_fichas,
        "unlinked_fichas": unlinked_fichas,
        "prog": progress,
        "can_close": can_close,
        "team": load("team"),
        "today": today(),
        "today_short": date.today().strftime("%y%m%d"),
        "folder_name": drive_folder,
        "file_ie": _ie_fallback,
        "file_xref": _xref_fallback,
        "active_base_quote": _active_base,
        "active_extras_count": len(_active_extras),
        "total_cotizado": total_cotizado,
        "costo_proveedor": costo_proveedor,
        "margen": margen,
        "consistency": consistency,
        "consistency_view": build_consistency_view(consistency),
    }
