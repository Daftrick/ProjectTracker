"""Bundles versionados para comparar COT contra LDM técnica.

Un bundle permite que un artículo comercial de COT (por ejemplo una salida
eléctrica) se expanda a componentes de catálogo esperados en LDM. Este módulo
no hace I/O; recibe estructuras ya cargadas desde JSON para mantener pruebas
simples y evitar acoplar la lógica al almacenamiento.
"""

from __future__ import annotations

from typing import Iterable

DEFAULT_BUNDLE_STATUS = "draft"
STATUS_DRAFT = "draft"
STATUS_ACTIVE = "active"
STATUS_ARCHIVED = "archived"


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: float, places: int = 4) -> float:
    return round(value, places)


def _clean(value) -> str:
    return str(value or "").strip()


def normalize_bundle(bundle: dict) -> dict:
    """Devuelve una copia normalizada de un bundle.

    La función tolera bundles incompletos para migraciones suaves: llena
    `versions`, `active_version`, estados y arreglos de componentes faltantes.
    """
    current = dict(bundle or {})
    versions = current.get("versions") or []
    normalized_versions = []
    for index, version in enumerate(versions, start=1):
        v = dict(version or {})
        vnum = int(_safe_float(v.get("version"), index))
        v["version"] = vnum
        v["label"] = _clean(v.get("label")) or f"Versión {vnum}"
        v["status"] = _clean(v.get("status")) or DEFAULT_BUNDLE_STATUS
        v["notes"] = _clean(v.get("notes"))
        v["components"] = [normalize_component(c) for c in (v.get("components") or [])]
        normalized_versions.append(v)

    current["versions"] = normalized_versions
    if not current.get("active_version") and normalized_versions:
        active = next((v for v in normalized_versions if v.get("status") == STATUS_ACTIVE), normalized_versions[0])
        current["active_version"] = active["version"]
    return current


def normalize_component(component: dict) -> dict:
    """Normaliza un componente de bundle."""
    current = dict(component or {})
    current["catalog_item_id"] = _clean(current.get("catalog_item_id"))
    current["qty"] = _safe_float(current.get("qty"))
    current["waste_pct"] = _safe_float(current.get("waste_pct"))
    current["comparison_rule_id"] = _clean(current.get("comparison_rule_id"))
    current["notes"] = _clean(current.get("notes"))
    return current


def get_active_bundle_version(bundle: dict) -> dict | None:
    """Obtiene la versión activa de un bundle."""
    current = normalize_bundle(bundle)
    versions = current.get("versions") or []
    if not versions:
        return None
    active_version = int(_safe_float(current.get("active_version")))
    if active_version:
        found = next((v for v in versions if int(v.get("version", 0)) == active_version), None)
        if found:
            return found
    return next((v for v in versions if v.get("status") == STATUS_ACTIVE), versions[0])


def bundle_by_catalog_item_id(bundles: Iterable[dict]) -> dict[str, dict]:
    """Indexa bundles por el artículo comercial de catálogo usado en COT."""
    indexed: dict[str, dict] = {}
    for bundle in bundles or []:
        current = normalize_bundle(bundle)
        cid = _clean(current.get("catalog_item_id"))
        if cid:
            indexed[cid] = current
    return indexed


def next_bundle_version(bundle: dict) -> int:
    """Calcula el siguiente número de versión para un bundle existente."""
    versions = (bundle or {}).get("versions") or []
    max_version = 0
    for version in versions:
        max_version = max(max_version, int(_safe_float(version.get("version"))))
    return max_version + 1


def create_bundle(catalog_item_id: str, name: str, components: list[dict] | None = None, *, bundle_id: str = "") -> dict:
    """Crea una estructura de bundle con versión 1 activa.

    El ID final puede asignarlo la ruta/servicio con `new_id()`; este helper
    permite pruebas sin depender de almacenamiento.
    """
    return {
        "id": _clean(bundle_id),
        "catalog_item_id": _clean(catalog_item_id),
        "name": _clean(name),
        "active_version": 1,
        "versions": [
            {
                "version": 1,
                "label": "Versión 1",
                "status": STATUS_ACTIVE,
                "notes": "",
                "components": [normalize_component(c) for c in (components or [])],
            }
        ],
    }


def add_bundle_version(bundle: dict, components: list[dict] | None = None, *, label: str = "", notes: str = "", make_active: bool = False) -> dict:
    """Agrega una versión al bundle y devuelve una copia actualizada."""
    current = normalize_bundle(bundle)
    new_version = next_bundle_version(current)
    current.setdefault("versions", []).append({
        "version": new_version,
        "label": _clean(label) or f"Versión {new_version}",
        "status": STATUS_ACTIVE if make_active else STATUS_DRAFT,
        "notes": _clean(notes),
        "components": [normalize_component(c) for c in (components or [])],
    })
    if make_active:
        current = activate_bundle_version(current, new_version)
    return current


