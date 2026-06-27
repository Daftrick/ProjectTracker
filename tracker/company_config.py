from .storage import load as _load, save as _save

COMPANY_DEFAULTS = {
    "name": "Mi Empresa",
    "prefix": "",
    "logo": "",
    "address": "",
    "rut": "",
    "portada_color": "#000000",
}


def get_company():
    try:
        data = _load("company")
        if not isinstance(data, dict):
            return dict(COMPANY_DEFAULTS)
        return {**COMPANY_DEFAULTS, **data}
    except Exception:
        return dict(COMPANY_DEFAULTS)


def save_company(data: dict):
    _save("company", data)
