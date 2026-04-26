from flask import request

from .storage import load, today


QUOTE_TYPE_GENERAL = "General"
QUOTE_TYPE_PRELIMINAR = "Preliminar"
QUOTE_TYPE_EXTRAORDINARIA = "Extraordinaria"

QUOTE_TYPE_ALIASES = {
    "general": QUOTE_TYPE_GENERAL,
    "preliminar": QUOTE_TYPE_PRELIMINAR,
    "extraordinaria": QUOTE_TYPE_EXTRAORDINARIA,
    "extraordinario": QUOTE_TYPE_EXTRAORDINARIA,
}

QUOTE_TYPE_CODES = {
    QUOTE_TYPE_GENERAL: "G",
    QUOTE_TYPE_PRELIMINAR: "P",
    QUOTE_TYPE_EXTRAORDINARIA: "E",
}


def quote_type_key(value):
    raw = str(value or QUOTE_TYPE_GENERAL).strip()
    return QUOTE_TYPE_ALIASES.get(raw.lower(), QUOTE_TYPE_GENERAL)


def quote_type_code(value):
    return QUOTE_TYPE_CODES[quote_type_key(value)]


def catalog_name_key(text):
    return " ".join(sanitize_pdf_text(text).lower().split())


def catalog_description_lookup():
    lookup = {}
    for item in load("catalogo"):
        key = catalog_name_key(item.get("nombre", ""))
        if key:
            lookup[key] = item.get("descripcion", "").strip()
    return lookup


def catalog_maps():
    by_id = {}
    by_name = {}
    for item in load("catalogo"):
        item_id = str(item.get("id", "")).strip()
        if item_id:
            by_id[item_id] = item
        key = catalog_name_key(item.get("nombre", ""))
        if key and key not in by_name:
            by_name[key] = item
    return by_id, by_name


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def resolve_catalog_binding(item, catalog_by_id, catalog_by_name, text_key, infer_by_name=True):
    catalog_item_id = str(item.get("catalog_item_id", "")).strip()
    if catalog_item_id:
        return catalog_item_id, catalog_by_id.get(catalog_item_id)
    if not infer_by_name:
        return "", None
    key = catalog_name_key(item.get(text_key, ""))
    catalog_item = catalog_by_name.get(key) if key else None
    return (catalog_item.get("id", "").strip() if catalog_item else ""), catalog_item


def quote_item_catalog_description(item):
    return (
        item.get("catalog_description")
        or item.get("description_secondary")
        or item.get("descripcion")
        or ""
    ).strip()


def quote_item_section(item):
    return str(item.get("section") or item.get("category") or item.get("group") or "").strip()


def quote_section_groups(items):
    groups = []
    for item in items:
        section = quote_item_section(item)
        if not groups or groups[-1]["name"] != section:
            groups.append({"name": section, "items": [], "subtotal": 0.0})
        groups[-1]["items"].append(item)
        groups[-1]["subtotal"] = round(groups[-1]["subtotal"] + safe_float(item.get("total", 0)), 2)
    return groups


def hydrate_quote_item(item, catalog_by_id, catalog_by_name, infer_by_name=True):
    hydrated = dict(item)
    stored_price = safe_float(hydrated.get("price", item.get("price", 0) if isinstance(item, dict) else 0))
    catalog_item_id, catalog_item = resolve_catalog_binding(
        hydrated, catalog_by_id, catalog_by_name, "description", infer_by_name=infer_by_name
    )
    if catalog_item:
        hydrated["catalog_item_id"] = catalog_item_id
        hydrated["description"] = catalog_item.get("nombre", hydrated.get("description", ""))
        hydrated["unit"] = catalog_item.get("unidad", hydrated.get("unit", "pza"))
        hydrated["price"] = stored_price
        hydrated["catalog_description"] = catalog_item.get("descripcion", "").strip()
        hydrated["catalog_linked"] = True
        hydrated["catalog_missing"] = False
    else:
        if catalog_item_id:
            hydrated["catalog_item_id"] = catalog_item_id
        hydrated["catalog_description"] = quote_item_catalog_description(hydrated)
        hydrated["catalog_linked"] = False
        hydrated["catalog_missing"] = bool(catalog_item_id)
        hydrated["price"] = stored_price
    hydrated["section"] = quote_item_section(hydrated)
    hydrated["qty"] = safe_float(hydrated.get("qty", 0))
    hydrated["total"] = round(hydrated["qty"] * hydrated["price"], 2)
    return hydrated


def hydrate_quote(quote, catalog_by_id=None, catalog_by_name=None):
    catalog_by_id = catalog_by_id if catalog_by_id is not None else {}
    catalog_by_name = catalog_by_name if catalog_by_name is not None else {}
    hydrated = dict(quote)
    hydrated["items"] = [hydrate_quote_item(item, catalog_by_id, catalog_by_name) for item in quote.get("items", [])]
    tax_rate = safe_float(hydrated.get("tax_rate", 16), 16)
    subtotal = round(sum(item.get("total", 0) for item in hydrated["items"]), 2)
    hydrated["tax_rate"] = tax_rate
    hydrated["subtotal"] = subtotal
    hydrated["tax"] = round(subtotal * tax_rate / 100, 2)
    hydrated["total"] = round(subtotal + hydrated["tax"], 2)
    hydrated["sections"] = quote_section_groups(hydrated["items"])
    return hydrated


