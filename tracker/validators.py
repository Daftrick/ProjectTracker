import re
from datetime import datetime

from .catalog import catalog_maps, hydrate_ldm_item, hydrate_quote_item, quote_type_key

VALID_CURRENCIES = {"MXN", "USD", "EUR"}
PROJECT_DATE_RE = re.compile(r"^\d{6}$")


def _clean(value):
    return str(value or "").strip()


def _is_blank(value):
    return _clean(value) == ""


def _parse_float(value, field_label, errors, row=None, default=0.0):
    raw = _clean(value)
    if raw == "":
        return default
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        prefix = f"Fila {row}: " if row else ""
        errors.append(f"{prefix}{field_label} debe ser un número válido.")
        return default


def _validate_iso_date(value, field_label, errors):
    cleaned = _clean(value)
    if not cleaned:
        errors.append(f"{field_label} es requerida.")
        return ""
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        errors.append(f"{field_label} debe tener formato AAAA-MM-DD.")
    return cleaned


def validate_project_form(form, selected_alcances, allowed_alcances):
    errors = []
    fields = {
        "name": _clean(form.get("name")),
        "clave": _clean(form.get("clave")),
        "client": _clean(form.get("client")),
        "version": _clean(form.get("version")) or "V1",
        "fecha": _clean(form.get("fecha")),
        "notes": _clean(form.get("notes")),
    }
    selected = [_clean(item) for item in selected_alcances if _clean(item)]

    if not fields["name"]:
        errors.append("El nombre del proyecto es requerido.")
    if not fields["clave"]:
        errors.append("La clave del proyecto es requerida.")
    if fields["fecha"] and not PROJECT_DATE_RE.match(fields["fecha"]):
        errors.append("La fecha del proyecto debe usar formato AAMMDD, por ejemplo 260424.")
    if not selected:
        errors.append("Selecciona al menos un alcance.")

    unknown = [alcance for alcance in selected if alcance not in allowed_alcances]
    if unknown:
        errors.append("Hay alcances no reconocidos en el formulario.")

    return {"ok": not errors, "errors": errors, "fields": fields, "alcances": selected}


def validate_quote_form(form):
    errors = []
    tax_rate = _parse_float(form.get("tax_rate", 16), "IVA", errors, default=16)
    if tax_rate < 0 or tax_rate > 100:
        errors.append("IVA debe estar entre 0 y 100.")

    currency = _clean(form.get("currency")) or "MXN"
    if currency not in VALID_CURRENCIES:
        errors.append("Moneda no reconocida.")
        currency = "MXN"

    items, subtotal = _parse_quote_items(form, errors)
    if not items:
        errors.append("Agrega al menos una partida a la cotización.")
    date_value = _validate_iso_date(form.get("date"), "La fecha de la cotización", errors)

    return {
        "ok": not errors,
        "errors": errors,
        "quote_type": quote_type_key(form.get("quote_type", "General")),
        "quote_number": _clean(form.get("quote_number")),
        "version": _clean(form.get("version")),
        "date": date_value,
        "currency": currency,
        "tax_rate": tax_rate,
        "notes": _clean(form.get("notes")),
        "items": items,
        "subtotal": round(subtotal, 2),
    }


def validate_ldm_form(form):
    errors = []
    proveedor = _clean(form.get("proveedor"))
    if not proveedor:
        errors.append("Proveedor es requerido.")

    items, subtotal_cot = _parse_ldm_items(form, errors)
    if not items:
        errors.append("Agrega al menos un artículo a la lista de materiales.")
    date_value = _validate_iso_date(form.get("fecha"), "La fecha de la lista", errors)

    return {
        "ok": not errors,
        "errors": errors,
        "proveedor": proveedor,
        "fecha": date_value,
        "items": items,
        "subtotal_cot": round(subtotal_cot, 2),
        "cot_proveedor": _clean(form.get("cot_proveedor")) or None,
        "notes": _clean(form.get("notes")),
    }


