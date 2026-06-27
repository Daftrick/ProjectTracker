from .pdfs import QUOTE_TERMS_DEFAULTS
from .storage import load as _load, save as _save

_SPECS_DEFAULTS = {
    "condiciones_pago": "",
    "exclusiones": "",
    "validez": "30 días naturales",
    "forma_entrega": "PDF digital",
    "contacto": "",
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


QUOTE_TEMPLATE_DEFAULTS = {
    "Proyecto": {
        "sections_default": [],
        "notes_default": "",
        "specs_default": dict(_SPECS_DEFAULTS),
        "terms_default": _default_terms(),
    },
    "Obra": {
        "sections_default": [],
        "notes_default": "",
        "specs_default": dict(_SPECS_DEFAULTS),
        "terms_default": _default_terms(),
    },
    "Servicio": {
        "sections_default": [],
        "notes_default": "",
        "specs_default": dict(_SPECS_DEFAULTS),
        "terms_default": _default_terms(),
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
            "title": stored.get("title") or title,
            "body": stored.get("body") if stored.get("body") is not None else body,
            "enabled": bool(stored.get("enabled", True)),
        })
    return normalized


def _normalize(raw):
    result = {}
    for qtype, defaults in QUOTE_TEMPLATE_DEFAULTS.items():
        stored = raw.get(qtype, {}) if isinstance(raw, dict) else {}
        if not isinstance(stored, dict):
            stored = {}
        specs = {**defaults["specs_default"], **(stored.get("specs_default") or {})}
        sections = stored.get("sections_default")
        result[qtype] = {
            "sections_default": sections if isinstance(sections, list) else list(defaults["sections_default"]),
            "notes_default": stored["notes_default"] if stored.get("notes_default") is not None else defaults["notes_default"],
            "specs_default": specs,
            "terms_default": _normalize_terms(stored.get("terms_default")),
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
