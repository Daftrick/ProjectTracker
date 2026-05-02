"""Reglas de comparación entre COT y LDM.

Permiten relacionar artículos equivalentes con distinta unidad o distinto ID de
catálogo. Caso típico: COT cotiza tubería por metro lineal, pero LDM compra
piezas/tramos de 3 m.
"""

from __future__ import annotations

from math import ceil, floor
from typing import Iterable

ROUND_NONE = "none"
ROUND_CEIL = "ceil"
ROUND_FLOOR = "floor"
ROUND_ROUND = "round"

DIRECTION_LDM_TO_COT = "ldm_to_cot"
DIRECTION_COT_TO_LDM = "cot_to_ldm"

DEFAULT_TOLERANCE_PCT = 5.0


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _clean(value) -> str:
    return str(value or "").strip()


def apply_rounding(value: float, rounding: str = ROUND_NONE) -> float:
    rounding = _clean(rounding) or ROUND_NONE
    if rounding == ROUND_CEIL:
        return float(ceil(value))
    if rounding == ROUND_FLOOR:
        return float(floor(value))
    if rounding == ROUND_ROUND:
        return float(round(value))
    return value


def normalize_rule(rule: dict) -> dict:
    current = dict(rule or {})
    current["id"] = _clean(current.get("id"))
    current["name"] = _clean(current.get("name"))
    current["cot_catalog_item_id"] = _clean(current.get("cot_catalog_item_id"))
    current["ldm_catalog_item_id"] = _clean(current.get("ldm_catalog_item_id"))
    current["cot_unit"] = _clean(current.get("cot_unit"))
    current["ldm_unit"] = _clean(current.get("ldm_unit"))
    current["factor"] = _safe_float(current.get("factor"), 1.0) or 1.0
    current["direction"] = _clean(current.get("direction")) or DIRECTION_LDM_TO_COT
    current["rounding"] = _clean(current.get("rounding")) or ROUND_NONE
    current["tolerance_pct"] = _safe_float(current.get("tolerance_pct"), DEFAULT_TOLERANCE_PCT)
    current["active"] = bool(current.get("active", True))
    current["notes"] = _clean(current.get("notes"))
    return current


def active_rules(rules: Iterable[dict]) -> list[dict]:
    return [normalize_rule(rule) for rule in (rules or []) if normalize_rule(rule).get("active", True)]


def rules_by_cot_id(rules: Iterable[dict]) -> dict[str, dict]:
    indexed: dict[str, dict] = {}
    for rule in active_rules(rules):
        cid = rule.get("cot_catalog_item_id")
        if cid and cid not in indexed:
            indexed[cid] = rule
    return indexed


def rules_by_ldm_id(rules: Iterable[dict]) -> dict[str, list[dict]]:
    indexed: dict[str, list[dict]] = {}
    for rule in active_rules(rules):
        ldm_id = rule.get("ldm_catalog_item_id")
        if ldm_id:
            indexed.setdefault(ldm_id, []).append(rule)
    return indexed


def convert_qty(value: float, rule: dict, *, to_expected: bool = True) -> float:
    """Convierte cantidades según una regla.

    `to_expected=True` convierte la cantidad LDM a unidad/ID esperado de COT.
    """
    current = normalize_rule(rule)
    factor = current.get("factor") or 1.0
    qty = _safe_float(value)
    direction = current.get("direction")
    if to_expected:
        converted = qty * factor if direction == DIRECTION_LDM_TO_COT else qty / factor
    else:
        converted = qty / factor if direction == DIRECTION_LDM_TO_COT else qty * factor
    return apply_rounding(converted, current.get("rounding"))


