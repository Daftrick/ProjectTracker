import csv

from .catalog import catalog_name_key

_ENCODING_ERROR = (
    "El CSV tiene codificación no compatible (posiblemente ANSI/cp1252). "
    "Verifica que AutoCAD pudo escribir el archivo en UTF-8. "
    "Si el problema persiste, abre el CSV en un editor de texto y guárdalo como UTF-8."
)


QUOTE_DESCRIPTION_COLUMNS = (
    "description",
    "descripcion",
    "descripción",
    "nombre",
    "concepto",
    "partida",
    "item",
    "articulo",
    "artículo",
)
QUOTE_UNIT_COLUMNS = ("unit", "unidad", "u")
QUOTE_QTY_COLUMNS = ("qty", "cantidad", "cant", "quantity")
QUOTE_PRICE_COLUMNS = (
    "price",
    "precio",
    "precio_unitario",
    "precio unitario",
    "unit_price",
    "pu",
    "p.u.",
)
QUOTE_SECTION_COLUMNS = ("section", "seccion", "sección", "categoria", "categoría", "grupo")


def _clean(value):
    return str(value or "").strip()


def _header_key(value):
    return _clean(value).lower().lstrip("\ufeff")


def _read_sample(path):
    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            return handle.read(4096)
    except UnicodeDecodeError:
        return None


def _detect_dialect(path):
    sample = _read_sample(path)
    if not sample:
        return csv.excel
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;")
    except csv.Error:
        return csv.excel


def _parse_float(value, row_number, field_label, errors, required=False, default=0.0):
    raw = _clean(value).replace(",", ".")
    if not raw:
        if required:
            errors.append(f"Fila {row_number}: {field_label} es requerida.")
        return default
    try:
        return float(raw)
    except ValueError:
        errors.append(f"Fila {row_number}: {field_label} debe ser un numero valido.")
        return default


def _metadata_value(row):
    values = [_clean(value) for value in row]
    return next((value for value in values[1:] if value), "")


def _build_catalog_index(catalog):
    index = {}
    for item in catalog or []:
        key = catalog_name_key(item.get("nombre", ""))
        if key and key not in index:
            index[key] = item
    return index


def _match_catalog(description, index):
    return index.get(catalog_name_key(description))


def _column_index(headers, aliases):
    for index, header in enumerate(headers):
        if _header_key(header) in aliases:
            return index
    return None


def _row_value(row, index):
    if index is None or index >= len(row):
        return ""
    return _clean(row[index])


def _find_header_row(rows, metadata):
    for index, row in enumerate(rows):
        if not any(_clean(value) for value in row):
            continue
        first = _clean(row[0])
        if first.startswith("#"):
            metadata[first.lstrip("#").strip().lower()] = _metadata_value(row)
            continue
        return index
    return None


def parse_quote_csv(path, catalog=None):
    """Parse a LISP-exported client quote CSV into quote draft data."""
    dialect = _detect_dialect(path)
    catalog_index = _build_catalog_index(catalog)
    metadata = {}
    items = []
    errors = []
    warnings = []

    try:
        with open(path, "r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.reader(handle, dialect=dialect))
    except UnicodeDecodeError:
        return {"items": [], "metadata": {}, "errors": [_ENCODING_ERROR], "warnings": []}

    header_row = _find_header_row(rows, metadata)
    if header_row is None:
        return {"items": [], "metadata": metadata, "errors": ["El CSV no tiene encabezados."], "warnings": []}

    headers = [_header_key(value) for value in rows[header_row]]
    description_index = _column_index(headers, QUOTE_DESCRIPTION_COLUMNS)
    unit_index = _column_index(headers, QUOTE_UNIT_COLUMNS)
    qty_index = _column_index(headers, QUOTE_QTY_COLUMNS)
    price_index = _column_index(headers, QUOTE_PRICE_COLUMNS)
    section_index = _column_index(headers, QUOTE_SECTION_COLUMNS)

    if description_index is None:
        errors.append("El CSV debe incluir una columna description o descripcion.")
    if qty_index is None:
        errors.append("El CSV debe incluir una columna qty o cantidad.")
    if errors:
        return {"items": [], "metadata": metadata, "errors": errors, "warnings": warnings}

    seen = {}
    for zero_based_index, row in enumerate(rows[header_row + 1:], start=header_row + 1):
        row_number = zero_based_index + 1
        if not any(_clean(value) for value in row):
            continue
        first = _clean(row[0])
        if first.startswith("#"):
            metadata[first.lstrip("#").strip().lower()] = _metadata_value(row)
            continue

        description = _row_value(row, description_index)
        unit = _row_value(row, unit_index) or "pza"
        qty = _parse_float(_row_value(row, qty_index), row_number, "cantidad", errors, required=True)
        price = _parse_float(_row_value(row, price_index), row_number, "precio unitario", errors, default=0.0)
        section = _row_value(row, section_index)

        if not description:
            errors.append(f"Fila {row_number}: descripcion es requerida.")
            continue
        if qty <= 0:
            errors.append(f"Fila {row_number}: cantidad debe ser mayor a 0.")
        if price < 0:
            errors.append(f"Fila {row_number}: precio unitario no puede ser negativo.")

        catalog_item = _match_catalog(description, catalog_index)
        key = (catalog_name_key(description), unit.lower())
        seen[key] = seen.get(key, 0) + 1
        items.append({
            "description": description,
            "unit": unit,
            "qty": qty,
            "price": price,
            "total": round(qty * price, 2),
            "catalog_item_id": catalog_item.get("id", "") if catalog_item else "",
            "catalog_description": catalog_item.get("descripcion", "") if catalog_item else "",
            "section": section,
            "origen": "csv",
        })

    duplicate_count = sum(1 for count in seen.values() if count > 1)
    if duplicate_count:
        warnings.append(f"{duplicate_count} concepto(s) aparecen mas de una vez con la misma unidad.")
    if not items and not errors:
        errors.append("El CSV no contiene partidas para importar.")
    return {"items": items, "metadata": metadata, "errors": errors, "warnings": warnings}
