import re
from datetime import datetime

from .catalog import catalog_maps, hydrate_ldm_item, hydrate_quote_item, quote_type_key

VALID_CURRENCIES = {"MXN", "USD", "EUR"}
PROJECT_DATE_RE = re.compile(r"^\d{6}$")


def _clean(value):
    return str(value or "").strip()


def _is_blank(value):
    return _clean(value) == ""


def _parse_float(value, field_label, errors, row=None, default=0.0, field_errors=None, field_key=None):
    raw = _clean(value)
    if raw == "":
        return default
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        prefix = f"Fila {row}: " if row else ""
        message = f"{prefix}{field_label} debe ser un número válido."
        errors.append(message)
        if field_errors is not None and field_key:
            field_errors.setdefault(field_key, message)
        return default


def _validate_iso_date(value, field_label, errors, field_errors=None, field_key=None):
    cleaned = _clean(value)
    if not cleaned:
        message = f"{field_label} es requerida."
        errors.append(message)
        if field_errors is not None and field_key:
            field_errors.setdefault(field_key, message)
        return ""
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        message = f"{field_label} debe tener formato AAAA-MM-DD."
        errors.append(message)
        if field_errors is not None and field_key:
            field_errors.setdefault(field_key, message)
    return cleaned


def _deleted_catalog_item_at(ids, names, descriptions, units, prices, deleted_dates, index):
    deleted_id = _clean(ids[index]) if index < len(ids) else ""
    if not deleted_id:
        return None
    return {
        "id": deleted_id,
        "nombre": _clean(names[index]) if index < len(names) else "",
        "descripcion": _clean(descriptions[index]) if index < len(descriptions) else "",
        "unidad": _clean(units[index]) if index < len(units) else "",
        "precio": _parse_float(prices[index], "precio de catálogo eliminado", [], default=0) if index < len(prices) else 0,
        "deleted_at": _clean(deleted_dates[index]) if index < len(deleted_dates) else "",
    }


def validate_project_form(form, selected_alcances, allowed_alcances):
    errors = []
    field_errors = {}
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
        message = "El nombre del proyecto es requerido."
        errors.append(message)
        field_errors["name"] = message
    if not fields["clave"]:
        message = "La clave del proyecto es requerida."
        errors.append(message)
        field_errors["clave"] = message
    if fields["fecha"] and not PROJECT_DATE_RE.match(fields["fecha"]):
        message = "La fecha del proyecto debe usar formato AAMMDD, por ejemplo 260424."
        errors.append(message)
        field_errors["fecha"] = message
    if not selected:
        message = "Selecciona al menos un alcance."
        errors.append(message)
        field_errors["alcances"] = message

    unknown = [alcance for alcance in selected if alcance not in allowed_alcances]
    if unknown:
        message = "Hay alcances no reconocidos en el formulario."
        errors.append(message)
        field_errors["alcances"] = message

    return {
        "ok": not errors,
        "errors": errors,
        "field_errors": field_errors,
        "fields": fields,
        "alcances": selected,
    }


def validate_quote_form(form):
    errors = []
    field_errors = {}
    tax_rate = _parse_float(
        form.get("tax_rate", 16),
        "IVA",
        errors,
        default=16,
        field_errors=field_errors,
        field_key="tax_rate",
    )
    if tax_rate < 0 or tax_rate > 100:
        message = "IVA debe estar entre 0 y 100."
        errors.append(message)
        field_errors.setdefault("tax_rate", message)

    currency = _clean(form.get("currency")) or "MXN"
    if currency not in VALID_CURRENCIES:
        message = "Moneda no reconocida."
        errors.append(message)
        field_errors["currency"] = message
        currency = "MXN"

    item_error_start = len(errors)
    items, subtotal = _parse_quote_items(form, errors)
    if not items:
        message = "Agrega al menos una partida a la cotización."
        errors.append(message)
        field_errors.setdefault("items", message)
    elif len(errors) > item_error_start:
        field_errors.setdefault("items", "Revisa las partidas marcadas por la validación.")
    date_value = _validate_iso_date(
        form.get("date"),
        "La fecha de la cotización",
        errors,
        field_errors=field_errors,
        field_key="date",
    )

    return {
        "ok": not errors,
        "errors": errors,
        "field_errors": field_errors,
        "quote_type": quote_type_key(form.get("quote_type", "General")),
        "quote_number": _clean(form.get("quote_number")),
        "version": _clean(form.get("version")),
        "date": date_value,
        "currency": currency,
        "tax_rate": tax_rate,
        "notes": _clean(form.get("notes")),
        "project_basis_note": _clean(form.get("project_basis_note")),
        "items": items,
        "subtotal": round(subtotal, 2),
    }


