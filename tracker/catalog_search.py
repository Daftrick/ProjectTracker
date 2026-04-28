"""Búsqueda y filtrado del catálogo.

Funciones puras (sin I/O) para reutilizar entre la API JSON, la vista de
catálogo y, a futuro, otros módulos que necesiten filtrar artículos por
tokens, categoría o cualquier criterio adicional.

Diseño:
    - Búsqueda por tokens: la query se divide por espacios y cada token debe
      aparecer (substring, sin acentos, case-insensitive) en
      nombre + descripción + categoría. AND lógico entre tokens.
    - Filtro por categoría: match exacto (case-insensitive) sobre el campo
      `categoria` del artículo.
    - Orden alfabético por nombre como criterio por defecto.

Para escalar, basta agregar nuevos campos al texto indexado en
`_indexable_text` o nuevos parámetros a `filter_catalog`.
"""

from __future__ import annotations

import unicodedata
from typing import Iterable


def _normalize(text: object) -> str:
    """Quita acentos y baja a minúsculas para comparar texto en español."""
    raw = str(text or "")
    nfkd = unicodedata.normalize("NFKD", raw)
    return "".join(ch for ch in nfkd if not unicodedata.combining(ch)).lower()


def tokenize(query: str) -> list[str]:
    """Divide la query en tokens normalizados, descartando vacíos."""
    return [token for token in _normalize(query).split() if token]


def _indexable_text(item: dict) -> str:
    """Texto consolidado de un artículo para búsqueda por tokens."""
    return _normalize(
        " ".join(
            str(item.get(field, "") or "")
            for field in ("nombre", "descripcion", "categoria")
        )
    )


def match_item(item: dict, tokens: Iterable[str], categoria: str = "") -> bool:
    """¿El artículo cumple con todos los tokens y la categoría exigida?

    Los tokens pueden venir crudos o ya normalizados; aquí se normalizan
    defensivamente para que el filtro sea robusto sin importar de dónde vengan.
    """
    if categoria:
        if _normalize(item.get("categoria", "")) != _normalize(categoria):
            return False
    normalized_tokens = [_normalize(token) for token in tokens if str(token or "").strip()]
    if not normalized_tokens:
        return True
    haystack = _indexable_text(item)
    return all(token in haystack for token in normalized_tokens)


def filter_catalog(
    items: Iterable[dict],
    q: str = "",
    categoria: str = "",
) -> list[dict]:
    """Aplica búsqueda por tokens y filtro de categoría, ordenado alfabéticamente."""
    tokens = tokenize(q)
    matched = [item for item in items if match_item(item, tokens, categoria)]
    matched.sort(key=lambda item: _normalize(item.get("nombre", "")))
    return matched


def list_categories(items: Iterable[dict]) -> list[str]:
    """Lista única de categorías presentes en el catálogo, en orden alfabético."""
    seen: dict[str, str] = {}
    for item in items:
        raw = str(item.get("categoria", "") or "").strip()
        if not raw:
            continue
        key = _normalize(raw)
        seen.setdefault(key, raw)
    return sorted(seen.values(), key=lambda value: _normalize(value))