def activate_bundle_version(bundle: dict, version_number: int) -> dict:
    """Activa una versión y archiva la versión activa anterior."""
    current = normalize_bundle(bundle)
    target = int(version_number)
    found = False
    for version in current.get("versions", []):
        if int(version.get("version", 0)) == target:
            version["status"] = STATUS_ACTIVE
            found = True
        elif version.get("status") == STATUS_ACTIVE:
            version["status"] = STATUS_ARCHIVED
    if not found:
        raise ValueError(f"No existe la versión {target} del bundle")
    current["active_version"] = target
    return current


def delete_bundle_version(bundle: dict, version_number: int) -> dict:
    """Elimina una versión si no es la única disponible."""
    current = normalize_bundle(bundle)
    versions = current.get("versions", [])
    if len(versions) <= 1:
        raise ValueError("No se puede eliminar la única versión del bundle")
    target = int(version_number)
    filtered = [v for v in versions if int(v.get("version", 0)) != target]
    if len(filtered) == len(versions):
        raise ValueError(f"No existe la versión {target} del bundle")
    current["versions"] = filtered
    if int(_safe_float(current.get("active_version"))) == target:
        current = activate_bundle_version(current, int(filtered[-1].get("version")))
    return current


def expand_quote_bundles(quote: dict | None, bundles: Iterable[dict], catalog_by_id: dict | None = None) -> dict:
    """Expande las partidas COT con bundle a materiales esperados.

    Retorna un diccionario con:
    - `items`: componentes esperados agregados por catalog_item_id
    - `bundle_rows`: detalle de qué partida COT generó cada componente
    - `bundle_quote_items`: partidas COT que sí tuvieron bundle
    - `unmapped_quote_items`: partidas COT sin bundle (no son error por sí mismas)
    - `invalid_components`: componentes sin catalog_item_id o cantidad válida
    """
    catalog_by_id = catalog_by_id or {}
    bundle_index = bundle_by_catalog_item_id(bundles)
    expected: dict[str, dict] = {}
    bundle_rows: list[dict] = []
    bundle_quote_items: list[dict] = []
    unmapped_quote_items: list[dict] = []
    invalid_components: list[dict] = []

    for item in (quote or {}).get("items", []) or []:
        item_cid = _clean(item.get("catalog_item_id"))
        quote_qty = _safe_float(item.get("qty"))
        bundle = bundle_index.get(item_cid)
        if not bundle:
            unmapped_quote_items.append(item)
            continue
        active_version = get_active_bundle_version(bundle)
        if not active_version:
            invalid_components.append({
                "bundle_catalog_item_id": item_cid,
                "reason": "bundle_without_active_version",
                "quote_item": item,
            })
            continue
        bundle_quote_items.append({
            "catalog_item_id": item_cid,
            "description": item.get("description") or bundle.get("name") or item_cid,
            "qty": quote_qty,
            "bundle_id": bundle.get("id", ""),
            "bundle_version": active_version.get("version"),
        })
        for component in active_version.get("components", []) or []:
            comp = normalize_component(component)
            comp_cid = comp["catalog_item_id"]
            comp_qty = comp["qty"]
            waste_pct = comp["waste_pct"]
            if not comp_cid or comp_qty <= 0:
                invalid_components.append({
                    "bundle_catalog_item_id": item_cid,
                    "bundle_version": active_version.get("version"),
                    "component": comp,
                    "reason": "invalid_component",
                })
                continue
            expected_qty = quote_qty * comp_qty * (1 + waste_pct / 100.0)
            bucket = expected.setdefault(comp_cid, {
                "catalog_item_id": comp_cid,
                "nombre": (catalog_by_id.get(comp_cid) or {}).get("nombre", comp_cid),
                "unidad": (catalog_by_id.get(comp_cid) or {}).get("unidad", ""),
                "qty": 0.0,
                "sources": [],
            })
            bucket["qty"] += expected_qty
            source = {
                "bundle_catalog_item_id": item_cid,
                "bundle_name": bundle.get("name") or item.get("description") or item_cid,
                "bundle_version": active_version.get("version"),
                "quote_qty": quote_qty,
                "component_qty": comp_qty,
                "waste_pct": waste_pct,
                "expected_qty": _round(expected_qty),
                "notes": comp.get("notes", ""),
                "comparison_rule_id": comp["comparison_rule_id"],
            }
            bucket["sources"].append(source)
            bundle_rows.append({"component_catalog_item_id": comp_cid, **source})

    for bucket in expected.values():
        bucket["qty"] = _round(bucket["qty"])
    return {
        "items": expected,
        "bundle_rows": bundle_rows,
        "bundle_quote_items": bundle_quote_items,
        "unmapped_quote_items": unmapped_quote_items,
        "invalid_components": invalid_components,
    }
