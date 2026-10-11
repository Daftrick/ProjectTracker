"""Plantillas de Términos y Condiciones — independientes de las plantillas
de artículos (Proyecto/Obra/Servicio).

Las plantillas son una base. Al guardar desde el editor, cada cotización
conserva su propia copia editable en specs.terms.
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
    """Resuelve copia local > plantilla > estándar, incluidos overrides antiguos.

    Una lista local vacía significa que la cotización no incluye términos.
    """
    specs = (quote or {}).get("specs") or {}
    template_id = str(specs.get("terms_template_id") or "").strip()
    template = get_terms_template_by_id(template_id) if template_id else {}
    if isinstance(specs.get("terms"), list):
        from .pdfs import QUOTE_TERM_TITLES
        terms = []
        for index, term in enumerate(specs["terms"]):
            if not isinstance(term, dict):
                continue
            key = term.get("key")
            terms.append({
                **term,
                "id": str(term.get("id") or key or f"legacy-{index}"),
                "title": term.get("title") or QUOTE_TERM_TITLES.get(key, "Sin título"),
            })
        return terms, template

    if not template:
        templates = get_terms_templates()
        template = templates[0] if templates else _seed_terms_template()
    overrides = specs.get("term_body_overrides") or {}
    terms = [
        {**term, "body": overrides.get(term.get("id")) or term.get("body", "")}
        for term in template.get("terms", [])
    ]
    return terms, template


def quote_terms_from_form(form):
    """None = formulario antiguo; [] = términos eliminados explícitamente."""
    if form.get("terms_present") != "1":
        return None
    ids = form.getlist("term_id[]")
    titles = form.getlist("term_title[]")
    bodies = form.getlist("term_body[]")
    enabled = form.getlist("term_enabled[]")
    terms = []
    for index, title in enumerate(titles):
        term = _normalize_term({
            "id": ids[index] if index < len(ids) else "",
            "title": title,
            "body": bodies[index] if index < len(bodies) else "",
            "enabled": index < len(enabled) and enabled[index] == "1",
        })
        if term is not None:
            terms.append(term)
    return terms
