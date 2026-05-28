from datetime import date

from .catalog import catalog_maps, hydrate_ldm, hydrate_quote
from .consistency import compute_consistency
from .domain import check_blocked, get_progress
from .drive import active_drive_paths, find_delivery_files, folder_name, load_config, scan_drive_folder
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
ISSUE_COLOR_MAP = {
    "below_cost": "danger",
    "missing_in_ldm": "danger",
    "missing_in_cot": "secondary",
    "qty_mismatch": "warning",
    "low_margin": "warning",
}
TECH_ISSUE_LABEL_MAP = {
    "ok": "OK",
    "missing_in_ldm": "Faltante en LDM",
    "extra_in_ldm": "Extra en LDM",
    "qty_shortage": "Cantidad insuficiente",
    "qty_excess": "Excedente",
}
TECH_ISSUE_COLOR_MAP = {
    "ok": "success",
    "missing_in_ldm": "danger",
    "extra_in_ldm": "warning",
    "qty_shortage": "danger",
    "qty_excess": "warning",
}
TECH_ACTION_MAP = {
    "missing_in_ldm": "Agregar material en la LDM del proyecto.",
    "extra_in_ldm": "Verificar origen; si no corresponde a este proyecto, marcar como ignorado técnico.",
    "qty_shortage": "Aumentar cantidad en LDM o ajustar la regla de conversión COT/LDM.",
    "qty_excess": "Revisar excedente: ajustar regla de conversión o revisar el bundle.",
    "ok": "",
}
TECH_STATUS_LABELS = {
    "ok": "Materiales consistentes",
    "warning": "Revisar diferencias",
    "critical": "Faltantes críticos",
    "no_data": "Sin datos técnicos",
}


