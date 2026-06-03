from .catalog import catalog_name_key


def _clean(value):
    return str(value or "").strip()


def _unit_key(value):
    return _clean(value).lower()


def _catalog_index(catalog):
    index = {}
    for item in catalog or []:
        key = catalog_name_key(item.get("nombre", ""))
        if key and key not in index:
            index[key] = item
    return index


def validate_csv_catalog_items(items, catalog, kind="CSV"):
    """Validate parsed CSV rows against catalog name and unit.

    Matching intentionally mirrors ProjectTracker hydration: names are compared
    with catalog_name_key, while units must match exactly after trim/lower.
    """
    catalog_by_name = _catalog_index(catalog)
    errors = []
    label = _clean(kind) or "CSV"

    for index, item in enumerate(items or [], start=1):
        row_number = item.get("csv_row_number") or index
        row_label = f"Fila {row_number}"
        description = _clean(item.get("description", ""))
        unit = _clean(item.get("unit", ""))

        if not description:
            errors.append(f"{row_label}: descripción vacía en {label}.")
            continue

        catalog_item = catalog_by_name.get(catalog_name_key(description))
        if not catalog_item:
            errors.append(
                f'{row_label}: "{description}" no tiene coincidencia exacta en catálogo.'
            )
            continue

        catalog_unit = _clean(catalog_item.get("unidad", ""))
        if not catalog_unit:
            errors.append(
                f'{row_label}: el artículo de catálogo "{catalog_item.get("nombre", description)}" no tiene unidad configurada.'
            )
            continue

        if _unit_key(unit) != _unit_key(catalog_unit):
            errors.append(
                f'{row_label}: unidad incompatible para "{description}". CSV="{unit}", catálogo="{catalog_unit}".'
            )

    return {"ok": not errors, "errors": errors}
