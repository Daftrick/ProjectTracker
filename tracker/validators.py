import re
from datetime import datetime

from .catalog import catalog_maps, hydrate_ldm_item, hydrate_quote_item, quote_type_key
from .pdfs import QUOTE_TERMS_DEFAULTS
from .quote_templates_config import MAX_QUOTE_TEMPLATE_CONTACTS, normalize_contact_rows
from .utils import clean as _clean, deleted_catalog_item_at as _deleted_catalog_item_at, parse_form_float as _parse_float

VALID_CURRENCIES = {"MXN", "USD", "EUR"}
PROJECT_DATE_RE = re.compile(r"^\d{6}$")


def _is_blank(value):
    return _clean(value) == ""


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


def _validate_optional_iso_date(value, field_label, errors, field_errors=None, field_key=None):
    cleaned = _clean(value)
    if not cleaned:
        return ""
    try:
        datetime.strptime(cleaned, "%Y-%m-%d")
    except ValueError:
        message = f"{field_label} debe tener formato AAAA-MM-DD."
        errors.append(message)
        if field_errors is not None and field_key:
            field_errors.setdefault(field_key, message)
    return cleaned


def validate_project_form(form):
    errors = []
    field_errors = {}
    fields = {
        "name": _clean(form.get("name")),
        "clave": _clean(form.get("clave")),
        "client": _clean(form.get("client")),
        "notes": _clean(form.get("notes")),
    }

    if not fields["name"]:
        message = "El nombre del proyecto es requerido."
        errors.append(message)
        field_errors["name"] = message
    if not fields["clave"]:
        message = "La clave del proyecto es requerida."
        errors.append(message)
        field_errors["clave"] = message

    return {
        "ok": not errors,
        "errors": errors,
        "field_errors": field_errors,
        "fields": fields,
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

    default_pct_mo = _parse_float(form.get("default_pct_mo", "0") or "0", "% MO", errors, default=0.0)
    default_pct_indirectos = _parse_float(form.get("default_pct_indirectos", "0") or "0", "% Indirectos", errors, default=0.0)
    default_pct_utilidad = _parse_float(form.get("default_pct_utilidad", "0") or "0", "% Utilidad", errors, default=0.0)
    item_error_start = len(errors)
    items, subtotal = _parse_quote_items(form, errors, default_pct_mo, default_pct_indirectos, default_pct_utilidad)
    if not items:
        message = "Agrega al menos una partida o sección a la cotización."
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
    valid_until = _validate_optional_iso_date(
        form.get("valid_until"),
        "Vigente hasta",
        errors,
        field_errors=field_errors,
        field_key="valid_until",
    )

    specs = {
        field: _clean(form.get(f"specs_{field}")) or ""
        for field in ("condiciones_pago", "exclusiones", "validez", "forma_entrega", "contacto")
    }
    terms = []
    for key, title, default_body in QUOTE_TERMS_DEFAULTS:
        body = (_clean(form.get(f"term_{key}_body")) or "").strip()
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
            "name": _clean(form.get(f"integrante_{index}_name")),
            "role": _clean(form.get(f"integrante_{index}_role")),
        }
        for index in range(MAX_QUOTE_TEMPLATE_CONTACTS)
    ])
    return {
        "ok": not errors,
        "errors": errors,
        "field_errors": field_errors,
        "quote_type": quote_type_key(form.get("quote_type", "Proyecto")),
        "quote_number": _clean(form.get("quote_number")),
        "version": _clean(form.get("version")),
        "date": date_value,
        "valid_until": valid_until,
        "currency": currency,
        "tax_rate": tax_rate,
        "notes": _clean(form.get("notes")),
        "project_basis_note": _clean(form.get("project_basis_note")),
        "cover_discipline": _clean(form.get("cover_discipline")),
        "specs": specs,
        "items": items,
        "subtotal": round(subtotal, 2),
        "default_pct_mo": default_pct_mo,
        "default_pct_indirectos": default_pct_indirectos,
        "default_pct_utilidad": default_pct_utilidad,
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


def _parse_quote_items(form, errors, default_pct_mo=0.0, default_pct_indirectos=0.0, default_pct_utilidad=0.0):
    kinds = form.getlist("item_kind[]")
    sections = form.getlist("item_section[]")
    descs = form.getlist("item_desc[]")
    desc2s = form.getlist("item_desc2[]")
    units = form.getlist("item_unit[]")
    qtys = form.getlist("item_qty[]")
    prices = form.getlist("item_precio_costo[]")
    pct_mos = form.getlist("item_pct_mo[]")
    pct_inds = form.getlist("item_pct_indirectos[]")
    pct_utils = form.getlist("item_pct_utilidad[]")
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
            if current_section:
                items.append({
                    "kind": "section",
                    "section": current_section,
                })
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
        price = _parse_float(raw_price, "costo unitario", errors, row=row)
        if qty <= 0:
            errors.append(f"Fila {row}: cantidad debe ser mayor a 0.")
        if price < 0:
            errors.append(f"Fila {row}: costo unitario no puede ser negativo.")

        raw_pct_mo = _clean(pct_mos[index]) if index < len(pct_mos) else ""
        raw_pct_ind = _clean(pct_inds[index]) if index < len(pct_inds) else ""
        raw_pct_util = _clean(pct_utils[index]) if index < len(pct_utils) else ""
        pct_mo_override = _parse_float(raw_pct_mo, "% MO", errors, row=row) if raw_pct_mo else None
        pct_ind_override = _parse_float(raw_pct_ind, "% Indirectos", errors, row=row) if raw_pct_ind else None
        pct_util_override = _parse_float(raw_pct_util, "% Utilidad", errors, row=row) if raw_pct_util else None

        raw_item = {
            "catalog_item_id": _clean(catalog_ids[index]) if index < len(catalog_ids) else "",
            "description": _clean(description),
            "unit": _clean(units[index]) if index < len(units) else "pza",
            "qty": qty,
            "precio_costo": price,
            "pct_mo_override": pct_mo_override,
            "pct_indirectos_override": pct_ind_override,
            "pct_utilidad_override": pct_util_override,
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
        hydrated = hydrate_quote_item(
            raw_item, catalog_by_id, catalog_by_name, infer_by_name=False,
            default_pct_mo=default_pct_mo,
            default_pct_indirectos=default_pct_indirectos,
            default_pct_utilidad=default_pct_utilidad,
        )
        parsed_item = {
            "catalog_item_id": hydrated.get("catalog_item_id", ""),
            "description": hydrated["description"],
            "unit": hydrated["unit"] or "pza",
            "qty": hydrated["qty"],
            "precio_costo": hydrated["precio_costo"],
            "pct_mo_override": pct_mo_override,
            "pct_indirectos_override": pct_ind_override,
            "pct_utilidad_override": pct_util_override,
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
    origins = form.getlist("item_origen[]")
    sync_expected_catalog_ids = form.getlist("item_sync_expected_catalog_item_id[]")
    sync_expected_qtys = form.getlist("item_sync_expected_qty[]")
    sync_total_expected_qtys = form.getlist("item_sync_total_expected_qty[]")
    sync_actual_qtys = form.getlist("item_sync_actual_qty[]")
    sync_issues = form.getlist("item_sync_issue[]")
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
        origin = _clean(origins[index]) if index < len(origins) else ""
        if origin:
            parsed_item["origen"] = origin
        sync_expected_catalog_id = _clean(sync_expected_catalog_ids[index]) if index < len(sync_expected_catalog_ids) else ""
        if sync_expected_catalog_id:
            parsed_item["sync_expected_catalog_item_id"] = sync_expected_catalog_id
            parsed_item["sync_expected_qty"] = _parse_float(
                sync_expected_qtys[index] if index < len(sync_expected_qtys) else "",
                "cantidad esperada",
                errors,
                row=row,
                default=0,
            )
            parsed_item["sync_issue"] = _clean(sync_issues[index]) if index < len(sync_issues) else ""
            _discard: list = []
            parsed_item["sync_total_expected_qty"] = _parse_float(
                sync_total_expected_qtys[index] if index < len(sync_total_expected_qtys) else "",
                "cantidad total esperada",
                _discard,
                row=row,
                default=0,
            )
            parsed_item["sync_actual_qty"] = _parse_float(
                sync_actual_qtys[index] if index < len(sync_actual_qtys) else "",
                "cantidad actual en LDM",
                _discard,
                row=row,
                default=0,
            )
        if hydrated.get("deleted_catalog_item"):
            parsed_item["deleted_catalog_item"] = hydrated["deleted_catalog_item"]
        items.append(parsed_item)
        subtotal += hydrated.get("total_cot", 0.0)

    return items, subtotal
