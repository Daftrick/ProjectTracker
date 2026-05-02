"""Consistencia entre cotización (COT) y listas de materiales (LDM).

Compara, por proyecto, los artículos cotizados al cliente contra los
artículos costeados con proveedores. Funciones puras (sin I/O) que pueden
combinarse para vistas: dashboard, detalle de proyecto, banners en formularios.

Reglas de comparación:
    - Cotización activa = la cotización General más reciente del proyecto.
      Si no hay General, se usa la más reciente de cualquier tipo.
    - Costo proveedor = suma de subtotales de todas las LDMs del proyecto.
    - Comparación por artículo: se agrega por `catalog_item_id`. Los items
      sin enlace al catálogo se contabilizan en `unlinked_*` para alertar.
    - Margen % = (cotizado - costo) / cotizado * 100. Si cotizado == 0 → None.
    - Auditoría por artículo: detecta faltantes, diferencias de cantidad,
      venta bajo costo y margen unitario bajo.
"""

from __future__ import annotations

from typing import Iterable

from .catalog import quote_type_key

MARGIN_OK_PCT = 30.0
LOW_ITEM_MARGIN_PCT = 30.0
QTY_TOLERANCE = 0.01  # diferencias menores se consideran iguales (redondeos)

STATUS_OK = "ok"
STATUS_WARNING = "warning"
STATUS_CRITICAL = "critical"
STATUS_NO_DATA = "no_data"

STATUS_LABELS = {
    STATUS_OK: "Consistente",
    STATUS_WARNING: "Revisar margen",
    STATUS_CRITICAL: "Crítico",
    STATUS_NO_DATA: "Sin datos",
}

ISSUE_LABELS = {
    "missing_in_ldm": "Sin LDM",
    "missing_in_cot": "Sin COT",
    "qty_mismatch": "Cantidad diferente",
    "below_cost": "Debajo de costo",
    "low_margin": "Margen bajo",
}

ISSUE_ACTIONS = {
    "missing_in_ldm": "Agregar a LDM o confirmar que no requiere compra.",
    "missing_in_cot": "Agregar a COT o retirar de LDM si no corresponde al alcance.",
    "qty_mismatch": "Revisar cantidades entre COT y LDM.",
    "below_cost": "Subir precio de venta, renegociar costo o justificar pérdida.",
    "low_margin": "Revisar precio de venta o costo para recuperar margen.",
}

ISSUE_SEVERITY = {
    "below_cost": STATUS_CRITICAL,
    "missing_in_ldm": STATUS_CRITICAL,
    "missing_in_cot": STATUS_WARNING,
    "qty_mismatch": STATUS_WARNING,
    "low_margin": STATUS_WARNING,
}

ISSUE_PRIORITY = {
    "below_cost": 0,
    "missing_in_ldm": 1,
    "qty_mismatch": 2,
    "missing_in_cot": 3,
    "low_margin": 4,
}


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float, places: int = 2) -> float:
    return round(value, places)


def _pct(numerator: float, denominator: float) -> float | None:
    if denominator <= 0:
        return None
    return _round(numerator / denominator * 100, 1)


def classify_margin(margin_pct: float | None) -> str:
    """Convierte un margen porcentual en un status discreto."""
    if margin_pct is None:
        return STATUS_NO_DATA
    if margin_pct < 0:
        return STATUS_CRITICAL
    if margin_pct < MARGIN_OK_PCT:
        return STATUS_WARNING
    return STATUS_OK


def pick_active_quote(project_quotes: Iterable[dict]) -> dict | None:
    """La cotización General más reciente; si no hay, la más reciente de cualquier tipo."""
    quotes = [q for q in project_quotes if q]
    if not quotes:
        return None
    generals = [q for q in quotes if quote_type_key(q.get("quote_type")) == "General"]
    pool = generals or quotes
    return max(pool, key=lambda q: (q.get("date") or "", q.get("created_at") or ""))


