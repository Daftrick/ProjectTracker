import datetime
import json
import os
import re
import unicodedata

from .storage import DATA_DIR, load, save

IGNORED_SCAN_EXTENSIONS = {".bak", ".dwl", ".dwl2"}

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")


def load_config():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        return {"drive_projects_path": "", "drive_fichas_path": ""}
    with open(CONFIG_FILE, encoding="utf-8") as handle:
        return json.load(handle)


def save_config(cfg):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
        json.dump(cfg, handle, ensure_ascii=False, indent=2)


def migrate_task_statuses():
    status_map = {
        "En Progreso": "En progreso",
        "Enviado a Revisión": "Revisión",
        "Con Observaciones": "Observaciones",
    }
    tasks = load("tasks")
    changed = False
    for task in tasks:
        if task.get("status") in status_map:
            task["status"] = status_map[task["status"]]
            changed = True
        for history in task.get("history", []):
            if history.get("from") in status_map:
                history["from"] = status_map[history["from"]]
                changed = True
            if history.get("to") in status_map:
                history["to"] = status_map[history["to"]]
                changed = True
    if changed:
        save("tasks", tasks)


def migrate_task_names():
    rename = {
        "Instalación Eléctrica de Iluminación": "IE - Iluminación",
        "Contactos": "IE - Contactos",
        "HVAC": "IE - HVAC",
        "Subestación Eléctrica Media/Baja Tensión": "Subestación Eléctrica",
        "Cotización / Presupuesto": "Cotización",
    }
    tasks = load("tasks")
    changed = False
    for task in tasks:
        if task.get("title") in rename:
            task["title"] = rename[task["title"]]
            changed = True
    if changed:
        save("tasks", tasks)


def migrate_folder_numbers():
    projects = load("projects")
    existing = {int(project["folder_num"]) for project in projects if project.get("folder_num", "").isdigit()}
    changed = False
    counter = 1
    for project in sorted(projects, key=lambda item: item.get("created_at", "")):
        if not project.get("folder_num"):
            while counter in existing:
                counter += 1
            project["folder_num"] = f"{counter:03d}"
            existing.add(counter)
            changed = True
        counter += 1
    if changed:
        save("projects", projects)


def folder_name(project):
    return f"IE-{project.get('folder_num', '000')}-{project['clave']}"


def normalize_ascii(text):
    normalized = unicodedata.normalize("NFKD", text or "")
    return normalized.encode("ascii", "ignore").decode("ascii")


def provider_token(text):
    match = re.search(r"[A-Za-z0-9]+", normalize_ascii(text))
    return match.group(0).lower() if match else ""


def version_key(filename):
    match = re.search(r"-V(\d+)(?:-([0-9]{6,8}))?", filename, re.IGNORECASE)
    if not match:
        return None
    return (int(match.group(1)), int(match.group(2) or 0))


def decorate_latest(names):
    names = sorted(names)
    parsed = {name: version_key(name) for name in names}
    versioned = [key for key in parsed.values() if key is not None]
    latest = max(versioned) if versioned else None
    single_file = len(names) == 1
    return [{"name": name, "highlight": (parsed[name] == latest) if latest is not None else single_file} for name in names]


def decorate_plain(names, **extra):
    return [{"name": name, **extra} for name in sorted(names)]


def latest_dwg_stem(folder):
    if not folder or not os.path.isdir(folder):
        return ""
    candidates = []
    for item in os.listdir(folder):
        path = os.path.join(folder, item)
        _, ext = os.path.splitext(item.lower())
        if not os.path.isfile(path) or ext != ".dwg":
            continue
        if ext in IGNORED_SCAN_EXTENSIONS:
            continue
        candidates.append(item)
    if not candidates:
        return ""

    latest = max(
        candidates,
        key=lambda name: (
            version_key(name) is not None,
            version_key(name) or (-1, 0),
            os.path.getmtime(os.path.join(folder, name)),
            name,
        ),
    )
    return os.path.splitext(latest)[0]


def parse_csv_plano_filename(filename, clave=None):
    clave_pattern = re.escape(clave) if clave else r"(?P<clave>[A-Za-z0-9_-]+)"
    pattern = re.compile(
        rf"^(?P<project>{clave_pattern})-v(?P<version>\d+)-i(?P<consecutive>\d+)-(?P<date>\d{{8}})\.csv$",
        re.IGNORECASE,
    )
    match = pattern.match(filename or "")
    if not match:
        return None
    date_token = match.group("date")
    try:
        date_label = datetime.datetime.strptime(date_token, "%Y%m%d").strftime("%d/%m/%Y")
    except ValueError:
        date_label = date_token
    return {
        "project": match.group("project"),
        "version": int(match.group("version")),
        "consecutive": int(match.group("consecutive")),
        "date": date_token,
        "date_label": date_label,
    }


