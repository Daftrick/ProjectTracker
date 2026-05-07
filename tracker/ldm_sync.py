"""Sincronizacion parcial de LDM desde bundles de COT."""

from __future__ import annotations

from typing import Iterable

from .bundles import expand_quote_bundles
from .comparison_ignored import SCOPE_TECHNICAL, ignored_catalog_ids, split_ignored_linked
from .comparison_rules import (
    aggregate_ldm_for_expected_items,
    compare_expected_vs_actual,
    convert_qty,
    rules_by_cot_id,
)


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float, places: int = 4) -> float:
    return round(value, places)


def _clean(value) -> str:
    return str(value or "").strip()


def missing_ldm_items_from_bundles(
    quote: dict | None,
    project_ldms: Iterable[dict],
    bundles: Iterable[dict],
    comparison_rules: Iterable[dict],
    catalog_by_id: dict | None = None,
    comparison_ignored_items: Iterable[dict] | None = None,
) -> list[dict]:
    """Devuelve filas LDM faltantes derivadas de la expansion tecnica.

    No modifica LDMs existentes. Calcula diferencias contra todas las LDMs del
    proyecto para evitar duplicar materiales ya capturados en otra lista.
    """
    catalog_by_id = catalog_by_id or {}
    expansion = expand_quote_bundles(quote, bundles or [], catalog_by_id)
    actual = aggregate_ldm_for_expected_items(project_ldms or [], comparison_rules or [], catalog_by_id)
    ignored_ids = ignored_catalog_ids(comparison_ignored_items or [], scope=SCOPE_TECHNICAL)
    expected_items, _ = split_ignored_linked(expansion["items"], ignored_ids)
    actual_items, _ = split_ignored_linked(actual["items"], ignored_ids)
    comparison = compare_expected_vs_actual(expected_items, actual_items, comparison_rules or [], catalog_by_id)
    by_expected_rule = rules_by_cot_id(comparison_rules or [])

    missing = []
    for row in comparison["rows"]:
        if row.get("issue") not in {"missing_in_ldm", "qty_shortage"}:
            continue
        expected_cid = _clean(row.get("catalog_item_id"))
        expected_qty = _safe_float(row.get("expected_qty"))
        actual_qty = _safe_float(row.get("actual_qty"))
        shortage_expected_qty = _round(max(expected_qty - actual_qty, 0.0))
        if not expected_cid or shortage_expected_qty <= 0:
            continue

        rule = by_expected_rule.get(expected_cid)
        target_cid = _clean((rule or {}).get("ldm_catalog_item_id")) or expected_cid
        target_qty = convert_qty(shortage_expected_qty, rule, to_expected=False) if rule else shortage_expected_qty
        target_qty = _round(target_qty)
        if target_qty <= 0:
            continue

        catalog_item = catalog_by_id.get(target_cid) or catalog_by_id.get(expected_cid) or {}
        missing.append({
            "catalog_item_id": target_cid,
            "description": catalog_item.get("nombre") or row.get("nombre") or target_cid,
            "unit": (rule or {}).get("ldm_unit") or catalog_item.get("unidad") or row.get("unidad") or "pza",
            "qty": target_qty,
            "precio_cot": 0.0,
            "total_cot": 0.0,
            "origen": "bundle_sync",
            "sync_expected_catalog_item_id": expected_cid,
            "sync_expected_qty": shortage_expected_qty,
            "sync_issue": row.get("issue"),
            "comparison_rule_id": (rule or {}).get("id", ""),
        })
    return missing


def append_missing_bundle_items_to_ldm(
    ldm: dict,
    quote: dict | None,
    project_ldms: Iterable[dict],
    bundles: Iterable[dict],
    comparison_rules: Iterable[dict],
    catalog_by_id: dict | None = None,
    comparison_ignored_items: Iterable[dict] | None = None,
) -> tuple[dict, list[dict]]:
    """Anexa faltantes a una LDM y devuelve (copia_actualizada, agregados)."""
    additions = missing_ldm_items_from_bundles(
        quote,
        project_ldms,
        bundles,
        comparison_rules,
        catalog_by_id=catalog_by_id,
        comparison_ignored_items=comparison_ignored_items,
    )
    updated = dict(ldm or {})
    updated["items"] = list(updated.get("items", []) or []) + additions
    return updated, additions
