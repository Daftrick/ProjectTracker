"""Plantillas de Términos y Condiciones — independientes de las plantillas
de artículos (Proyecto/Obra/Servicio).

Cada cotización se liga por referencia (terms_template_id) a una de estas
plantillas: si se corrige el texto de una plantilla, el cambio se refleja
en todas las cotizaciones que la usan. No hay edición de términos por
cotización — sólo se elige cuál plantilla aplica.
"""

import uuid

from .pdfs import QUOTE_TERMS_DEFAULTS
from .storage import load as _load, save as _save

DEFAULT_TERMS_TEMPLATE_NAME = "Términos estándar"


def _new_id():
    return str(uuid.uuid4())[:8].upper()


def _seed_terms_template():
    return {
        "id": "estandar",
        "name": DEFAULT_TERMS_TEMPLATE_NAME,
        "terms": [
            {"id": key, "title": title, "body": body, "enabled": True}
            for key, title, body in QUOTE_TERMS_DEFAULTS
        ],
    }


def _normalize_term(term):
    if not isinstance(term, dict):
        return None
    title = str(term.get("title") or "").strip()
    body = str(term.get("body") or "").strip()
    if not title and not body:
        return None
    return {
        "id": str(term.get("id") or _new_id()).strip() or _new_id(),
        "title": title or "Sin título",
        "body": body,
        "enabled": bool(term.get("enabled", True)),
    }


def _normalize_template(template):
    if not isinstance(template, dict):
        return None
    name = str(template.get("name") or "Sin nombre").strip() or "Sin nombre"
    terms = [
        normalized
        for term in (template.get("terms") or [])
        if (normalized := _normalize_term(term)) is not None
    ]
    return {
        "id": str(template.get("id") or _new_id()).strip() or _new_id(),
        "name": name,
        "terms": terms,
    }


def _normalize(raw):
    source = raw if isinstance(raw, list) else []
    templates = [
        normalized
        for template in source
        if (normalized := _normalize_template(template)) is not None
    ]
    return templates or [_seed_terms_template()]


def get_terms_templates() -> list:
    try:
        raw = _load("terms_templates")
        if not isinstance(raw, list):
            return _normalize([])
        return _normalize(raw)
    except Exception:
        return _normalize([])


def save_terms_templates(data: list):
    _save("terms_templates", _normalize(data))


def get_terms_template_by_id(template_id: str) -> dict:
    template_id = str(template_id or "").strip()
    for template in get_terms_templates():
        if str(template.get("id")) == template_id:
            return template
    return {}


def resolve_quote_terms(quote: dict) -> tuple[list, dict]:
    """Devuelve (terms, template) para una cotización.

    Orden de resolución:
    1. terms_template_id explícito → esa plantilla.
    2. Cotizaciones legado con specs.terms guardado directamente (antes de
       existir plantillas independientes) → se usan tal cual, sin plantilla.
    3. Ninguno de los anteriores → la primera plantilla disponible (estándar).
    """
    specs = (quote or {}).get("specs") or {}
    template_id = str(specs.get("terms_template_id") or "").strip()
    if template_id:
        template = get_terms_template_by_id(template_id)
        if template:
            return template.get("terms", []), template

    legacy_terms = specs.get("terms")
    if legacy_terms:
        from .pdfs import QUOTE_TERM_TITLES
        normalized_legacy = []
        for term in legacy_terms:
            if not isinstance(term, dict):
                continue
            key = term.get("key")
            title = QUOTE_TERM_TITLES.get(key, term.get("title", "")) if key else term.get("title", "")
            normalized_legacy.append({**term, "title": title})
        return normalized_legacy, {}

    templates = get_terms_templates()
    default_template = templates[0] if templates else _seed_terms_template()
    return default_template.get("terms", []), default_template