def csv_version_key(filename, clave=None):
    parsed = parse_csv_plano_filename(filename, clave)
    if not parsed:
        return (-1, -1, 0)
    return (parsed["version"], parsed["consecutive"], int(parsed["date"]))


def _ldm_csv_sources(ldms, clave=None):
    sources = {}
    for ldm in ldms or []:
        raw_sources = []
        for key in ("csv_origen", "csv_origin", "csv_filename"):
            if ldm.get(key):
                raw_sources.append(ldm.get(key))
        raw_sources.extend(ldm.get("csv_sources", []) or [])
        for source in raw_sources:
            name = os.path.basename(str(source or "").strip())
            if not name:
                continue
            sources[name.lower()] = {
                "name": name,
                "ldm_number": ldm.get("ldm_number", ""),
                "key": csv_version_key(name, clave),
            }
    return sources


def decorate_csv_plano(files, ldms=None, clave=None):
    linked = _ldm_csv_sources(ldms, clave)
    latest_key = max((csv_version_key(item["name"], clave) for item in files), default=(-1, -1, 0))
    latest_linked_key = max((info["key"] for info in linked.values()), default=None)
    decorated = []
    for item in sorted(files, key=lambda value: csv_version_key(value["name"], clave)):
        name = item["name"]
        parsed = parse_csv_plano_filename(name, clave)
        link = linked.get(name.lower())
        if link and csv_version_key(name, clave) < latest_key:
            status = "desactualizado"
            status_label = "Desactualizado"
            badge_class = "bg-warning text-dark"
            hint = "Hay un CSV más reciente en la carpeta."
        elif link:
            status = "importado"
            status_label = "Importado"
            badge_class = "bg-success"
            hint = f"Vinculado a {link['ldm_number']}" if link.get("ldm_number") else "Vinculado a LDM."
        elif latest_linked_key and csv_version_key(name, clave) > latest_linked_key:
            status = "pendiente"
            status_label = "Actualización"
            badge_class = "bg-info text-dark"
            hint = "CSV nuevo posterior a la LDM importada."
        else:
            status = "pendiente"
            status_label = "Pendiente"
            badge_class = "bg-secondary"
            hint = "CSV disponible para importar a una LDM."
        decorated.append({
            **item,
            "parsed": parsed,
            "status": status,
            "status_label": status_label,
            "badge_class": badge_class,
            "hint": hint,
            "linked_ldm": link.get("ldm_number") if link else "",
            "is_latest": csv_version_key(name, clave) == latest_key,
        })
    return decorated


def provider_quote_status(filename, ldms):
    normalized_name = normalize_ascii(filename).lower()
    provider_tokens = set()
    for ldm in ldms or []:
        token = provider_token(ldm.get("proveedor", ""))
        quote = str(ldm.get("cot_proveedor", "") or "").strip().lower()
        if token:
            provider_tokens.add(token)
        if token and quote and token in normalized_name and quote in normalized_name:
            return {"is_provider_quote": True, "linked": True}
    for token in provider_tokens:
        if normalized_name.endswith(".pdf") and re.match(rf"^{re.escape(token)}\s*-\s*[\w\-]+", normalized_name):
            return {"is_provider_quote": True, "linked": False}
    return {"is_provider_quote": False, "linked": False}


def _format_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.0f} KB"
    return f"{size_bytes / (1024 * 1024):.1f} MB"


def _format_mtime(mtime_ts):
    return datetime.datetime.fromtimestamp(mtime_ts).strftime("%d-%b-%Y %H:%M")


