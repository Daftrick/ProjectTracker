import datetime
import json
import os
import re
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor, as_completed

from .storage import DATA_DIR, load, save

IGNORED_SCAN_EXTENSIONS = {".bak", ".dwl", ".dwl2"}

# Compiled regex patterns for performance
PATTERNS = {
    'csv_plano': None,  # Will be compiled with clave
    'xref': re.compile(r'^XREF', re.IGNORECASE),
    'ldm': re.compile(r'^LDM-', re.IGNORECASE),
    'cot': re.compile(r'^(COT-|CPROV-)', re.IGNORECASE),
    'mem': re.compile(r'^MEM-', re.IGNORECASE),
    'ie': re.compile(r'^IE-', re.IGNORECASE),
    'provider_quote': None,  # Will be compiled with token
}

CONFIG_FILE = os.path.join(DATA_DIR, "config.json")
CONFIG_DEFAULTS = {
    "drive_projects_path": "",
    "drive_fichas_path": "",
    "drive_projects_path_windows": "",
    "drive_fichas_path_windows": "",
    "drive_projects_path_macos": "",
    "drive_fichas_path_macos": "",
    "drive_projects_path_linux": "",
    "drive_fichas_path_linux": "",
}


class DriveCache:
    """LRU cache for drive folder scans with TTL and mtime-based invalidation"""

    def __init__(self, ttl=300):  # 5 minutes default
        self.cache = {}
        self.ttl = ttl

    def _get_folder_mtime(self, folder):
        """Get folder modification time for invalidation"""
        try:
            return os.stat(folder).st_mtime
        except (OSError, FileNotFoundError):
            return None

    def _make_key(self, folder, clave, ldms_hash):
        """Create cache key from folder path and parameters"""
        return (folder, clave or "", ldms_hash)

    def is_valid(self, key):
        """Check if cached result is still valid"""
        if key not in self.cache:
            return False

        cached_result, mtime_then, timestamp = self.cache[key]

        # Check TTL
        if time.time() - timestamp > self.ttl:
            return False

        # Check if folder has changed
        folder, _, _ = key
        mtime_now = self._get_folder_mtime(folder)
        return mtime_then == mtime_now

    def get(self, folder, clave, ldms_hash):
        """Get cached result if valid"""
        key = self._make_key(folder, clave, ldms_hash)
        if self.is_valid(key):
            return self.cache[key][0]
        return None

    def put(self, folder, clave, ldms_hash, result):
        """Store result in cache"""
        key = self._make_key(folder, clave, ldms_hash)
        mtime_now = self._get_folder_mtime(folder)
        self.cache[key] = (result, mtime_now, time.time())

        # Simple LRU: keep only last 50 entries
        if len(self.cache) > 50:
            oldest_key = min(self.cache.keys(),
                           key=lambda k: self.cache[k][2])
            del self.cache[oldest_key]


# Global cache instance
_drive_cache = DriveCache()


class LazyFileLoader:
    """Lazy loader for large files to avoid loading all file metadata at once"""

    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self._executor = None

    def _get_file_info(self, file_path):
        """Get file information for a single file"""
        try:
            stat = os.stat(file_path)
            return {
                "name": os.path.basename(file_path),
                "size": stat.st_size,
                "mtime": stat.st_mtime,
                "path": file_path
            }
        except (OSError, FileNotFoundError):
            return None

    def load_files_parallel(self, folder_path, file_filter=None):
        """Load file information in parallel for better performance"""
        if not os.path.isdir(folder_path):
            return []

        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=self.max_workers)

        file_paths = []
        for item in os.listdir(folder_path):
            path = os.path.join(folder_path, item)
            if os.path.isfile(path) and (file_filter is None or file_filter(item)):
                file_paths.append(path)

        # Submit all file info requests
        future_to_path = {
            self._executor.submit(self._get_file_info, path): path
            for path in file_paths
        }

        # Collect results as they complete
        results = []
        for future in as_completed(future_to_path):
            result = future.result()
            if result:
                results.append(result)

        return sorted(results, key=lambda x: x["name"])

    def shutdown(self):
        """Shutdown the thread pool"""
        if self._executor:
            self._executor.shutdown(wait=True)
            self._executor = None


# Global lazy loader instance
_lazy_loader = LazyFileLoader()


def clear_drive_cache():
    """Clear the drive scan cache. Useful for testing or forcing fresh scans."""
    global _drive_cache
    _drive_cache = DriveCache()


def clear_lazy_loader():
    """Shutdown and clear the lazy loader thread pool."""
    global _lazy_loader
    _lazy_loader.shutdown()
    _lazy_loader = LazyFileLoader()


def current_platform_key():
    if os.name == "nt":
        return "windows"
    if sys.platform == "darwin":
        return "macos"
    return "linux"


def platform_label(platform_key=None):
    labels = {"windows": "Windows", "macos": "macOS", "linux": "Linux"}
    return labels.get(platform_key or current_platform_key(), platform_key or current_platform_key())


def _platform_path_key(base_key, platform_key=None):
    return f"{base_key}_{platform_key or current_platform_key()}"


def _infer_platform_for_path(path):
    clean = str(path or "").strip()
    if not clean:
        return ""
    if re.match(r"^[A-Za-z]:[\\/]", clean) or "\\" in clean:
        return "windows"
    if clean.startswith(("/Users/", "/Volumes/")):
        return "macos"
    if clean.startswith("/"):
        return "linux"
    return current_platform_key()


def normalize_config(cfg):
    normalized = dict(CONFIG_DEFAULTS)
    normalized.update(cfg or {})
    for base_key in ("drive_projects_path", "drive_fichas_path"):
        legacy_value = str(normalized.get(base_key, "") or "").strip()
        inferred = _infer_platform_for_path(legacy_value)
        platform_key = _platform_path_key(base_key, inferred) if inferred else ""
        if platform_key and not normalized.get(platform_key):
            normalized[platform_key] = legacy_value
    return normalized