def _parse_quote_items(form, errors):
    descs = form.getlist("item_desc[]")
    desc2s = form.getlist("item_desc2[]")
    units = form.getlist("item_unit[]")
    qtys = form.getlist("item_qty[]")
    prices = form.getlist("item_price[]")
    catalog_ids = form.getlist("item_catalog_id[]")
    catalog_by_id, catalog_by_name = catalog_maps()
    items = []
    subtotal = 0.0

    for index, description in enumerate(descs):
        row = index + 1
        raw_qty = qtys[index] if index < len(qtys) else ""
        raw_price = prices[index] if index < len(prices) else ""
        has_values = (
            not _is_blank(description)
            or (index < len(desc2s) and not _is_blank(desc2s[index]))
            or (index < len(catalog_ids) and not _is_blank(catalog_ids[index]))
            or _clean(raw_price) not in {"", "0", "0.0", "0.00"}
            or _clean(raw_qty) not in {"", "1", "1.0", "1.00"}
        )
        if not has_values:
            continue
        if _is_blank(description):
            errors.append(f"Fila {row}: descripción es requerida.")
            continue

        qty = _parse_float(raw_qty, "cantidad", errors, row=row)
        price = _parse_float(raw_price, "precio unitario", errors, row=row)
        if qty <= 0:
            errors.append(f"Fila {row}: cantidad debe ser mayor a 0.")
        if price < 0:
            errors.append(f"Fila {row}: precio unitario no puede ser negativo.")

        raw_item = {
            "catalog_item_id": _clean(catalog_ids[index]) if index < len(catalog_ids) else "",
            "description": _clean(description),
            "unit": _clean(units[index]) if index < len(units) else "pza",
            "qty": qty,
            "price": price,
            "catalog_description": _clean(desc2s[index]) if index < len(desc2s) else "",
        }
        hydrated = hydrate_quote_item(raw_item, catalog_by_id, catalog_by_name, infer_by_name=False)
        items.append({
            "catalog_item_id": hydrated.get("catalog_item_id", ""),
            "description": hydrated["description"],
            "unit": hydrated["unit"] or "pza",
            "qty": hydrated["qty"],
            "price": hydrated["price"],
            "total": hydrated["total"],
            "catalog_description": hydrated.get("catalog_description", ""),
        })
        subtotal += hydrated["total"]

    return items, subtotal


def _parse_ldm_items(form, errors):
    descs = form.getlist("item_desc[]")
    units = form.getlist("item_unit[]")
    qtys = form.getlist("item_qty[]")
    prices = form.getlist("item_precio_cot[]")
    catalog_ids = form.getlist("item_catalog_id[]")
    catalog_by_id, catalog_by_name = catalog_maps()
    items = []
    subtotal = 0.0

    for index, description in enumerate(descs):
        row = index + 1
        raw_qty = qtys[index] if index < len(qtys) else ""
        raw_price = prices[index] if index < len(prices) else ""
        has_values = (
            not _is_blank(description)
            or (index < len(catalog_ids) and not _is_blank(catalog_ids[index]))
            or _clean(raw_price) not in {"", "0", "0.0", "0.00"}
            or _clean(raw_qty) not in {"", "1", "1.0", "1.00"}
        )
        if not has_values:
            continue
        if _is_blank(description):
            errors.append(f"Fila {row}: descripción es requerida.")
            continue

        qty = _parse_float(raw_qty, "cantidad", errors, row=row, default=1)
        price = _parse_float(raw_price, "precio cotizado", errors, row=row)
        if qty <= 0:
            errors.append(f"Fila {row}: cantidad debe ser mayor a 0.")
        if price < 0:
            errors.append(f"Fila {row}: precio cotizado no puede ser negativo.")

        raw_item = {
            "catalog_item_id": _clean(catalog_ids[index]) if index < len(catalog_ids) else "",
            "description": _clean(description),
            "unit": _clean(units[index]) if index < len(units) else "pza",
            "qty": qty,
            "precio_cot": price,
        }
        hydrated = hydrate_ldm_item(raw_item, catalog_by_id, catalog_by_name, infer_by_name=False)
        items.append({
            "catalog_item_id": hydrated.get("catalog_item_id", ""),
            "description": hydrated["description"],
            "unit": hydrated["unit"] or "pza",
            "qty": hydrated["qty"],
            "precio_cot": hydrated.get("precio_cot", 0.0),
            "total_cot": hydrated.get("total_cot", 0.0),
        })
        subtotal += hydrated.get("total_cot", 0.0)

    return items, subtotal