def scan_drive_folder(folder_nm, projects_root, ldms=None, clave=None):
    result = {
        "deliverable": [],
        "working": [],
        "ldm": [],
        "cot": [],
        "other": [],
        "ie_files": [],
        "mem_files": [],
        "ldm_files": [],
        "provider_quote_files": [],
        "cot_files": [],
        "work_files": [],
        "other_files": [],
        "csv_plano": [],
        "error": None,
        "folder": folder_nm,
    }
    if not projects_root:
        result["error"] = "Ruta de proyectos Drive no configurada."
        return result
    folder = os.path.join(projects_root, folder_nm)
    if not os.path.isdir(folder):
        result["error"] = f"Carpeta no encontrada: {folder}"
        return result

    ie_files = []
    mem_files = []
    ldm_files = []
    provider_quote_files = []
    cot_files = []
    work_files = []
    other_files = []
    csv_plano_files = []

    # Pattern: {clave}-v{digits}... (case-insensitive), e.g. OM001-v2-i1-20260420.csv
    csv_pattern = re.compile(rf"^{re.escape(clave)}-v\d", re.IGNORECASE) if clave else None

    for item in sorted(os.listdir(folder)):
        path = os.path.join(folder, item)
        _, ext = os.path.splitext(item.lower())
        if not os.path.isfile(path) or item.lower().endswith(".zip") or ext in IGNORED_SCAN_EXTENSIONS:
            continue
        # Detect CSV plano files before other categories
        if item.lower().endswith(".csv") and csv_pattern and csv_pattern.match(item):
            stat = os.stat(path)
            csv_plano_files.append({
                "name": item,
                "size_str": _format_size(stat.st_size),
                "mtime_str": _format_mtime(stat.st_mtime),
            })
            continue
        provider_quote = provider_quote_status(item, ldms)
        if item.startswith("LDM-"):
            ldm_files.append(item)
        elif provider_quote["is_provider_quote"]:
            provider_quote_files.append(item)
        elif item.startswith(("COT-", "CPROV-")):
            cot_files.append(item)
        elif item.startswith("MEM-"):
            mem_files.append(item)
        elif item.startswith("IE-"):
            ie_files.append(item)
        elif item.upper().startswith("XREF"):
            work_files.append(item)
        else:
            other_files.append(item)

    result["ie_files"] = decorate_latest(ie_files)
    result["mem_files"] = decorate_latest(mem_files)
    result["ldm_files"] = decorate_plain(ldm_files, provider_quote=False)
    result["provider_quote_files"] = [
        {"name": name, "provider_quote": True, "linked": provider_quote_status(name, ldms)["linked"]}
        for name in sorted(provider_quote_files)
    ]
    result["cot_files"] = decorate_plain(cot_files)
    result["work_files"] = decorate_latest(work_files)
    result["other_files"] = decorate_plain(other_files)
    result["csv_plano"] = decorate_csv_plano(csv_plano_files, ldms, clave)
    result["deliverable"] = sorted(ie_files + mem_files + cot_files)
    result["working"] = sorted(work_files)
    result["ldm"] = sorted(ldm_files)
    result["cot"] = sorted(cot_files)
    result["other"] = sorted(other_files + provider_quote_files)
    return result


def find_delivery_files(folder_nm, clave, version, fecha, projects_root, fichas_root, linked_fichas):
    found = {"ie_dwg": None, "ie_pdf": None, "mem_pdf": None, "cot_pdf": None, "fichas": [], "missing": []}
    folder = os.path.join(projects_root, folder_nm) if projects_root else None

    def best_match(search_folder, prefix, ext):
        if not search_folder or not os.path.isdir(search_folder):
            return None
        exact = f"{prefix}{clave}-{version}-{fecha}{ext}"
        if os.path.isfile(os.path.join(search_folder, exact)):
            return exact
        candidates = [item for item in os.listdir(search_folder) if item.startswith(prefix) and item.endswith(ext)]
        return sorted(candidates)[-1] if candidates else None

    if folder:
        found["ie_dwg"] = best_match(folder, "IE-", ".dwg")
        found["ie_pdf"] = best_match(folder, "IE-", ".pdf")
        found["mem_pdf"] = best_match(folder, "MEM-", ".pdf")
        found["cot_pdf"] = best_match(folder, "COT-", ".pdf")
        if not found["ie_dwg"]:
            found["missing"].append("IE-*.dwg")
        if not found["ie_pdf"]:
            found["missing"].append("IE-*.pdf")
        if not found["mem_pdf"]:
            found["missing"].append("MEM-*.pdf")
        if not found["cot_pdf"]:
            found["missing"].append("COT-*.pdf (exporta la cotización como PDF)")

    for ficha in linked_fichas:
        filename = ficha.get("filename", "").strip()
        if not filename:
            found["missing"].append(f"Ficha PDF: {ficha['code']} (sin nombre de archivo)")
            continue
        path = os.path.join(fichas_root, filename) if fichas_root else None
        if path and os.path.isfile(path):
            found["fichas"].append({"name": filename, "path": path})
        else:
            found["missing"].append(f"Ficha PDF: {filename}")
    return found