def hydrate_ldm_item(item, catalog_by_id, catalog_by_name, infer_by_name=True):
    hydrated = dict(item)
    catalog_item_id, catalog_item = resolve_catalog_binding(
        hydrated, catalog_by_id, catalog_by_name, "description", infer_by_name=infer_by_name
    )
    if catalog_item:
        hydrated["catalog_item_id"] = catalog_item_id
        hydrated["description"] = catalog_item.get("nombre", hydrated.get("description", ""))
        hydrated["unit"] = catalog_item.get("unidad", hydrated.get("unit", "pza"))
        hydrated["catalog_linked"] = True
        hydrated["catalog_missing"] = False
    else:
        if catalog_item_id:
            hydrated["catalog_item_id"] = catalog_item_id
        hydrated["catalog_linked"] = False
        hydrated["catalog_missing"] = bool(catalog_item_id)
    hydrated["qty"] = safe_float(hydrated.get("qty", 0))
    if "precio_cot" in hydrated:
        hydrated["precio_cot"] = safe_float(hydrated.get("precio_cot", 0))
        hydrated["total_cot"] = round(hydrated["qty"] * hydrated["precio_cot"], 2)
    return hydrated


def hydrate_ldm(ldm, catalog_by_id=None, catalog_by_name=None):
    catalog_by_id = catalog_by_id if catalog_by_id is not None else {}
    catalog_by_name = catalog_by_name if catalog_by_name is not None else {}
    hydrated = dict(ldm)
    hydrated["items"] = [hydrate_ldm_item(item, catalog_by_id, catalog_by_name) for item in ldm.get("items", [])]
    has_item_costs = any(item.get("precio_cot") or item.get("total_cot") for item in hydrated["items"])
    if has_item_costs:
        hydrated["subtotal_cot"] = round(sum(item.get("total_cot", 0) for item in hydrated["items"]), 2)
    else:
        hydrated["subtotal_cot"] = round(safe_float(hydrated.get("subtotal_cot", 0)), 2)
    return hydrated


def parse_quote_items():
    descs, desc2s, units, qtys, prices = (
        request.form.getlist(f"item_{key}[]") for key in ("desc", "desc2", "unit", "qty", "price")
    )
    catalog_ids = request.form.getlist("item_catalog_id[]")
    catalog_by_id, catalog_by_name = catalog_maps()
    items = []
    subtotal = 0.0
    for index, description in enumerate(descs):
        if not description.strip():
            continue
        qty = safe_float(qtys[index]) if index < len(qtys) and qtys[index] else 0
        price = safe_float(prices[index]) if index < len(prices) and prices[index] else 0
        explicit_desc = desc2s[index].strip() if index < len(desc2s) and desc2s[index] else ""
        unit = units[index] if index < len(units) else "pza"
        raw_item = {
            "catalog_item_id": catalog_ids[index].strip() if index < len(catalog_ids) and catalog_ids[index] else "",
            "description": description.strip(),
            "unit": unit,
            "qty": qty,
            "price": price,
            "catalog_description": explicit_desc,
        }
        hydrated = hydrate_quote_item(raw_item, catalog_by_id, catalog_by_name, infer_by_name=False)
        items.append({
            "catalog_item_id": hydrated.get("catalog_item_id", ""),
            "description": hydrated["description"],
            "unit": hydrated["unit"],
            "qty": hydrated["qty"],
            "price": hydrated["price"],
            "total": hydrated["total"],
            "catalog_description": hydrated.get("catalog_description", ""),
        })
        subtotal += hydrated["total"]
    return items, subtotal


def parse_ldm_items():
    descs = request.form.getlist("item_desc[]")
    units = request.form.getlist("item_unit[]")
    qtys = request.form.getlist("item_qty[]")
    prices = request.form.getlist("item_precio_cot[]")
    catalog_ids = request.form.getlist("item_catalog_id[]")
    catalog_by_id, catalog_by_name = catalog_maps()
    items = []
    subtotal = 0.0
    for index, description in enumerate(descs):
        if not description.strip():
            continue
        qty = safe_float(qtys[index], 1) if index < len(qtys) and qtys[index] else 1
        price = safe_float(prices[index], 0) if index < len(prices) and prices[index] else 0.0
        raw_item = {
            "catalog_item_id": catalog_ids[index].strip() if index < len(catalog_ids) and catalog_ids[index] else "",
            "description": description.strip(),
            "unit": units[index] if index < len(units) else "pza",
            "qty": qty,
            "precio_cot": price,
        }
        hydrated = hydrate_ldm_item(raw_item, catalog_by_id, catalog_by_name, infer_by_name=False)
        items.append({
            "catalog_item_id": hydrated.get("catalog_item_id", ""),
            "description": hydrated["description"],
            "unit": hydrated["unit"],
            "qty": hydrated["qty"],
            "precio_cot": hydrated.get("precio_cot", 0.0),
            "total_cot": hydrated.get("total_cot", 0.0),
        })
        subtotal += hydrated.get("total_cot", 0.0)
    return items, round(subtotal, 2)


def next_quote_number(project, all_quotes, quote_type, date_str):
    canonical_type = quote_type_key(quote_type)
    tipo_code = quote_type_code(canonical_type)
    same_type = [
        quote
        for quote in all_quotes
        if quote["project_id"] == project["id"] and quote_type_key(quote.get("quote_type")) == canonical_type
    ]
    sequence = len(same_type) + 1
    date_token = (date_str or today()).replace("-", "")
    return f"COT-{project['clave']}-{tipo_code}{sequence:02d}-{date_token}"


def sanitize_pdf_text(text):
    return (
        str(text if text is not None else "")
        .replace("\u2014", "-")
        .replace("\u2013", "-")
        .replace("\u2022", "-")
        .replace("\u00b7", "-")
        .replace("\u2018", "'")
        .replace("\u2019", "'")
        .replace("\u201c", '"')
        .replace("\u201d", '"')
        .replace("\u2026", "...")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )
