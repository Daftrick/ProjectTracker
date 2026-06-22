import json
import os
import tempfile
import threading
import uuid
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# TOCTOU note: acquired per-call, not per read-modify-write cycle —
# two threads can interleave load→modify→save (last write wins).
# Acceptable at 2-3 users; full SQLite migration resolves this (v1.5+).
_LOCK = threading.Lock()

FILES = {
    "projects": os.path.join(DATA_DIR, "projects.json"),
    "tasks": os.path.join(DATA_DIR, "tasks.json"),
    "deliveries": os.path.join(DATA_DIR, "deliveries.json"),
    "quotes": os.path.join(DATA_DIR, "quotes.json"),
    "materiales": os.path.join(DATA_DIR, "materiales.json"),
    "fichas": os.path.join(DATA_DIR, "fichas.json"),
    "catalogo": os.path.join(DATA_DIR, "catalogo.json"),
    "proveedores": os.path.join(DATA_DIR, "proveedores.json"),
    "team": os.path.join(DATA_DIR, "team.json"),
    "bundles": os.path.join(DATA_DIR, "bundles.json"),
    "comparison_rules": os.path.join(DATA_DIR, "comparison_rules.json"),
    "comparison_ignored_items": os.path.join(DATA_DIR, "comparison_ignored_items.json"),
    "company":           os.path.join(DATA_DIR, "company.json"),
    "project_templates": os.path.join(DATA_DIR, "project_templates.json"),
    "quote_templates":   os.path.join(DATA_DIR, "quote_templates.json"),
}


def load(key):
    with _LOCK:
        try:
            with open(FILES[key], "r", encoding="utf-8") as handle:
                return json.load(handle)
        except FileNotFoundError:
            return []


def save(key, data):
    path = FILES[key]
    dir_name = os.path.dirname(path)
    with _LOCK:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=dir_name, delete=False, suffix=".tmp"
        ) as tmp:
            json.dump(data, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name
        os.replace(tmp_path, path)


def new_id():
    return str(uuid.uuid4())[:8].upper()


def today():
    return date.today().isoformat()
