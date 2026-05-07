"""Filtros puros para vistas administrativas con listas largas."""

from __future__ import annotations

import unicodedata
from typing import Iterable


def _normalize(value: object) -> str:
    raw = str(value or "")
    nfkd = unicodedata.normalize("NFKD", raw)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).casefold()


def _tokens(query: str) -> list[str]:
    return [token for token in _normalize(query).split() if token]


def _indexed(item: dict, fields: Iterable[str]) -> str:
    return _normalize(" ".join(str(item.get(field, "") or "") for field in fields))


def _matches_tokens(item: dict, query: str, fields: Iterable[str]) -> bool:
    tokens = _tokens(query)
    if not tokens:
        return True
    haystack = _indexed(item, fields)
    return all(token in haystack for token in tokens)


def list_field_values(items: Iterable[dict], field: str) -> list[str]:
    """Valores únicos no vacíos de un campo, ordenados sin distinguir acentos."""
    seen: dict[str, str] = {}
    for item in items:
        raw = str(item.get(field, "") or "").strip()
        if raw:
            seen.setdefault(_normalize(raw), raw)
    return sorted(seen.values(), key=_normalize)


def filter_proveedores(items: Iterable[dict], q: str = "", categoria: str = "") -> list[dict]:
    """Filtra proveedores por búsqueda libre y categoría exacta."""
    category_key = _normalize(categoria)
    fields = ("nombre", "categoria", "contacto", "email", "telefono", "notas")
    matched = []
    for item in items:
        if category_key and _normalize(item.get("categoria")) != category_key:
            continue
        if _matches_tokens(item, q, fields):
            matched.append(item)
    return sorted(matched, key=lambda item: _normalize(item.get("nombre")))


def filter_fichas(items: Iterable[dict], q: str = "", tipo: str = "", vinculo: str = "") -> list[dict]:
    """Filtra fichas por texto, tipo y estado de vinculación a proyectos."""
    tipo_key = _normalize(tipo)
    vinculo_key = _normalize(vinculo)
    fields = ("code", "tipo", "marca", "modelo", "descripcion", "filename", "notes")
    matched = []
    for item in items:
        if tipo_key and _normalize(item.get("tipo")) != tipo_key:
            continue
        linked = bool(item.get("projects"))
        if vinculo_key == "con-proyecto" and not linked:
            continue
        if vinculo_key == "sin-proyecto" and linked:
            continue
        if _matches_tokens(item, q, fields):
            matched.append(item)
    return sorted(
        matched,
        key=lambda item: (
            _normalize(item.get("tipo")),
            _normalize(item.get("marca")),
            _normalize(item.get("modelo")),
            _normalize(item.get("code")),
        ),
    )
