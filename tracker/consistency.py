"""Consistencia entre cotización (COT) y listas de materiales (LDM).

Compara, por proyecto, los artículos cotizados al cliente contra los
artículos costeados con proveedores. Funciones puras (sin I/O) que pueden
combinarse para vistas: dashboard, detalle de proyecto, banners en formularios.

Reglas de comparación:
    - Cotización activa = la cotización General más reciente del proyecto.
      Si no hay General, se usa la más reciente de cualquier tipo (la UI
      indicará explícitamente que no hubo General).
    - Costo proveedor = suma de subtotales de todas las LDMs del proyecto.
    - Comparación por artículo: se agrega por `catalog_item_id`. Los items
      sin enlace al catálogo se contabilizan en `unlinked_*` para alertar.
    - Margen % = (cotizado - costo) / cotizado * 100. Si cotizado == 0 → None.

Umbrales de estado (mantener en una sola constante para futura configurabilidad):
    margen >= MARGIN_OK_PCT   (30%)  → "ok"        (consistente)
    0   <= margen <  30%             → "warning"   (revisar)
    margen <  0%                     → "critical"  (LDM > COT)
    sin datos suficientes            → "no_data"
"""

from __future__ import annotations

from typing import Iterable

from .catalog import quote_type_key
from .bundles import expand_quote_bundles
from .comparison_rules import aggregate_ldm_for_expected_items, compare_expected_vs_actual
from .comparison_ignored import (
    SCOPE_COMMERCIAL,
    SCOPE_TECHNICAL,
    ignored_catalog_ids,
    split_ignored_linked,
    summarize_ignored,
)

MARGIN_OK_PCT = 30.0
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


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float, places: int = 2) -> float:
    return round(value, places)


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
    if price_cot > 0 and cost_avg > 0 and price_cot < cost_avg:
        issues.append("below_cost")
    elif price_cot > 0 and cost_avg > 0:
        margin_pct = (price_cot - cost_avg) / price_cot * 100
        if 0 <= margin_pct < MARGIN_OK_PCT:
            issues.append("low_margin")
    return issues


def _classify_item(issues: list[str]) -> str:
    """Severidad del renglón para colorear."""
    if "below_cost" in issues or "missing_in_ldm" in issues:
        return STATUS_CRITICAL
    if issues:
        return STATUS_WARNING
    return STATUS_OK


def _issue_details(issues: list[str]) -> list[str]:
    labels = {
        "missing_in_ldm": "Existe en COT pero no aparece en LDM.",
        "missing_in_cot": "Existe en LDM pero no aparece en COT.",
        "qty_mismatch": "La cantidad COT/LDM no coincide.",
        "below_cost": "El costo unitario es mayor al precio de venta.",
        "low_margin": "El margen unitario está por debajo del objetivo.",
    }
    return [labels.get(issue, issue) for issue in issues]


