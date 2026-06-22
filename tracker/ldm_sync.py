"""Sincronizacion parcial de LDM desde bundles de COT."""

from __future__ import annotations

from typing import Iterable

from .bundles import expand_quote_bundles


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float, places: int = 4) -> float:
    return round(value, places)


def _clean(value) -> str:
    return str(value or "").strip()


def _aggregate_ldm_qty_by_catalog(project_ldms: Iterable[dict], catalog_by_id: dict | None = None) -> dict[str, dict]:
    catalog_by_id = catalog_by_id or {}
    actual: dict[str, dict] = {}
    for ldm in project_ldms or []:
        ldm_number = ldm.get("ldm_number") or ""
        for item in ldm.get("items", []) or []:
            catalog_item_id = _clean(item.get("catalog_item_id"))
            if not catalog_item_id:
                continue
            qty = _safe_float(item.get("qty"))
            catalog_item = catalog_by_id.get(catalog_item_id) or {}
            bucket = actual.setdefault(catalog_item_id, {
                "catalog_item_id": catalog_item_id,
                "description": catalog_item.get("nombre") or item.get("description") or catalog_item_id,
                "unit": catalog_item.get("unidad") or item.get("unit") or "pza",
                "qty": 0.0,
                "ldm_numbers": [],
            })
            bucket["qty"] += qty
            if ldm_number:
                bucket["ldm_numbers"].append(ldm_number)
    for bucket in actual.values():
        bucket["qty"] = _round(bucket["qty"])
        bucket["ldm_numbers"] = sorted(set(bucket["ldm_numbers"]))
    return actual


def missing_ldm_items_from_bundles(
    quote: dict | None,
    project_ldms: Iterable[dict],
    bundles: Iterable[dict],
    catalog_by_id: dict | None = None,
) -> list[dict]:
    """Devuelve filas LDM faltantes derivadas de la expansion tecnica.

    No modifica LDMs existentes. Calcula diferencias contra todas las LDMs del
    proyecto para evitar duplicar materiales ya capturados en otra lista.
    """
    catalog_by_id = catalog_by_id or {}
    expansion = expand_quote_bundles(quote, bundles or [], catalog_by_id)
    actual_items = _aggregate_ldm_qty_by_catalog(project_ldms or [], catalog_by_id)

    missing = []
    for expected_cid, expected in sorted(expansion["items"].items()):
        expected_cid = _clean(expected_cid)
        expected_qty = _safe_float(expected.get("qty"))
        actual_qty = _safe_float((actual_items.get(expected_cid) or {}).get("qty"))
        shortage_expected_qty = _round(max(expected_qty - actual_qty, 0.0))
        if not expected_cid or shortage_expected_qty <= 0:
            continue

        catalog_item = catalog_by_id.get(expected_cid) or {}
        issue = "missing_in_ldm" if expected_cid not in actual_items else "qty_shortage"
        missing.append({
            "catalog_item_id": expected_cid,
            "description": catalog_item.get("nombre") or expected.get("nombre") or expected_cid,
            "unit": catalog_item.get("unidad") or expected.get("unidad") or "pza",
            "qty": shortage_expected_qty,
            "precio_cot": 0.0,
            "total_cot": 0.0,
            "origen": "bundle_sync",
            "sync_expected_catalog_item_id": expected_cid,
            "sync_expected_qty": shortage_expected_qty,
            "sync_total_expected_qty": _round(expected_qty),
            "sync_actual_qty": _round(actual_qty),
            "sync_issue": issue,
        })
    return missing


def selected_missing_bundle_items(missing_items: Iterable[dict], catalog_item_ids: Iterable[str]) -> list[dict]:
    """Filtra faltantes por seleccion explicita de catalog_item_id."""
    selected = {_clean(item_id) for item_id in catalog_item_ids or [] if _clean(item_id)}
    if not selected:
        return []
    return [
        dict(item)
        for item in missing_items or []
        if _clean(item.get("catalog_item_id")) in selected
    ]


def append_missing_bundle_items_to_ldm(
    ldm: dict,
    quote: dict | None,
    project_ldms: Iterable[dict],
    bundles: Iterable[dict],
    catalog_by_id: dict | None = None,
) -> tuple[dict, list[dict]]:
    """Anexa faltantes a una LDM y devuelve (copia_actualizada, agregados)."""
    additions = missing_ldm_items_from_bundles(
        quote,
        project_ldms,
        bundles,
        catalog_by_id=catalog_by_id,
    )
    updated = dict(ldm or {})
    updated["items"] = list(updated.get("items", []) or []) + additions
    return updated, additions