def _as_float(value, default=0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _status_color(status):
    return STATUS_COLOR_MAP.get(status or "no_data", "secondary")


def _status_icon(status):
    return STATUS_ICON_MAP.get(status or "no_data", "info-circle")


def _csv_importable_files(scan):
    return [
        csv_file
        for csv_file in (scan or {}).get("csv_plano", [])
        if not csv_file.get("linked_ldm")
    ]


def _deleted_catalog_items(record):
    return [
        item
        for item in (record or {}).get("items", [])
        if item.get("catalog_deleted")
    ]


def _filename_extension(name):
    parts = (name or "").rsplit(".", 1)
    return f".{parts[1].lower()}" if len(parts) > 1 else ""


def _drive_file_view(file_info, color_class):
    view = dict(file_info or {})
    view["display_class"] = color_class
    return view


def _ie_file_color(file_info):
    if not file_info.get("highlight"):
        return "drive-code-muted"
    ext = _filename_extension(file_info.get("name", ""))
    if ext == ".pdf":
        return "drive-code-ie-pdf"
    if ext == ".dwg":
        return "drive-code-ie-dwg"
    return "drive-code-ie"


def build_drive_scan_view(scan):
    view = dict(scan or {})
    view["ie_files"] = [_drive_file_view(file, _ie_file_color(file)) for file in view.get("ie_files", [])]
    view["mem_files"] = [
        _drive_file_view(file, "drive-code-mem" if file.get("highlight") else "drive-code-muted")
        for file in view.get("mem_files", [])
    ]
    view["ldm_files"] = [_drive_file_view(file, "drive-code-ldm") for file in view.get("ldm_files", [])]
    view["provider_quote_files"] = [
        _drive_file_view(file, "drive-code-prov" if file.get("linked") else "drive-code-muted")
        for file in view.get("provider_quote_files", [])
    ]
    view["csv_plano"] = [
        _drive_file_view(
            file,
            "drive-code-cot"
            if file.get("status") == "importado"
            else "drive-code-prov"
            if file.get("status") == "desactualizado"
            else "drive-code-muted",
        )
        for file in view.get("csv_plano", [])
    ]
    view["cot_files"] = [_drive_file_view(file, "drive-code-cot") for file in view.get("cot_files", [])]
    view["work_files"] = [
        _drive_file_view(file, "drive-code-work" if file.get("highlight") else "drive-code-muted")
        for file in view.get("work_files", [])
    ]
    view["other_files"] = [_drive_file_view(file, "drive-code-muted") for file in view.get("other_files", [])]
    view["has_ldm_documents"] = bool(view.get("ldm_files") or view.get("provider_quote_files"))
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
    rows = []
    for quote in quotes or []:
        items = quote.get("items", []) or []
        deleted_catalog_items = _deleted_catalog_items(quote)
        rows.append({
            "quote": quote,
            "items": items,
            "item_count": len(items),
            "deleted_catalog_items": deleted_catalog_items,
            "deleted_catalog_count": len(deleted_catalog_items),
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


def _row_class(status):
    if status == "critical":
        return "table-danger"
    if status == "warning":
        return "table-warning"
    return ""


def _technical_search_text(row):
    expected_sources = row.get("sources_expected", []) or []
    actual_sources = row.get("sources_actual", []) or []
    return " ".join(
        [
            str(row.get("nombre", "")),
            str(row.get("unidad", "")),
            str(row.get("issue", "")),
            str(row.get("comparison_rule_id", "")),
            " ".join(str(src.get("bundle_name", "")) for src in expected_sources),
            " ".join(str(src.get("ldm_number", "")) for src in actual_sources),
        ]
    )


def _technical_row_view(row):
    row = row or {}
    status = row.get("status") or "no_data"
    issue = row.get("issue") or ""
    sources_expected = row.get("sources_expected", []) or []
    sources_actual = row.get("sources_actual", []) or []
    color = _status_color(status)
    issue_color = TECH_ISSUE_COLOR_MAP.get(issue, color)
    return {
        "row": row,
        "catalog_item_id": row.get("catalog_item_id", ""),
        "status": status,
        "issue": issue,
        "diff_qty": _as_float(row.get("diff_qty")),
        "color": color,
        "icon": _status_icon(status),
        "issue_label": TECH_ISSUE_LABEL_MAP.get(issue, issue),
        "issue_color": issue_color,
        "action": TECH_ACTION_MAP.get(issue, ""),
        "row_class": _row_class(status),
        "sources_expected_preview": sources_expected[:2],
        "sources_expected_more_count": max(len(sources_expected) - 2, 0),
        "sources_actual_preview": sources_actual[:2],
        "sources_actual_more_count": max(len(sources_actual) - 2, 0),
        "search_text": _technical_search_text(row),
    }


def _bundle_component_view(component, matching_row):
    component = component or {}
    matching_row = matching_row or _technical_row_view({})
    status = matching_row["status"]
    issue = matching_row["issue"]
    color = matching_row["color"]
    return {
        "component": component,
        "matching": matching_row,
        "status": status,
        "issue": issue,
        "actual_qty": _as_float(matching_row["row"].get("actual_qty")),
        "diff_qty": matching_row["diff_qty"],
        "expected_qty": _as_float(component.get("expected_qty")),
        "color": color,
        "icon": matching_row["icon"],
        "issue_label": TECH_ISSUE_LABEL_MAP.get(issue, issue),
        "issue_color": TECH_ISSUE_COLOR_MAP.get(issue, color),
        "action": TECH_ACTION_MAP.get(issue, ""),
        "row_class": _row_class(status),
    }


def _commercial_issue_views(issue_details):
    views = []
    for detail in issue_details or []:
        if isinstance(detail, dict):
            issue_key = detail.get("issue", "unknown")
            issue_label = detail.get("label", issue_key)
        else:
            issue_key = getattr(detail, "issue", "unknown")
            issue_label = getattr(detail, "label", issue_key)
        views.append({
            "key": issue_key,
            "label": issue_label,
            "color": ISSUE_COLOR_MAP.get(issue_key, "secondary"),
        })
    return views


def _primary_action_text(primary_action):
    if isinstance(primary_action, dict):
        return primary_action.get("text", "")
    return getattr(primary_action, "text", "")


def _suggested_action_views(actions):
    views = []
    for action in actions or []:
        view = dict(action)
        view["color"] = _status_color(view.get("status"))
        views.append(view)
    return views


def _commercial_row_view(row):
    row = row or {}
    status = row.get("status", "no_data")
    issues = row.get("issues", []) or []
    ldm_numbers = row.get("ldm_numbers", []) or []
    return {
        "row": row,
        "status": status,
        "color": _status_color(status),
        "icon": _status_icon(status),
        "issues": issues,
        "ldm_numbers": ldm_numbers,
        "qty_delta": row.get("qty_delta", 0) or 0,
        "qty_cot": row.get("qty_cot"),
        "qty_ldm": row.get("qty_ldm"),
        "price_cot": row.get("price_cot"),
        "cost_avg": row.get("cost_avg"),
        "margin_unit": row.get("margin_unit"),
        "margin_unit_pct": row.get("margin_unit_pct"),
        "issue_details": _commercial_issue_views(row.get("issue_details", []) or []),
        "primary_action_text": _primary_action_text(row.get("primary_action")),
        "row_class": _row_class(status),
        "search_text": " ".join([
            str(row.get("nombre", "Sin nombre")),
            str(row.get("categoria", "")),
            " ".join(str(issue) for issue in issues),
            " ".join(str(ldm_number) for ldm_number in ldm_numbers),
        ]),
    }


def build_consistency_view(consistency):
    cn = consistency or {}
    status = cn.get("status", "no_data")
    ignored = cn.get("ignored") or {}
    tech = cn.get("bundle_consistency") or {}
    tech_status = tech.get("status") or "no_data"
    tech_invalid_components = tech.get("invalid_components", []) or []
    tech_rows = [_technical_row_view(row) for row in tech.get("rows", []) or []]
    tech_rows_by_catalog = {row["catalog_item_id"]: row for row in tech_rows}
    bundle_rows_by_quote_item = {}
    for bundle_row in tech.get("bundle_rows", []) or []:
        bundle_rows_by_quote_item.setdefault(bundle_row.get("bundle_catalog_item_id"), []).append(bundle_row)

    bundle_quote_items = []
    for quote_item in tech.get("bundle_quote_items", []) or []:
        components = [
            _bundle_component_view(
                bundle_row,
                tech_rows_by_catalog.get(bundle_row.get("component_catalog_item_id")),
            )
            for bundle_row in bundle_rows_by_quote_item.get(quote_item.get("catalog_item_id"), [])
        ]
        if components:
            item = dict(quote_item)
            item["components"] = components
            bundle_quote_items.append(item)

    return {
        "raw": cn,
        "status_color_map": STATUS_COLOR_MAP,
        "status_icon_map": STATUS_ICON_MAP,
        "issue_color_map": ISSUE_COLOR_MAP,
        "badge_color": _status_color(status),
        "badge_icon": _status_icon(status),
        "tab_severity": "critical"
        if status == "critical" or tech_status == "critical"
        else "warning"
        if status == "warning" or tech_status == "warning"
        else "",
        "commercial_rows": [_commercial_row_view(row) for row in cn.get("items", []) or []],
        "suggested_actions": _suggested_action_views(cn.get("suggested_actions")),
        "ignored_quote": ignored.get("commercial_quote") or {"count": 0, "total": 0, "rows": []},
        "ignored_ldm": ignored.get("commercial_ldm") or {"count": 0, "total": 0, "rows": []},
        "technical": {
            "raw": tech,
            "status": tech_status,
            "status_label": TECH_STATUS_LABELS.get(tech_status, "Sin datos técnicos"),
            "summary": tech.get("summary") or {},
            "rows": tech_rows,
            "ldm_unlinked": tech.get("ldm_unlinked") or {"count": 0, "total": 0},
            "bundle_quote_items": bundle_quote_items,
            "unmapped_quote_items": tech.get("unmapped_quote_items") or [],
            "invalid_components": tech_invalid_components,
            "bundles_no_active_version": tech.get("bundles_no_active_version") or [],
            "components_no_rule": tech.get("components_no_rule") or [],
            "technical_suggested_actions": _suggested_action_views(tech.get("technical_suggested_actions")),
            "ignored_expected": tech.get("ignored_expected") or {"count": 0, "qty": 0, "rows": []},
            "ignored_actual": tech.get("ignored_actual") or {"count": 0, "qty": 0, "rows": []},
            "other_invalid_components": [
                item
                for item in tech_invalid_components
                if item.get("reason") != "bundle_without_active_version"
            ],
            "color": _status_color(tech_status),
            "icon": _status_icon(tech_status),
        },
    }


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
    drive_paths = active_drive_paths(cfg)
    drive_folder = folder_name(project)
    scan = build_drive_scan_view(
        scan_drive_folder(drive_folder, drive_paths["projects"], ldms, clave=project["clave"])
    )
    available = find_delivery_files(
        drive_folder,
        project["clave"],
        project.get("version", "V1"),
        project.get("fecha", ""),
        drive_paths["projects"],
        drive_paths["fichas"],
        linked_fichas,
    )

    # Totales globales (incluyen todas las cotizaciones e IVA) para el header del proyecto.
    total_cotizado = round(sum(quote.get("total", 0) for quote in quotes), 2)
    costo_proveedor = round(sum(ldm.get("subtotal_cot", 0) for ldm in ldms), 2)
    margen = round(total_cotizado - costo_proveedor, 2)

    # Reporte de consistencia: compara la cotización General activa contra el
    # costo de proveedor agregado por catalog_item_id.
    consistency = compute_consistency(
        project,
        quotes,
        ldms,
        catalog_by_id,
        bundles=load("bundles"),
        comparison_rules=load("comparison_rules"),
        comparison_ignored_items=load("comparison_ignored_items"),
    )

    # Nombres reales de los archivos DWG más recientes en Drive.
    # Se prefiere el archivo marcado como highlight (última versión detectada por
    # decorate_latest) para mostrar el nombre exacto en las tarjetas del header.
    # Si Drive no está disponible o no hay archivos, se cae al nombre canónico
    # construido con los metadatos del proyecto.
    def _latest_scan_name(scan_files, fallback):
        """Devuelve el nombre del archivo con highlight=True, o el fallback."""
        for f in scan_files or []:
            if f.get("highlight"):
                return f["name"]
        # Si sólo hay un archivo (sin versión parseable), usarlo igual
        if len(scan_files or []) == 1:
            return scan_files[0]["name"]
        return fallback

    _ie_fallback = f"IE-{project['clave']}-{project['version']}-{project['fecha']}.dwg"
    _xref_fallback = f"XREF-{project['clave']}-{project['version']}-{project['fecha']}.dwg"

    # Filtramos sólo DWGs para las tarjetas (excluye PDFs del grupo IE)
    ie_dwg_files = [f for f in scan.get("ie_files", []) if f["name"].lower().endswith(".dwg")]
    xref_dwg_files = [f for f in scan.get("work_files", []) if f["name"].lower().endswith(".dwg")]

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
        "scan": scan,
        "importable_csvs": _csv_importable_files(scan),
        "available": available,
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
        "file_ie": _latest_scan_name(ie_dwg_files, _ie_fallback),
        "file_xref": _latest_scan_name(xref_dwg_files, _xref_fallback),
        "total_cotizado": total_cotizado,
        "costo_proveedor": costo_proveedor,
        "margen": margen,
        "consistency": consistency,
        "consistency_view": build_consistency_view(consistency),
    }
