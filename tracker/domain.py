from datetime import date, datetime

from .storage import load

APP_VERSION = "v45.12"

DEFAULT_ALCANCES = [
    {"id": "iluminacion",    "nombre": "IE - Iluminación",        "source": "externa", "dep_label": "Diseño de iluminación (otra área)", "blocked_by": [],                                                                          "info_ext": True},
    {"id": "contactos",      "nombre": "IE - Contactos",           "source": "propia",  "dep_label": None,                                "blocked_by": [],                                                                          "info_ext": True},
    {"id": "hvac",           "nombre": "IE - HVAC",                "source": "externa", "dep_label": "Proyecto HVAC (otra área)",          "blocked_by": [],                                                                          "info_ext": True},
    {"id": "emergencia",     "nombre": "Sistema de Emergencia",    "source": "propia",  "dep_label": None,                                "blocked_by": [],                                                                          "info_ext": True},
    {"id": "fotovoltaico",   "nombre": "Sistema Fotovoltaico",     "source": "propia",  "dep_label": None,                                "blocked_by": [],                                                                          "info_ext": True},
    {"id": "subestacion",    "nombre": "Subestación Eléctrica",    "source": "propia",  "dep_label": None,                                "blocked_by": [],                                                                          "info_ext": True},
    {"id": "cuadro_cargas",  "nombre": "Cuadro de Cargas",         "source": "propia",  "dep_label": None,                                "blocked_by": ["iluminacion", "contactos", "hvac", "emergencia", "fotovoltaico", "subestacion"], "info_ext": False},
    {"id": "diagrama_unifilar", "nombre": "Diagrama Unifilar",     "source": "propia",  "dep_label": None,                                "blocked_by": ["cuadro_cargas"],                                                            "info_ext": False},
    {"id": "cotizacion",     "nombre": "Cotización",               "source": "propia",  "dep_label": None,                                "blocked_by": [],                                                                          "info_ext": False},
]


def get_alcances():
    data = load("alcances")
    if not isinstance(data, list) or not data:
        return DEFAULT_ALCANCES
    return data


def get_alcances_by_id(alcances=None):
    return {a["id"]: a for a in (alcances if alcances is not None else get_alcances())}


def get_info_ext_excluded(alcances=None):
    return {a["id"] for a in (alcances if alcances is not None else get_alcances()) if not a.get("info_ext", True)}


DEFAULT_DISCIPLINAS = [
    {"id": "IE",  "nombre": "Instalaciones Eléctricas"},
    {"id": "ARQ", "nombre": "Arquitectónico"},
    {"id": "EST", "nombre": "Estructural"},
    {"id": "AA",  "nombre": "Aire Acondicionado (HVAC)"},
    {"id": "HID", "nombre": "Hidráulico / Sanitario"},
    {"id": "VOZ", "nombre": "Voz y Datos"},
]


def get_disciplinas():
    data = load("disciplinas")
    if not isinstance(data, list) or not data:
        return DEFAULT_DISCIPLINAS
    return data


# Module-level names kept for backward-compat imports; use get_alcances() for live data.
ALCANCES = DEFAULT_ALCANCES
ALCANCES_BY_ID = {a["id"]: a for a in DEFAULT_ALCANCES}
INFO_EXT_EXCLUDED = {a["id"] for a in DEFAULT_ALCANCES if not a.get("info_ext", True)}
TASK_STATUSES = ["Pendiente", "En progreso", "Revisión", "Observaciones", "Aprobado"]
TIPOS_FICHA = ["LUM", "CONT", "INT", "THERM", "TFO", "PANEL", "CABLE", "COND", "UPS", "FV", "AC", "OTRO"]

STAGES = ["Cotización", "Diseño", "Entregado", "Obra"]


def check_blocked(task, main_tasks):
    for dep_id in get_alcances_by_id().get(task.get("alcance", ""), {}).get("blocked_by", []):
        dep = next((item for item in main_tasks if item.get("alcance") == dep_id), None)
        if dep and dep["status"] != "Aprobado":
            return True
    return False


def project_stage(project, tasks):
    """Derive the portfolio stage from existing task data + the in_obra flag.

    Stages: Cotización → Diseño → Entregado → Obra
    'Obra' is the only manually-set state (project['in_obra'] = True).
    The rest are computed from alcance statuses to avoid divergent state.
    """
    if project.get("in_obra"):
        return "Obra"
    main_tasks = [
        t for t in tasks
        if t["project_id"] == project["id"] and not t.get("parent_task_id")
    ]
    if not main_tasks:
        return "Cotización"
    cot_task = next((t for t in main_tasks if t.get("alcance") == "cotizacion"), None)
    cot_approved = cot_task is not None and cot_task["status"] == "Aprobado"
    if not cot_approved:
        return "Cotización"
    if all(t["status"] == "Aprobado" for t in main_tasks):
        return "Entregado"
    return "Diseño"


def get_progress(project_id, tasks=None):
    tasks = tasks if tasks is not None else load("tasks")
    main_tasks = [task for task in tasks if task["project_id"] == project_id and not task.get("parent_task_id")]
    total = len(main_tasks)
    approved = sum(1 for task in main_tasks if task["status"] == "Aprobado")
    pct = int(approved / total * 100) if total else 0
    if total == 0:
        status = "Sin alcances"
    elif approved == total:
        status = "Completado"
    elif any(task["status"] in ("En progreso", "Revisión", "Observaciones") for task in main_tasks):
        status = "En progreso"
    else:
        status = "Pendiente"
    return {"total": total, "approved": approved, "pct": pct, "status": status}


def fdate(v):
    if not v:
        return "—"
    try:
        return datetime.strptime(v, "%Y-%m-%d").strftime("%d/%m/%Y")
    except Exception:
        return v


def currency(v):
    try:
        return f"${float(v):,.2f}"
    except Exception:
        return str(v)


def today_short():
    return date.today().strftime("%y%m%d")


def project_semaphore(project, today_str):
    """Returns 'verde', 'amarillo', 'rojo', or 'gris' based on deadline and inactivity."""
    deadline = project.get("deadline")
    updated_at = project.get("updated_at")

    try:
        today_date = date.fromisoformat(today_str)
    except Exception:
        return "gris"

    days_inactive = None
    if updated_at:
        try:
            days_inactive = (today_date - date.fromisoformat(updated_at)).days
        except Exception:
            pass

    days_to_deadline = None
    if deadline:
        try:
            days_to_deadline = (date.fromisoformat(deadline) - today_date).days
        except Exception:
            pass

    if days_to_deadline is not None and days_to_deadline <= 3:
        return "rojo"
    if days_inactive is not None and days_inactive >= 7:
        return "rojo"
    if days_to_deadline is not None and days_to_deadline <= 7:
        return "amarillo"
    if days_inactive is not None and days_inactive >= 3:
        return "amarillo"
    if days_to_deadline is not None and days_inactive is not None and days_inactive < 3:
        return "verde"
    return "gris"
