import uuid

from .pdfs import QUOTE_TERMS_DEFAULTS
from .storage import load as _load, save as _save

MAX_QUOTE_TEMPLATE_CONTACTS = 4

_SEED_QUOTE_TEMPLATE = {
    "Proyecto": {
        "id": "proy-com",
        "name": "Proyecto ejecutivo completo",
        "sections_default": [
            {
                "name": "Diseno de Instalaciones Electricas",
                "items": [
                    {
                        "catalog_item_id": "6CA7BF58",
                        "description": "Desarrollo de Circuito Electrico para Iluminacion | 20 [m] | Sin Tuberia",
                        "unit": "lote",
                        "qty": 1,
                    },
                    {
                        "catalog_item_id": "5C329F0A",
                        "description": "Desarrollo de Circuito Electrico para Contactos | 20 [m] | Sin Tuberia",
                        "unit": "lote",
                        "qty": 1,
                    },
                    {
                        "catalog_item_id": "374DD97B",
                        "description": "Desarrollo de Circuito Electrico para HVAC | 20 [m] | Sin Tuberia",
                        "unit": "lote",
                        "qty": 1,
                    },
                ],
            },
            {
                "name": "Salidas y canalizacion base",
                "items": [
                    {
                        "catalog_item_id": "42075597",
                        "description": "Salida Electrica para Luminaria en Muro, Piso o Plafon",
                        "unit": "pza",
                        "qty": 10,
                    },
                    {
                        "catalog_item_id": "8F45B371",
                        "description": "Metro Lineal de Tuberia Conduit Galvanizado Pared Delgada | 21 [mm] (3/4\")",
                        "unit": "ml",
                        "qty": 20,
                    },
                ],
            },
        ],
    }
}


def _default_terms():
    return [
        {
            "key": key,
            "title": title,
            "body": body,
            "enabled": True,
        }
        for key, title, body in QUOTE_TERMS_DEFAULTS
    ]


def _default_contacts():
    return [
        {
            "enabled": False,
            "name": "",
            "role": "",
        }
        for _ in range(MAX_QUOTE_TEMPLATE_CONTACTS)
    ]


QUOTE_TEMPLATE_DEFAULTS = {
    "Proyecto": {
        "sections_default": [],
        "terms_default": _default_terms(),
        "contacts_default": _default_contacts(),
    },
    "Obra": {
        "sections_default": [],
        "terms_default": _default_terms(),
        "contacts_default": _default_contacts(),
    },
    "Servicio": {
        "sections_default": [],
        "terms_default": _default_terms(),
        "contacts_default": _default_contacts(),
    },
}


def _new_id():
    return str(uuid.uuid4())[:8].upper()


def _normalize_terms(stored_terms):
    stored_by_key = {}
    if isinstance(stored_terms, list):
        stored_by_key = {
            item.get("key"): item
            for item in stored_terms
            if isinstance(item, dict) and item.get("key")
        }

    normalized = []
    for key, title, body in QUOTE_TERMS_DEFAULTS:
        stored = stored_by_key.get(key, {})
        normalized.append({
            "key": key,
            "title": title,
            "body": stored.get("body") if stored.get("body") is not None else body,
            "enabled": bool(stored.get("enabled", True)),
        })
    return normalized


def _normalize_contacts(stored_contacts):
    stored = stored_contacts if isinstance(stored_contacts, list) else []
    normalized = []
    for index in range(MAX_QUOTE_TEMPLATE_CONTACTS):
        item = stored[index] if index < len(stored) and isinstance(stored[index], dict) else {}
        normalized.append({
            "enabled": bool(item.get("enabled", False)),
            "name": str(item.get("name") or "").strip(),
            "role": str(item.get("role") or "").strip(),
        })
    return normalized


def normalize_contact_rows(stored_contacts):
    return _normalize_contacts(stored_contacts)


def _normalize_template_item(item):
    if not isinstance(item, dict):
        return None
    catalog_item_id = str(item.get("catalog_item_id") or "").strip()
    if not catalog_item_id:
        return None
    try:
        qty = float(str(item.get("qty", 1) or 1).replace(",", "."))
    except ValueError:
        qty = 1.0
    return {
        "catalog_item_id": catalog_item_id,
        "description": str(item.get("description") or "").strip(),
        "unit": str(item.get("unit") or "").strip(),
        "qty": qty,
    }


def _normalize_section(section):
    if isinstance(section, str):
        name = section.strip()
        return {"name": name, "items": []} if name else None
    if not isinstance(section, dict):
        return None
    name = str(section.get("name") or "").strip()
    items = [
        normalized
        for item in section.get("items", [])
        if (normalized := _normalize_template_item(item)) is not None
    ]
    if not name and not items:
        return None
    return {"name": name, "items": items}


def _normalize_sections(raw_sections, defaults):
    source = raw_sections if isinstance(raw_sections, list) else defaults["sections_default"]
    sections = [
        normalized
        for section in source
        if (normalized := _normalize_section(section)) is not None
    ]
    return sections


def _make_default_template(qtype, defaults):
    seed = _SEED_QUOTE_TEMPLATE.get(qtype)
    if seed:
        return _normalize_template(seed, qtype, defaults)
    return {
        "id": _new_id(),
        "name": qtype,
        "sections_default": _normalize_sections(defaults["sections_default"], defaults),
        "terms_default": _normalize_terms(defaults["terms_default"]),
        "contacts_default": _normalize_contacts(defaults["contacts_default"]),
    }


def _normalize_template(template, qtype, defaults):
    if not isinstance(template, dict):
        return None
    name = str(template.get("name") or qtype or "Sin nombre").strip() or "Sin nombre"
    return {
        "id": str(template.get("id") or _new_id()).strip() or _new_id(),
        "name": name,
        "sections_default": _normalize_sections(template.get("sections_default"), defaults),
        "terms_default": _normalize_terms(template.get("terms_default")),
        "contacts_default": _normalize_contacts(template.get("contacts_default")),
    }


def _normalize(raw):
    result = {}
    for qtype, defaults in QUOTE_TEMPLATE_DEFAULTS.items():
        stored = raw.get(qtype, []) if isinstance(raw, dict) else []
        if isinstance(stored, dict):
            stored = [stored]
        if not isinstance(stored, list):
            stored = []
        templates = [
            normalized
            for template in stored
            if (normalized := _normalize_template(template, qtype, defaults)) is not None
        ]
        result[qtype] = templates or [_make_default_template(qtype, defaults)]
    return result


def get_quote_templates() -> dict:
    try:
        raw = _load("quote_templates")
        if not isinstance(raw, dict):
            return _normalize({})
        return _normalize(raw)
    except Exception:
        return _normalize({})


def save_quote_templates(data: dict):
    _save("quote_templates", _normalize(data))


def get_template_for_type(quote_type: str) -> dict:
    templates = get_quote_templates().get(quote_type, [])
    return templates[0] if templates else {}


def get_template_by_id(quote_type: str, template_id: str) -> dict:
    template_id = str(template_id or "").strip()
    for template in get_quote_templates().get(quote_type, []):
        if str(template.get("id")) == template_id:
            return template
    return {}
