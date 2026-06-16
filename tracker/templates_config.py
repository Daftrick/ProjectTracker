from .storage import load as _load, save as _save

DEFAULT_TEMPLATES = [
    {
        "id": "residencial",
        "name": "Proyecto Residencial",
        "stages": ["Diseño", "Permisos", "Obra", "Entrega"],
    },
    {
        "id": "comercial",
        "name": "Proyecto Comercial",
        "stages": ["Diseño", "Permisos", "Obra", "Entrega"],
    },
]


def get_project_templates():
    try:
        data = _load("project_templates")
        if not isinstance(data, list) or not data:
            return [dict(t) for t in DEFAULT_TEMPLATES]
        return data
    except Exception:
        return [dict(t) for t in DEFAULT_TEMPLATES]


def save_project_templates(data: list):
    _save("project_templates", data)
