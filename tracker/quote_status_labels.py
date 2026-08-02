"""Nomenclatura editable de estados de cotización (borrador / activa / obsoleta).

Antes el sistema mostraba etiquetas distintas según el tipo de cotización:
"Aprobada"/"Obsoleta" para cotizaciones base y "Activa"/"Inactiva" para
extraordinarias — inconsistente (VERSIONES.md #10). Ahora hay tres estados
únicos (draft/active/obsolete) con texto editable por cualquier usuario
autenticado, aplicados sin importar el tipo de cotización.
"""

from .storage import load as _load, save as _save

DEFAULT_LABELS = {
    "draft": "Borrador",
    "active": "Activa",
    "obsolete": "Obsoleta",
}

_ICONS = {
    "draft": "pencil-square",
    "active": "check-circle",
    "obsolete": "slash-circle",
}

_BADGES = {
    "draft": "warning",
    "active": "success",
    "obsolete": "secondary",
}

STATUS_KEYS = ("draft", "active", "obsolete")


def get_quote_status_labels() -> dict:
    try:
        data = _load("quote_status_labels")
        if not isinstance(data, dict):
            return dict(DEFAULT_LABELS)
    except Exception:
        return dict(DEFAULT_LABELS)
    labels = dict(DEFAULT_LABELS)
    for key in STATUS_KEYS:
        value = str(data.get(key) or "").strip()
        if value:
            labels[key] = value
    return labels


def save_quote_status_labels(data: dict):
    cleaned = {}
    for key in STATUS_KEYS:
        value = str((data or {}).get(key) or "").strip()
        cleaned[key] = value or DEFAULT_LABELS[key]
    _save("quote_status_labels", cleaned)


def quote_status_view(approval_status) -> dict:
    """Badge/label/icon unificados para un approval_status dado, sin
    distinguir cotización base vs. extraordinaria."""
    status = approval_status if approval_status in STATUS_KEYS else "draft"
    labels = get_quote_status_labels()
    return {
        "status": status,
        "label": labels[status],
        "badge": _BADGES[status],
        "icon": _ICONS[status],
    }
