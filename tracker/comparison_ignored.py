"""Artículos ignorados en comparación COT/LDM.

Los artículos ignorados siguen formando parte del costo total del proyecto,
pero se excluyen de los cruces de consistencia comercial/técnica porque no son
atribuibles directamente al cliente o funcionan como consumibles indirectos.
"""

from __future__ import annotations

from typing import Iterable

SCOPE_BOTH = "both"
SCOPE_COMMERCIAL = "commercial"
SCOPE_TECHNICAL = "technical"
VALID_SCOPES = {SCOPE_BOTH, SCOPE_COMMERCIAL, SCOPE_TECHNICAL}


def _clean(value) -> str:
    return str(value or "").strip()


def normalize_ignored_item(item: dict) -> dict:
    """Normaliza una regla de artículo ignorado."""
    current = dict(item or {})
    scope = _clean(current.get("scope")) or SCOPE_BOTH
    if scope not in VALID_SCOPES:
        scope = SCOPE_BOTH
    current["id"] = _clean(current.get("id"))
    current["catalog_item_id"] = _clean(current.get("catalog_item_id"))
    current["scope"] = scope
    current["active"] = bool(current.get("active", True))
    current["notes"] = _clean(current.get("notes"))
    return current


def active_ignored_items(items: Iterable[dict], *, scope: str | None = None) -> list[dict]:
    """Devuelve reglas activas aplicables al scope solicitado."""
    requested = _clean(scope)
    result = []
    for item in items or []:
        current = normalize_ignored_item(item)
        if not current.get("active", True) or not current.get("catalog_item_id"):
            continue
        if requested and current.get("scope") not in {SCOPE_BOTH, requested}:
            continue
        result.append(current)
    return result


def ignored_catalog_ids(items: Iterable[dict], *, scope: str | None = None) -> set[str]:
    """Conjunto de catalog_item_id ignorados para un scope."""
    return {item["catalog_item_id"] for item in active_ignored_items(items, scope=scope)}


def ignored_catalog_map(items: Iterable[dict], *, scope: str | None = None) -> dict[str, dict]:
    """Mapa catalog_item_id → regla de ignorado."""
    return {item["catalog_item_id"]: item for item in active_ignored_items(items, scope=scope)}


def split_ignored_linked(linked: dict, ignored_ids: set[str]) -> tuple[dict, dict]:
    """Separa agregados linked en (incluidos, ignorados)."""
    ignored_ids = set(ignored_ids or set())
    kept = {}
    ignored = {}
    for cid, value in (linked or {}).items():
        if cid in ignored_ids:
            ignored[cid] = value
        else:
            kept[cid] = value
    return kept, ignored


def summarize_ignored(ignored_linked: dict, catalog_by_id: dict | None = None, *, total_key: str = "total") -> dict:
    """Construye resumen compacto para UI."""
    catalog_by_id = catalog_by_id or {}
    rows = []
    total = 0.0
    qty = 0.0
    for cid, item in (ignored_linked or {}).items():
        row_total = float(item.get(total_key, 0) or 0)
        row_qty = float(item.get("qty", 0) or 0)
        total += row_total
        qty += row_qty
        catalog_item = catalog_by_id.get(cid) or {}
        rows.append({
            "catalog_item_id": cid,
            "nombre": catalog_item.get("nombre") or (item.get("descripciones") or [cid])[0] or cid,
            "unidad": catalog_item.get("unidad", ""),
            "qty": round(row_qty, 4),
            "total": round(row_total, 2),
        })
    rows.sort(key=lambda row: row["nombre"].casefold())
    return {"count": len(rows), "qty": round(qty, 4), "total": round(total, 2), "rows": rows}