def _primary_action(issues: list[str]) -> str:
    if "below_cost" in issues:
        return "Revisar precio de venta o costo proveedor."
    if "missing_in_ldm" in issues:
        return "Agregar material en LDM o marcar artículo como no requerido."
    if "missing_in_cot" in issues:
        return "Vincular a COT, integrar en bundle o marcar como ignorado."
    if "qty_mismatch" in issues:
        return "Revisar cantidades y unidades."
    if "low_margin" in issues:
        return "Revisar margen unitario."
    return "Sin acción requerida."


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
        price_cot = _safe_float(cot.get("price_avg"))
        cost_avg = _safe_float(ldm.get("cost_avg"))
        issues = _detect_item_issues(qty_cot, qty_ldm, price_cot, cost_avg)
        catalog_item = catalog_by_id.get(cid) or {}
        nombre = (
            catalog_item.get("nombre")
            or (cot.get("descripciones") or [""])[0]
            or (ldm.get("descripciones") or [""])[0]
            or cid
        )
        rows.append({
            "catalog_item_id": cid,
            "nombre": nombre,
            "categoria": catalog_item.get("categoria", ""),
            "unidad": catalog_item.get("unidad", ""),
            "qty_cot": qty_cot,
            "qty_ldm": qty_ldm,
            "qty_delta": _round(qty_ldm - qty_cot),
            "price_cot": price_cot,
            "cost_avg": cost_avg,
            "margin_unit": _round(price_cot - cost_avg) if price_cot and cost_avg else None,
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


def compute_consistency(
    project: dict,
    quotes: Iterable[dict],
    ldms: Iterable[dict],
    catalog_by_id: dict | None = None,
    bundles: Iterable[dict] | None = None,
    comparison_rules: Iterable[dict] | None = None,
    comparison_ignored_items: Iterable[dict] | None = None,
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

    ignored_commercial_ids = ignored_catalog_ids(comparison_ignored_items or [], scope=SCOPE_COMMERCIAL)
    quote_linked, quote_ignored_linked = split_ignored_linked(quote_linked, ignored_commercial_ids)
    ldm_linked, ldm_ignored_linked = split_ignored_linked(ldm_linked, ignored_commercial_ids)

    quote_subtotal = _round(_safe_float((active_quote or {}).get("subtotal")))
    ldm_subtotal = _round(sum(_safe_float(m.get("subtotal_cot")) for m in project_ldms))
    margin_abs = _round(quote_subtotal - ldm_subtotal)
    if quote_subtotal > 0:
        margin_pct = _round(margin_abs / quote_subtotal * 100, 1)
    else:
        margin_pct = None
    status = classify_margin(margin_pct) if (quote_subtotal > 0 or ldm_subtotal > 0) else STATUS_NO_DATA

    quote_linked_total = _round(sum(_safe_float(item.get("total")) for item in quote_linked.values()))
    ldm_linked_total = _round(sum(_safe_float(item.get("total_cot")) for item in ldm_linked.values()))
    quote_unlinked_total = _round(_safe_float(quote_unlinked.get("total")))
    ldm_unlinked_total = _round(_safe_float(ldm_unlinked.get("total")))

    rows = compare_items(quote_linked, ldm_linked, catalog_by_id or {})
    summary = _summarize_rows(rows)
    suggested_actions = []
    action_defs = [
        ("missing_in_ldm", STATUS_CRITICAL, "Faltantes en LDM", "Agregar materiales faltantes, crear bundle o marcar artículo como ignorado."),
        ("missing_in_cot", STATUS_WARNING, "Extras en LDM", "Atribuir a COT/bundle o marcar como costo no atribuible al cliente."),
        ("qty_mismatch", STATUS_WARNING, "Cantidades diferentes", "Revisar cantidades, unidades y reglas COT/LDM."),
        ("below_cost", STATUS_CRITICAL, "Venta bajo costo", "Corregir precio de venta o costo de proveedor."),
        ("low_margin", STATUS_WARNING, "Margen bajo", "Revisar margen unitario."),
    ]
    for key, action_status, label, text in action_defs:
        count = summary.get(key, 0)
        if count:
            suggested_actions.append({"key": key, "status": action_status, "label": label, "text": text, "count": count})

    # Consistencia técnica por bundles: la COT se expande a materiales
    # esperados y la LDM se normaliza con reglas de comparación (por ejemplo
    # tubería cotizada en ml vs comprada por pieza/tramo).
    bundle_expansion = expand_quote_bundles(active_quote, bundles or [], catalog_by_id or {})
    technical_actual = aggregate_ldm_for_expected_items(project_ldms, comparison_rules or [], catalog_by_id or {})
    ignored_technical_ids = ignored_catalog_ids(comparison_ignored_items or [], scope=SCOPE_TECHNICAL)
    technical_expected_items, technical_expected_ignored = split_ignored_linked(bundle_expansion["items"], ignored_technical_ids)
    technical_actual_items, technical_actual_ignored = split_ignored_linked(technical_actual["items"], ignored_technical_ids)
    technical_compare = compare_expected_vs_actual(
        technical_expected_items,
        technical_actual_items,
        comparison_rules or [],
        catalog_by_id or {},
    )
    bundle_consistency = {
        "status": technical_compare["status"],
        "rows": technical_compare["rows"],
        "summary": technical_compare["summary"],
        "expected": technical_expected_items,
        "actual": technical_actual_items,
        "ignored_expected": summarize_ignored(technical_expected_ignored, catalog_by_id or {}, total_key="total"),
        "ignored_actual": summarize_ignored(technical_actual_ignored, catalog_by_id or {}, total_key="total_cot"),
        "ldm_unlinked": technical_actual["unlinked"],
        "bundle_quote_items": bundle_expansion["bundle_quote_items"],
        "unmapped_quote_items": bundle_expansion["unmapped_quote_items"],
        "invalid_components": bundle_expansion["invalid_components"],
    }

    has_general = any(
        quote_type_key(q.get("quote_type")) == "General" for q in project_quotes
    )

    return {
        "active_quote": active_quote,
        "active_quote_is_general": bool(active_quote) and quote_type_key(active_quote.get("quote_type")) == "General",
        "has_general_quote": has_general,
        "quote_subtotal": quote_subtotal,
        "ldm_subtotal": ldm_subtotal,
        "margin_abs": margin_abs,
        "margin_pct": margin_pct,
        "status": status,
        "status_label": STATUS_LABELS[status],
        "items": rows,
        "summary": summary,
        "quote_linked_total": quote_linked_total,
        "ldm_linked_total": ldm_linked_total,
        "quote_unlinked_total": quote_unlinked_total,
        "ldm_unlinked_total": ldm_unlinked_total,
        "suggested_actions": suggested_actions,
        "quote_unlinked": quote_unlinked,
        "ldm_unlinked": ldm_unlinked,
        "ignored": {
            "commercial_quote": summarize_ignored(quote_ignored_linked, catalog_by_id or {}, total_key="total"),
            "commercial_ldm": summarize_ignored(ldm_ignored_linked, catalog_by_id or {}, total_key="total_cot"),
            "catalog_ids": sorted(ignored_commercial_ids | ignored_technical_ids),
        },
        "bundle_consistency": bundle_consistency,
    }
