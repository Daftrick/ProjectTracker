#!/usr/bin/env python3
"""
Migración v31.x → semáforo de proyectos.
Agrega 'deadline' y 'updated_at' a cada proyecto en data/projects.json.
Es idempotente: si el campo ya existe, no lo sobreescribe.
"""
import json
import shutil
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "projects.json"
BACKUP_FILE = DATA_FILE.with_suffix(".json.bak")


def main():
    if not DATA_FILE.exists():
        print(f"ERROR: no se encontró {DATA_FILE}")
        return

    with open(DATA_FILE, encoding="utf-8") as f:
        projects = json.load(f)

    # Backup antes de tocar nada
    shutil.copy2(DATA_FILE, BACKUP_FILE)
    print(f"Backup guardado en: {BACKUP_FILE}")

    today = date.today().isoformat()
    modified = 0

    for p in projects:
        changed = False

        if "deadline" not in p:
            p["deadline"] = None
            changed = True

        if "updated_at" not in p:
            p["updated_at"] = p.get("created_at") or today
            changed = True

        if changed:
            modified += 1
            print(f"  [{p['id']}] {p['name']} → deadline=null, updated_at={p['updated_at']}")

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(projects, f, ensure_ascii=False, indent=2)

    print(f"\n{modified} proyecto(s) migrado(s). {len(projects) - modified} ya tenían los campos.")
    print("Ahora podés editar 'deadline' en data/projects.json o desde la UI cuando esté lista.")


if __name__ == "__main__":
    main()
