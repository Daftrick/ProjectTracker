from .catalog import quote_type_code, quote_type_key
from .pdfs import QUOTE_TERMS_DEFAULTS
from .quote_templates_config import MAX_QUOTE_TEMPLATE_CONTACTS, normalize_contact_rows
from .storage import today
from .utils import deleted_catalog_item_at as _deleted_catalog_item_at


def quote_default_numbers(project, quotes, quote_id=None):
    other_quotes = [item for item in quotes if item.get("id") != quote_id]
    project_others = [item for item in other_quotes if item["project_id"] == project["id"]]
    proyecto_quotes = [item for item in project_others if quote_type_code(item.get("quote_type", "")) == "P"]
    obra_quotes = [item for item in project_others if quote_type_code(item.get("quote_type", "")) == "O"]
    servicio_quotes = [item for item in project_others if quote_type_code(item.get("quote_type", "")) == "S"]
    extraordinary_quotes = [item for item in project_others if quote_type_code(item.get("quote_type", "")) == "E"]
    date_token = today().replace("-", "")
    return {
        "default_num_pr": f"COT-{project['clave']}-P{len(proyecto_quotes) + 1:02d}-{date_token}",
        "default_num_o": f"COT-{project['clave']}-O{len(obra_quotes) + 1:02d}-{date_token}",
        "default_num_s": f"COT-{project['clave']}-S{len(servicio_quotes) + 1:02d}-{date_token}",
        "default_num_e": f"COT-{project['clave']}-E{len(extraordinary_quotes) + 1:02d}-{date_token}",
    }


def quote_from_form(form, fallback_quote=None):
    kinds = form.getlist("item_kind[]")
    sections = form.getlist("item_section[]")
    descs = form.getlist("item_desc[]")
    desc2s = form.getlist("item_desc2[]")
    units = form.getlist("item_unit[]")
    qtys = form.getlist("item_qty[]")
    precios_costo = form.getlist("item_precio_costo[]")
    pct_mo_overrides = form.getlist("item_pct_mo[]")
    pct_ind_overrides = form.getlist("item_pct_indirectos[]")
    pct_util_overrides = form.getlist("item_pct_utilidad[]")
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
            if current_section:
                items.append({
                    "kind": "section",
                    "section": current_section,
                })
            continue
        section = raw_section.strip() or current_section
        qty = qtys[index] if index < len(qtys) else "1"
        precio_costo = precios_costo[index] if index < len(precios_costo) else "0"
        pct_mo_raw = pct_mo_overrides[index].strip() if index < len(pct_mo_overrides) else ""
        pct_ind_raw = pct_ind_overrides[index].strip() if index < len(pct_ind_overrides) else ""
        pct_util_raw = pct_util_overrides[index].strip() if index < len(pct_util_overrides) else ""
        parsed_item = {
            "catalog_item_id": catalog_ids[index].strip() if index < len(catalog_ids) else "",
            "description": description.strip(),
            "unit": units[index].strip() if index < len(units) else "pza",
            "qty": qty,
            "precio_costo": precio_costo,
            "pct_mo_override": _to_float(pct_mo_raw) if pct_mo_raw else None,
            "pct_indirectos_override": _to_float(pct_ind_raw) if pct_ind_raw else None,
            "pct_utilidad_override": _to_float(pct_util_raw) if pct_util_raw else None,
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
    specs = {
        field: (form.get(f"specs_{field}") or "").strip()
        for field in ("condiciones_pago", "exclusiones", "validez", "forma_entrega", "contacto")
    }
    terms = []
    for key, title, default_body in QUOTE_TERMS_DEFAULTS:
        body = (form.get(f"term_{key}_body") or "").strip()
        enabled = bool(form.get(f"term_{key}_enabled"))
        terms.append({
            "key": key,
            "title": title,
            "body": body or default_body,
            "enabled": enabled,
        })
    specs["terms"] = terms
    specs["integrantes"] = normalize_contact_rows([
        {
            "enabled": bool(form.get(f"integrante_{index}_enabled")),
            "name": (form.get(f"integrante_{index}_name") or "").strip(),
            "role": (form.get(f"integrante_{index}_role") or "").strip(),
        }
        for index in range(MAX_QUOTE_TEMPLATE_CONTACTS)
    ])
    base.update({
        "quote_type": quote_type_key(form.get("quote_type", "Proyecto")),
        "quote_number": form.get("quote_number", "").strip(),
        "version": form.get("version", "").strip(),
        "date": form.get("date", "").strip(),
        "valid_until": form.get("valid_until", "").strip(),
        "currency": form.get("currency", "MXN").strip() or "MXN",
        "tax_rate": form.get("tax_rate", "16").strip() or "16",
        "default_pct_mo": _to_float(form.get("default_pct_mo", "0") or "0"),
        "default_pct_indirectos": _to_float(form.get("default_pct_indirectos", "0") or "0"),
        "default_pct_utilidad": _to_float(form.get("default_pct_utilidad", "0") or "0"),
        "notes": form.get("notes", "").strip(),
        "project_basis_note": form.get("project_basis_note", "").strip(),
        "cover_discipline": form.get("cover_discipline", "").strip(),
        "specs": specs,
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

