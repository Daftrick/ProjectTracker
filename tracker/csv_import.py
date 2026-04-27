import csv


LDM_DESCRIPTION_COLUMNS = ("description", "descripcion", "descripción", "nombre", "item", "articulo", "artículo")
LDM_UNIT_COLUMNS = ("unit", "unidad", "u")
LDM_QTY_COLUMNS = ("qty", "cantidad", "cant", "quantity")


def _clean(value):
    return str(value or "").strip()


def _header_key(value):
    return _clean(value).lower().lstrip("\ufeff")


def _first_value(row, aliases):
    for key, value in row.items():
        if _header_key(key) in aliases:
            return _clean(value)
    return ""


def _parse_float(value, row_number, errors):
    raw = _clean(value).replace(",", ".")
    if not raw:
        errors.append(f"Fila {row_number}: cantidad es requerida.")
        return 0.0
    try:
        return float(raw)
    except ValueError:
        errors.append(f"Fila {row_number}: cantidad debe ser un número válido.")
        return 0.0


def _read_sample(path):
    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        return handle.read(4096)


def _detect_dialect(path):
    sample = _read_sample(path)
    if not sample:
        return csv.excel
    try:
        return csv.Sniffer().sniff(sample, delimiters=",;")
    except csv.Error:
        return csv.excel


def parse_ldm_csv(path):
    """Parse a LISP-exported material list CSV into LDM draft data."""
    dialect = _detect_dialect(path)
    items = []
    metadata = {}
    errors = []

    with open(path, "r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, dialect=dialect)
        if not reader.fieldnames:
            return {"items": [], "metadata": {}, "errors": ["El CSV no tiene encabezados."]}

        headers = {_header_key(name) for name in reader.fieldnames}
        if not headers.intersection(LDM_DESCRIPTION_COLUMNS):
            errors.append("El CSV debe incluir una columna description o descripcion.")
        if not headers.intersection(LDM_QTY_COLUMNS):
            errors.append("El CSV debe incluir una columna qty o cantidad.")
        if errors:
            return {"items": [], "metadata": {}, "errors": errors}

        for row_number, row in enumerate(reader, start=2):
            description = _first_value(row, LDM_DESCRIPTION_COLUMNS)
            unit = _first_value(row, LDM_UNIT_COLUMNS) or "pza"
            qty_raw = _first_value(row, LDM_QTY_COLUMNS)
            if not any(_clean(value) for value in row.values()):
                continue
            if description.startswith("#"):
                key = description.lstrip("#").strip().lower()
                values = [_clean(value) for value in row.values()]
                metadata[key] = next((value for value in values[1:] if value), "")
                continue
            if not description:
                errors.append(f"Fila {row_number}: descripción es requerida.")
                continue
            qty = _parse_float(qty_raw, row_number, errors)
            if qty <= 0:
                errors.append(f"Fila {row_number}: cantidad debe ser mayor a 0.")
            items.append({
                "description": description,
                "unit": unit,
                "qty": qty,
                "precio_cot": 0.0,
                "total_cot": 0.0,
                "qty_csv": qty,
                "qty_editada": False,
                "origen": "csv",
            })

    if not items and not errors:
        errors.append("El CSV no contiene artículos para importar.")
    return {"items": items, "metadata": metadata, "errors": errors}