def validate_ldm_form(form):
    errors = []
    field_errors = {}
    proveedor = _clean(form.get("proveedor"))
    if not proveedor:
        message = "Proveedor es requerido."
        errors.append(message)
        field_errors["proveedor"] = message

    item_error_start = len(errors)
    items, subtotal_cot = _parse_ldm_items(form, errors)
    if not items:
        message = "Agrega al menos un artículo a la lista de materiales."
        errors.append(message)
        field_errors.setdefault("items", message)
    elif len(errors) > item_error_start:
        field_errors.setdefault("items", "Revisa los artículos marcados por la validación.")
    date_value = _validate_iso_date(
        form.get("fecha"),
        "La fecha de la lista",
        errors,
        field_errors=field_errors,
        field_key="fecha",
    )

    return {
        "ok": not errors,
        "errors": errors,
        "field_errors": field_errors,
        "proveedor": proveedor,
        "fecha": date_value,
        "items": items,
        "subtotal_cot": round(subtotal_cot, 2),
        "cot_proveedor": _clean(form.get("cot_proveedor")) or None,
        "notes": _clean(form.get("notes")),
    }


def _parse_quote_items(form, errors):
    kinds = form.getlist("item_kind[]")
    sections = form.getlist("item_section[]")
    descs = form.getlist("item_desc[]")
    desc2s = form.getlist("item_desc2[]")
    units = form.getlist("item_unit[]")
    qtys = form.getlist("item_qty[]")
    prices = form.getlist("item_price[]")
    catalog_ids = form.getlist("item_catalog_id[]")
    deleted_ids = form.getlist("item_deleted_catalog_id[]")
    deleted_names = form.getlist("item_deleted_catalog_nombre[]")
    deleted_descriptions = form.getlist("item_deleted_catalog_descripcion[]")
    deleted_units = form.getlist("item_deleted_catalog_unidad[]")
    deleted_prices = form.getlist("item_deleted_catalog_precio[]")
    deleted_dates = form.getlist("item_deleted_catalog_deleted_at[]")
    catalog_by_id, catalog_by_name = catalog_maps()
    items = []
    subtotal = 0.0
    current_section = ""

    for index, description in enumerate(descs):
        kind = _clean(kinds[index]) if index < len(kinds) else "item"
        raw_section = _clean(sections[index]) if index < len(sections) else ""
        if kind == "section":
            current_section = raw_section
            continue
        row = index + 1
        section = raw_section or current_section
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
            "section": section,
        }
        deleted_catalog_item = _deleted_catalog_item_at(
            deleted_ids,
            deleted_names,
            deleted_descriptions,
            deleted_units,
            deleted_prices,
            deleted_dates,
            index,
        )
        if deleted_catalog_item:
            raw_item["deleted_catalog_item"] = deleted_catalog_item
        hydrated = hydrate_quote_item(raw_item, catalog_by_id, catalog_by_name, infer_by_name=False)
        parsed_item = {
            "catalog_item_id": hydrated.get("catalog_item_id", ""),
            "description": hydrated["description"],
            "unit": hydrated["unit"] or "pza",
            "qty": hydrated["qty"],
            "price": hydrated["price"],
            "total": hydrated["total"],
            "catalog_description": hydrated.get("catalog_description", ""),
            "section": hydrated.get("section", ""),
        }
        if hydrated.get("deleted_catalog_item"):
            parsed_item["deleted_catalog_item"] = hydrated["deleted_catalog_item"]
        items.append(parsed_item)
        subtotal += hydrated["total"]

    return items, subtotal


def _parse_ldm_items(form, errors):
    descs = form.getlist("item_desc[]")
    units = form.getlist("item_unit[]")
    qtys = form.getlist("item_qty[]")
    prices = form.getlist("item_precio_cot[]")
    catalog_ids = form.getlist("item_catalog_id[]")
    deleted_ids = form.getlist("item_deleted_catalog_id[]")
    deleted_names = form.getlist("item_deleted_catalog_nombre[]")
    deleted_descriptions = form.getlist("item_deleted_catalog_descripcion[]")
    deleted_units = form.getlist("item_deleted_catalog_unidad[]")
    deleted_prices = form.getlist("item_deleted_catalog_precio[]")
    deleted_dates = form.getlist("item_deleted_catalog_deleted_at[]")
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
        deleted_catalog_item = _deleted_catalog_item_at(
            deleted_ids,
            deleted_names,
            deleted_descriptions,
            deleted_units,
            deleted_prices,
            deleted_dates,
            index,
        )
        if deleted_catalog_item:
            raw_item["deleted_catalog_item"] = deleted_catalog_item
        hydrated = hydrate_ldm_item(raw_item, catalog_by_id, catalog_by_name, infer_by_name=False)
        parsed_item = {
            "catalog_item_id": hydrated.get("catalog_item_id", ""),
            "description": hydrated["description"],
            "unit": hydrated["unit"] or "pza",
            "qty": hydrated["qty"],
            "precio_cot": hydrated.get("precio_cot", 0.0),
            "total_cot": hydrated.get("total_cot", 0.0),
        }
        if hydrated.get("deleted_catalog_item"):
            parsed_item["deleted_catalog_item"] = hydrated["deleted_catalog_item"]
        items.append(parsed_item)
        subtotal += hydrated.get("total_cot", 0.0)

    return items, subtotal