def aggregate_quote_items(quote: dict | None) -> tuple[dict, dict]:
    """Devuelve (linked_by_id, unlinked_summary).

    `linked_by_id` mapea catalog_item_id → {qty, total, price_avg, descripciones}.
    `unlinked_summary` cuenta y suma los items de la cotización sin enlace.
    """
    if not quote:
        return {}, {"count": 0, "total": 0.0}

    linked: dict[str, dict] = {}
    unlinked = {"count": 0, "total": 0.0}
    for item in quote.get("items", []) or []:
        cid = str(item.get("catalog_item_id", "") or "").strip()
        qty = _safe_float(item.get("qty"))
        price = _safe_float(item.get("price"))
        total = _safe_float(item.get("total"), qty * price)
        if not cid:
            unlinked["count"] += 1
            unlinked["total"] = _round(unlinked["total"] + total)
            continue
        bucket = linked.setdefault(cid, {
            "qty": 0.0,
            "total": 0.0,
            "descripciones": set(),
        })
        bucket["qty"] += qty
        bucket["total"] += total
        desc = str(item.get("description") or "").strip()
        if desc:
            bucket["descripciones"].add(desc)

    for bucket in linked.values():
        bucket["qty"] = _round(bucket["qty"])
        bucket["total"] = _round(bucket["total"])
        bucket["price_avg"] = _round(bucket["total"] / bucket["qty"]) if bucket["qty"] else 0.0
        bucket["descripciones"] = sorted(bucket["descripciones"])
    return linked, unlinked


def aggregate_ldm_items(ldms: Iterable[dict]) -> tuple[dict, dict]:
    """Agrega artículos a través de TODAS las LDMs del proyecto.

    Devuelve (linked_by_id, unlinked_summary). El costo unitario es un
    promedio ponderado por cantidad: total_cot / qty.
    """
    linked: dict[str, dict] = {}
    unlinked = {"count": 0, "total": 0.0}
    for ldm in ldms or []:
        for item in ldm.get("items", []) or []:
            cid = str(item.get("catalog_item_id", "") or "").strip()
            qty = _safe_float(item.get("qty"))
            precio_cot = _safe_float(item.get("precio_cot"))
            total_cot = _safe_float(item.get("total_cot"), qty * precio_cot)
            if not cid:
                unlinked["count"] += 1
                unlinked["total"] = _round(unlinked["total"] + total_cot)
                continue
            bucket = linked.setdefault(cid, {
                "qty": 0.0,
                "total_cot": 0.0,
                "descripciones": set(),
                "ldm_numbers": set(),
            })
            bucket["qty"] += qty
            bucket["total_cot"] += total_cot
            desc = str(item.get("description") or "").strip()
            if desc:
                bucket["descripciones"].add(desc)
            ldm_number = str(ldm.get("ldm_number") or "").strip()
            if ldm_number:
                bucket["ldm_numbers"].add(ldm_number)

    for bucket in linked.values():
        bucket["qty"] = _round(bucket["qty"])
        bucket["total_cot"] = _round(bucket["total_cot"])
        bucket["cost_avg"] = (
            _round(bucket["total_cot"] / bucket["qty"]) if bucket["qty"] else 0.0
        )
        bucket["descripciones"] = sorted(bucket["descripciones"])
        bucket["ldm_numbers"] = sorted(bucket["ldm_numbers"])
    return linked, unlinked


def _detect_item_issues(qty_cot: float, qty_ldm: float, price_cot: float, cost_avg: float) -> list[str]:
    """Etiquetas de problema para un artículo. La UI las traduce a colores."""
    issues: list[str] = []
    if qty_cot > 0 and qty_ldm <= 0:
        issues.append("missing_in_ldm")
    if qty_ldm > 0 and qty_cot <= 0:
        issues.append("missing_in_cot")
    if qty_cot > 0 and qty_ldm > 0 and abs(qty_cot - qty_ldm) > QTY_TOLERANCE:
        issues.append("qty_mismatch")
    if price_cot > 0 and cost_avg > 0:
        margin_unit = price_cot - cost_avg
        margin_unit_pct = _pct(margin_unit, price_cot)
        if margin_unit < 0:
            issues.append("below_cost")
        elif margin_unit_pct is not None and margin_unit_pct < LOW_ITEM_MARGIN_PCT:
            issues.append("low_margin")
    return issues


def _classify_item(issues: list[str]) -> str:
    """Severidad del renglón para colorear."""
    if any(ISSUE_SEVERITY.get(issue) == STATUS_CRITICAL for issue in issues):
        return STATUS_CRITICAL
    if issues:
        return STATUS_WARNING
    return STATUS_OK


