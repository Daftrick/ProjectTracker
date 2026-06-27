from .pdfs import QUOTE_TERMS_DEFAULTS
from .storage import load as _load, save as _save

MAX_QUOTE_TEMPLATE_CONTACTS = 4


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


def _normalize(raw):
    result = {}
    for qtype, defaults in QUOTE_TEMPLATE_DEFAULTS.items():
        stored = raw.get(qtype, {}) if isinstance(raw, dict) else {}
        if not isinstance(stored, dict):
            stored = {}
        sections = stored.get("sections_default")
        result[qtype] = {
            "sections_default": sections if isinstance(sections, list) else list(defaults["sections_default"]),
            "terms_default": _normalize_terms(stored.get("terms_default")),
            "contacts_default": _normalize_contacts(stored.get("contacts_default")),
        }
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
    _save("quote_templates", data)


def get_template_for_type(quote_type: str) -> dict:
    return get_quote_templates().get(quote_type, QUOTE_TEMPLATE_DEFAULTS.get(quote_type, {}))
