from .storage import load as _load, save as _save

_SPECS_DEFAULTS = {
    "condiciones_pago": "",
    "exclusiones": "",
    "validez": "30 días naturales",
    "forma_entrega": "PDF digital",
    "contacto": "",
}

QUOTE_TEMPLATE_DEFAULTS = {
    "Proyecto": {
        "sections_default": [],
        "notes_default": "",
        "specs_default": dict(_SPECS_DEFAULTS),
    },
    "Obra": {
        "sections_default": [],
        "notes_default": "",
        "specs_default": dict(_SPECS_DEFAULTS),
    },
    "Servicio": {
        "sections_default": [],
        "notes_default": "",
        "specs_default": dict(_SPECS_DEFAULTS),
    },
}


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