def aggregate_ldm_for_expected_items(ldms: Iterable[dict], rules: Iterable[dict], catalog_by_id: dict | None = None) -> dict:
    """Agrega LDM convirtiendo artículos LDM al ID/unidad esperada de COT.

    Si un artículo LDM no tiene regla, se agrega con su propio catalog_item_id.
    Si tiene regla, se agrega bajo `cot_catalog_item_id` convertido.
    """
    catalog_by_id = catalog_by_id or {}
    by_ldm_id = rules_by_ldm_id(rules)
    actual: dict[str, dict] = {}
    unlinked = {"count": 0, "qty": 0.0, "items": []}

    for ldm in ldms or []:
        ldm_number = _clean(ldm.get("ldm_number"))
        for item in ldm.get("items", []) or []:
            item_cid = _clean(item.get("catalog_item_id"))
            qty = _safe_float(item.get("qty"))
            if not item_cid:
                unlinked["count"] += 1
                unlinked["qty"] += qty
                unlinked["items"].append(item)
                continue
            item_rules = by_ldm_id.get(item_cid) or []
            if item_rules:
                # En fase 1 usamos la primera regla activa. La UI de fase 2 debe
                # impedir ambigüedades o permitir resolverlas manualmente.
                rule = item_rules[0]
                target_cid = rule.get("cot_catalog_item_id") or item_cid
                converted_qty = convert_qty(qty, rule, to_expected=True)
                conversion = rule
            else:
                target_cid = item_cid
                converted_qty = qty
                conversion = None
            bucket = actual.setdefault(target_cid, {
                "catalog_item_id": target_cid,
                "nombre": (catalog_by_id.get(target_cid) or {}).get("nombre", target_cid),
                "unidad": (catalog_by_id.get(target_cid) or {}).get("unidad", ""),
                "qty": 0.0,
                "sources": [],
            })
            bucket["qty"] += converted_qty
            bucket["sources"].append({
                "ldm_number": ldm_number,
                "ldm_catalog_item_id": item_cid,
                "description": item.get("description", ""),
                "qty_original": qty,
                "qty_converted": round(converted_qty, 4),
                "rule_id": conversion.get("id", "") if conversion else "",
                "rule_name": conversion.get("name", "") if conversion else "",
            })

    for bucket in actual.values():
        bucket["qty"] = round(bucket["qty"], 4)
    unlinked["qty"] = round(unlinked["qty"], 4)
    return {"items": actual, "unlinked": unlinked}


def compare_expected_vs_actual(expected: dict, actual: dict, rules: Iterable[dict], catalog_by_id: dict | None = None) -> dict:
    """Compara materiales esperados por bundles contra LDM real convertida."""
    catalog_by_id = catalog_by_id or {}
    by_cot = rules_by_cot_id(rules)
    rows = []
    all_ids = set((expected or {}).keys()) | set((actual or {}).keys())
    for cid in all_ids:
        exp = (expected or {}).get(cid) or {}
        act = (actual or {}).get(cid) or {}
        expected_qty = _safe_float(exp.get("qty"))
        actual_qty = _safe_float(act.get("qty"))
        diff = round(actual_qty - expected_qty, 4)
        rule = by_cot.get(cid)
        tolerance_pct = _safe_float((rule or {}).get("tolerance_pct"), DEFAULT_TOLERANCE_PCT)
        tolerance_qty = abs(expected_qty) * tolerance_pct / 100.0 if expected_qty else 0.0
        if expected_qty > 0 and actual_qty <= 0:
            status = "critical"
            issue = "missing_in_ldm"
        elif actual_qty > 0 and expected_qty <= 0:
            status = "warning"
            issue = "extra_in_ldm"
        elif abs(diff) <= max(tolerance_qty, 0.0001):
            status = "ok"
            issue = "ok"
        elif diff < 0:
            status = "critical"
            issue = "qty_shortage"
        else:
            status = "warning"
            issue = "qty_excess"
        catalog_item = catalog_by_id.get(cid) or {}
        rows.append({
            "catalog_item_id": cid,
            "nombre": catalog_item.get("nombre") or exp.get("nombre") or act.get("nombre") or cid,
            "unidad": catalog_item.get("unidad") or exp.get("unidad") or act.get("unidad") or "",
            "expected_qty": round(expected_qty, 4),
            "actual_qty": round(actual_qty, 4),
            "diff_qty": diff,
            "tolerance_pct": tolerance_pct,
            "status": status,
            "issue": issue,
            "sources_expected": exp.get("sources", []),
            "sources_actual": act.get("sources", []),
            "comparison_rule_id": (rule or {}).get("id", ""),
        })
    rank = {"critical": 0, "warning": 1, "ok": 2}
    rows.sort(key=lambda row: (rank.get(row["status"], 9), row["nombre"].lower()))
    summary = {
        "items_total": len(rows),
        "items_critical": sum(1 for row in rows if row["status"] == "critical"),
        "items_warning": sum(1 for row in rows if row["status"] == "warning"),
        "items_ok": sum(1 for row in rows if row["status"] == "ok"),
        "missing_in_ldm": sum(1 for row in rows if row["issue"] == "missing_in_ldm"),
        "extra_in_ldm": sum(1 for row in rows if row["issue"] == "extra_in_ldm"),
        "qty_shortage": sum(1 for row in rows if row["issue"] == "qty_shortage"),
        "qty_excess": sum(1 for row in rows if row["issue"] == "qty_excess"),
    }
    if summary["items_critical"]:
        status = "critical"
    elif summary["items_warning"]:
        status = "warning"
    elif rows:
        status = "ok"
    else:
        status = "no_data"
    return {"status": status, "rows": rows, "summary": summary}