def _primary_action(issues: list[str]) -> dict | None:
    if not issues:
        return None
    issue = sorted(issues, key=lambda item: ISSUE_PRIORITY.get(item, 99))[0]
    return {
        "issue": issue,
        "label": ISSUE_LABELS.get(issue, issue),
        "text": ISSUE_ACTIONS.get(issue, "Revisar el renglón."),
        "status": ISSUE_SEVERITY.get(issue, STATUS_WARNING),
    }


def _issue_details(issues: list[str]) -> list[dict]:
    return [
        {
            "issue": issue,
            "label": ISSUE_LABELS.get(issue, issue),
            "action": ISSUE_ACTIONS.get(issue, "Revisar el renglón."),
            "status": ISSUE_SEVERITY.get(issue, STATUS_WARNING),
        }
        for issue in sorted(issues, key=lambda item: ISSUE_PRIORITY.get(item, 99))
    ]


def compare_items(
    quote_linked: dict,
    ldm_linked: dict,
    catalog_by_id: dict,
) -> list[dict]:
    """Construye una lista de filas comparadas, ordenada por severidad."""
    rows: list[dict] = []
    all_ids = set(quote_linked) | set(ldm_linked)
    for cid in all_ids:
        cot = quote_linked.get(cid) or {}
        ldm = ldm_linked.get(cid) or {}
        qty_cot = _safe_float(cot.get("qty"))
        qty_ldm = _safe_float(ldm.get("qty"))
        total_cot = _safe_float(cot.get("total"))
        total_ldm = _safe_float(ldm.get("total_cot"))
        price_cot = _safe_float(cot.get("price_avg"))
        cost_avg = _safe_float(ldm.get("cost_avg"))
        margin_unit = _round(price_cot - cost_avg) if price_cot and cost_avg else None
        margin_unit_pct = _pct(margin_unit, price_cot) if margin_unit is not None else None
        margin_total = _round(total_cot - total_ldm) if (total_cot or total_ldm) else None
        margin_total_pct = _pct(margin_total, total_cot) if margin_total is not None else None
        qty_delta = _round(qty_ldm - qty_cot) if (qty_cot or qty_ldm) else 0.0
        issues = _detect_item_issues(qty_cot, qty_ldm, price_cot, cost_avg)
        catalog_item = catalog_by_id.get(cid) or {}
        cot_desc = cot.get("descripciones") or []
        ldm_desc = ldm.get("descripciones") or []
        nombre = (
            catalog_item.get("nombre")
            or (cot_desc or [""])[0]
            or (ldm_desc or [""])[0]
            or cid
        )
        rows.append({
            "catalog_item_id": cid,
            "nombre": nombre,
            "categoria": catalog_item.get("categoria", ""),
            "unidad": catalog_item.get("unidad", ""),
            "qty_cot": qty_cot,
            "qty_ldm": qty_ldm,
            "qty_delta": qty_delta,
            "price_cot": price_cot,
            "cost_avg": cost_avg,
            "total_cot": _round(total_cot),
            "total_ldm": _round(total_ldm),
            "margin_unit": margin_unit,
            "margin_unit_pct": margin_unit_pct,
            "margin_total": margin_total,
            "margin_total_pct": margin_total_pct,
            "quote_descripciones": cot_desc,
            "ldm_descripciones": ldm_desc,
            "ldm_numbers": ldm.get("ldm_numbers", []),
            "issues": issues,
            "issue_details": _issue_details(issues),
            "primary_action": _primary_action(issues),
            "status": _classify_item(issues),
        })

    severity_rank = {STATUS_CRITICAL: 0, STATUS_WARNING: 1, STATUS_OK: 2}
    rows.sort(key=lambda r: (severity_rank.get(r["status"], 9), r["nombre"].lower()))
    return rows


def _summarize_rows(rows: list[dict]) -> dict:
    summary = {
        "items_total": len(rows),
        "items_critical": 0,
        "items_warning": 0,
        "items_ok": 0,
        "missing_in_ldm": 0,
        "missing_in_cot": 0,
        "qty_mismatch": 0,
        "below_cost": 0,
        "low_margin": 0,
    }
    for row in rows:
        status_key = f"items_{row['status']}"
        if status_key in summary:
            summary[status_key] += 1
        for issue in row["issues"]:
            if issue in summary:
                summary[issue] += 1
    return summary


