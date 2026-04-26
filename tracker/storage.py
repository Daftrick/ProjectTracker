import json
import os
import uuid
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

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
}


def load(key):
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(FILES[key]):
        return []
    with open(FILES[key], "r", encoding="utf-8") as handle:
        return json.load(handle)


def save(key, data):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(FILES[key], "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def new_id():
    return str(uuid.uuid4())[:8].upper()


def today():
    return date.today().isoformat()