def resolve_config_path(cfg, base_key, platform_key=None):
    normalized = normalize_config(cfg)
    platform_key = platform_key or current_platform_key()
    platform_value = str(normalized.get(_platform_path_key(base_key, platform_key), "") or "").strip()
    if platform_value:
        return platform_value
    legacy_value = str(normalized.get(base_key, "") or "").strip()
    if legacy_value and _infer_platform_for_path(legacy_value) == platform_key:
        return legacy_value
    return ""


def active_drive_paths(cfg=None):
    cfg = normalize_config(cfg if cfg is not None else load_config())
    platform_key = current_platform_key()
    return {
        "platform": platform_key,
        "platform_label": platform_label(platform_key),
        "projects": resolve_config_path(cfg, "drive_projects_path", platform_key),
        "fichas": resolve_config_path(cfg, "drive_fichas_path", platform_key),
    }


def load_config():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(CONFIG_FILE):
        return normalize_config({})
    with open(CONFIG_FILE, encoding="utf-8") as handle:
        return normalize_config(json.load(handle))


def save_config(cfg):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CONFIG_FILE, "w", encoding="utf-8") as handle:
        json.dump(normalize_config(cfg), handle, ensure_ascii=False, indent=2)


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

    # Compile provider quote pattern if needed
    for token in provider_tokens:
        if not PATTERNS['provider_quote']:
            PATTERNS['provider_quote'] = re.compile(rf"^{re.escape(token)}\s*-\s*[\w\-]+", re.IGNORECASE)
        if normalized_name.endswith(".pdf") and PATTERNS['provider_quote'].match(normalized_name):
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
    # Compile dynamic patterns if not already done
    if clave and not PATTERNS['csv_plano']:
        PATTERNS['csv_plano'] = re.compile(rf"^{re.escape(clave)}-v\d", re.IGNORECASE)

    # Create hash for LDMs to detect changes
    ldms_hash = hash(json.dumps(ldms or [], sort_keys=True, default=str))

    # Check cache first
    cached_result = _drive_cache.get(projects_root, clave, ldms_hash)
    if cached_result:
        return cached_result

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

    # Use compiled patterns
    csv_pattern = PATTERNS['csv_plano'] if clave else None

    # Filter function for file types we care about
    def file_filter(filename):
        _, ext = os.path.splitext(filename.lower())
        return not (filename.lower().endswith(".zip") or ext in IGNORED_SCAN_EXTENSIONS)

    # Load files in parallel for better performance
    file_infos = _lazy_loader.load_files_parallel(folder, file_filter)

    for file_info in file_infos:
        item = file_info["name"]
        path = file_info["path"]

        # Detect CSV plano files before other categories
        if item.lower().endswith(".csv") and csv_pattern and csv_pattern.match(item):
            csv_plano_files.append({
                "name": item,
                "size_str": _format_size(file_info["size"]),
                "mtime_str": _format_mtime(file_info["mtime"]),
            })
            continue

        provider_quote = provider_quote_status(item, ldms)
        if PATTERNS['ldm'].match(item):
            ldm_files.append(item)
        elif provider_quote["is_provider_quote"]:
            provider_quote_files.append(item)
        elif PATTERNS['cot'].match(item):
            cot_files.append(item)
        elif PATTERNS['mem'].match(item):
            mem_files.append(item)
        elif PATTERNS['ie'].match(item):
            ie_files.append(item)
        elif PATTERNS['xref'].match(item.upper()):
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

    # Cache the result
    _drive_cache.put(projects_root, clave, ldms_hash, result)

    return result


def batch_scan_drive_folders(folder_names, projects_root, ldms_dict=None, max_workers=4):
    """
    Scan multiple drive folders in parallel for better performance.

    Args:
        folder_names: List of folder names to scan
        projects_root: Root path for projects
        ldms_dict: Dictionary mapping folder names to their LDMs (optional)
        max_workers: Maximum number of parallel workers

    Returns:
        Dictionary mapping folder names to their scan results
    """
    if not projects_root or not os.path.isdir(projects_root):
        return {name: {"error": "Invalid projects root path"} for name in folder_names}

    results = {}
    start_time = time.time()
    processed_count = 0
    error_count = 0

    def scan_single_folder(folder_name):
        nonlocal processed_count, error_count
        try:
            ldms = ldms_dict.get(folder_name, []) if ldms_dict else []
            # Extract clave from folder name (IE-{folder_num}-{clave})
            clave = None
            if folder_name.startswith("IE-") and "-" in folder_name:
                parts = folder_name.split("-")
                if len(parts) >= 3:
                    clave = parts[2]
            result = scan_drive_folder(folder_name, projects_root, ldms, clave)
            processed_count += 1
            return folder_name, result
        except Exception as exc:
            error_count += 1
            return folder_name, {"error": f"Scan failed: {exc}"}

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_folder = {
            executor.submit(scan_single_folder, name): name
            for name in folder_names
        }

        for future in as_completed(future_to_folder):
            folder_name = future_to_folder[future]
            try:
                name, result = future.result()
                results[name] = result
            except Exception as exc:
                results[folder_name] = {"error": f"Batch processing failed: {exc}"}
                error_count += 1

    # Add performance metrics to results
    total_time = time.time() - start_time
    results["_batch_metrics"] = {
        "total_folders": len(folder_names),
        "processed_successfully": processed_count,
        "errors": error_count,
        "total_time_seconds": round(total_time, 3),
        "avg_time_per_folder": round(total_time / len(folder_names), 3) if folder_names else 0,
        "parallel_workers": max_workers
    }

    return results


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