def _suggested_actions(rows: list[dict], quote_unlinked: dict, ldm_unlinked: dict) -> list[dict]:
    counts: dict[str, int] = {}
    first_status: dict[str, str] = {}
    for row in rows:
        for issue in row.get("issues", []):
            counts[issue] = counts.get(issue, 0) + 1
            first_status.setdefault(issue, ISSUE_SEVERITY.get(issue, STATUS_WARNING))

    if quote_unlinked.get("count"):
        counts["quote_unlinked"] = quote_unlinked["count"]
        first_status["quote_unlinked"] = STATUS_WARNING
    if ldm_unlinked.get("count"):
        counts["ldm_unlinked"] = ldm_unlinked["count"]
        first_status["ldm_unlinked"] = STATUS_WARNING

    labels = {
        **ISSUE_LABELS,
        "quote_unlinked": "COT sin catálogo",
        "ldm_unlinked": "LDM sin catálogo",
    }
    actions = {
        **ISSUE_ACTIONS,
        "quote_unlinked": "Vincular partidas manuales de COT al catálogo.",
        "ldm_unlinked": "Vincular partidas manuales de LDM al catálogo.",
    }
    priority = {**ISSUE_PRIORITY, "quote_unlinked": 5, "ldm_unlinked": 6}
    result = []
    for issue, count in counts.items():
        result.append({
            "issue": issue,
            "count": count,
            "label": labels.get(issue, issue),
            "text": actions.get(issue, "Revisar."),
            "status": first_status.get(issue, STATUS_WARNING),
        })
    result.sort(key=lambda item: priority.get(item["issue"], 99))
    return result


def compute_consistency(
    project: dict,
    quotes: Iterable[dict],
    ldms: Iterable[dict],
    catalog_by_id: dict | None = None,
) -> dict:
    """Reporte completo de consistencia para un proyecto.

    Retorna un diccionario listo para inyectar en plantillas.
    """
    project_id = project.get("id")
    project_quotes = [q for q in quotes if q.get("project_id") == project_id]
    project_ldms = [m for m in ldms if m.get("project_id") == project_id]

    active_quote = pick_active_quote(project_quotes)
    quote_linked, quote_unlinked = aggregate_quote_items(active_quote)
    ldm_linked, ldm_unlinked = aggregate_ldm_items(project_ldms)

    quote_subtotal = _round(_safe_float((active_quote or {}).get("subtotal")))
    ldm_subtotal = _round(sum(_safe_float(m.get("subtotal_cot")) for m in project_ldms))
    quote_linked_total = _round(sum(item.get("total", 0.0) for item in quote_linked.values()))
    ldm_linked_total = _round(sum(item.get("total_cot", 0.0) for item in ldm_linked.values()))
    quote_unlinked_total = _round(quote_unlinked.get("total", 0.0))
    ldm_unlinked_total = _round(ldm_unlinked.get("total", 0.0))
    margin_abs = _round(quote_subtotal - ldm_subtotal)
    if quote_subtotal > 0:
        margin_pct = _round(margin_abs / quote_subtotal * 100, 1)
    else:
        margin_pct = None
    status = classify_margin(margin_pct) if (quote_subtotal > 0 or ldm_subtotal > 0) else STATUS_NO_DATA

    rows = compare_items(quote_linked, ldm_linked, catalog_by_id or {})
    summary = _summarize_rows(rows)
    suggested_actions = _suggested_actions(rows, quote_unlinked, ldm_unlinked)

    has_general = any(
        quote_type_key(q.get("quote_type")) == "General" for q in project_quotes
    )

    return {
        "active_quote": active_quote,
        "active_quote_is_general": bool(active_quote) and quote_type_key(active_quote.get("quote_type")) == "General",
        "has_general_quote": has_general,
        "quote_subtotal": quote_subtotal,
        "ldm_subtotal": ldm_subtotal,
        "quote_linked_total": quote_linked_total,
        "ldm_linked_total": ldm_linked_total,
        "quote_unlinked_total": quote_unlinked_total,
        "ldm_unlinked_total": ldm_unlinked_total,
        "margin_abs": margin_abs,
        "margin_pct": margin_pct,
        "status": status,
        "status_label": STATUS_LABELS[status],
        "items": rows,
        "summary": summary,
        "quote_unlinked": quote_unlinked,
        "ldm_unlinked": ldm_unlinked,
        "suggested_actions": suggested_actions,
    }
