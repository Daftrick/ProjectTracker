from .catalog import quote_type_key
from .storage import today


def quote_default_numbers(project, quotes, quote_id=None):
    other_quotes = [item for item in quotes if item.get("id") != quote_id]
    general_quotes = [
        item
        for item in other_quotes
        if item["project_id"] == project["id"] and quote_type_key(item.get("quote_type")) == "General"
    ]
    preliminary_quotes = [
        item
        for item in other_quotes
        if item["project_id"] == project["id"] and quote_type_key(item.get("quote_type")) == "Preliminar"
    ]
    extraordinary_quotes = [
        item
        for item in other_quotes
        if item["project_id"] == project["id"] and quote_type_key(item.get("quote_type")) == "Extraordinaria"
    ]
    date_token = today().replace("-", "")
    return {
        "default_num_g": f"COT-{project['clave']}-G{len(general_quotes) + 1:02d}-{date_token}",
        "default_num_p": f"COT-{project['clave']}-P{len(preliminary_quotes) + 1:02d}-{date_token}",
        "default_num_e": f"COT-{project['clave']}-E{len(extraordinary_quotes) + 1:02d}-{date_token}",
    }


def quote_from_form(form, fallback_quote=None):
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
    items = []
    current_section = ""

    for index, description in enumerate(descs):
        kind = kinds[index] if index < len(kinds) else "item"
        raw_section = sections[index] if index < len(sections) else ""
        if kind == "section":
            current_section = raw_section.strip()
            continue
        section = raw_section.strip() or current_section
        qty = qtys[index] if index < len(qtys) else "1"
        price = prices[index] if index < len(prices) else "0"
        total = round(_to_float(qty, 0) * _to_float(price, 0), 2)
        parsed_item = {
            "catalog_item_id": catalog_ids[index].strip() if index < len(catalog_ids) else "",
            "description": description.strip(),
            "unit": units[index].strip() if index < len(units) else "pza",
            "qty": qty,
            "price": price,
            "total": total,
            "catalog_description": desc2s[index].strip() if index < len(desc2s) else "",
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
            parsed_item["deleted_catalog_item"] = deleted_catalog_item
        items.append(parsed_item)

    base = dict(fallback_quote or {})
    base.update({
        "quote_type": quote_type_key(form.get("quote_type", "General")),
        "quote_number": form.get("quote_number", "").strip(),
        "version": form.get("version", "").strip(),
        "date": form.get("date", "").strip(),
        "valid_until": form.get("valid_until", "").strip(),
        "currency": form.get("currency", "MXN").strip() or "MXN",
        "tax_rate": form.get("tax_rate", "16").strip() or "16",
        "notes": form.get("notes", "").strip(),
        "project_basis_note": form.get("project_basis_note", "").strip(),
        "items": items,
    })
    return base


def ldm_from_form(form, fallback_ldm=None):
    descs = form.getlist("item_desc[]")
    units = form.getlist("item_unit[]")
    qtys = form.getlist("item_qty[]")
    catalog_ids = form.getlist("item_catalog_id[]")
    deleted_ids = form.getlist("item_deleted_catalog_id[]")
    deleted_names = form.getlist("item_deleted_catalog_nombre[]")
    deleted_descriptions = form.getlist("item_deleted_catalog_descripcion[]")
    deleted_units = form.getlist("item_deleted_catalog_unidad[]")
    deleted_prices = form.getlist("item_deleted_catalog_precio[]")
    deleted_dates = form.getlist("item_deleted_catalog_deleted_at[]")
    items = []
    for index, description in enumerate(descs):
        parsed_item = {
            "catalog_item_id": catalog_ids[index].strip() if index < len(catalog_ids) else "",
            "description": description.strip(),
            "unit": units[index].strip() if index < len(units) else "pza",
            "qty": qtys[index] if index < len(qtys) else "1",
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
            parsed_item["deleted_catalog_item"] = deleted_catalog_item
        items.append(parsed_item)

    base = dict(fallback_ldm or {})
    base.update({
        "proveedor": form.get("proveedor", "").strip(),
        "fecha": form.get("fecha", "").strip(),
        "cot_proveedor": form.get("cot_proveedor", "").strip(),
        "notes": form.get("notes", "").strip(),
        "items": items,
    })
    return base


def _to_float(value, default=0):
    try:
        return float(str(value or "").replace(",", "."))
    except ValueError:
        return default


def _deleted_catalog_item_at(ids, names, descriptions, units, prices, deleted_dates, index):
    deleted_id = ids[index].strip() if index < len(ids) else ""
    if not deleted_id:
        return None
    return {
        "id": deleted_id,
        "nombre": names[index].strip() if index < len(names) else "",
        "descripcion": descriptions[index].strip() if index < len(descriptions) else "",
        "unidad": units[index].strip() if index < len(units) else "",
        "precio": _to_float(prices[index], 0) if index < len(prices) else 0,
        "deleted_at": deleted_dates[index].strip() if index < len(deleted_dates) else "",
    }
