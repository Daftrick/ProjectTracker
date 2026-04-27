from .domain import ALCANCES_BY_ID, check_blocked
from .storage import new_id, today


def next_folder_number(projects):
    numbers = [int(project["folder_num"]) for project in projects if project.get("folder_num", "").isdigit()]
    return (max(numbers) + 1) if numbers else 1


def build_scope_task(project_id, alcance_id, note, id_factory=new_id, today_value=None):
    created_at = today_value or today()
    alcance = ALCANCES_BY_ID.get(alcance_id, {})
    return {
        "id": id_factory(),
        "project_id": project_id,
        "alcance": alcance_id,
        "title": alcance.get("nombre", alcance_id),
        "source": alcance.get("source", "propia"),
        "external_dep": alcance.get("dep_label"),
        "status": "Pendiente",
        "parent_task_id": None,
        "notes": "",
        "history": [{"from": None, "to": "Pendiente", "date": created_at, "note": note}],
        "created_at": created_at,
    }


def create_project_with_tasks(projects, tasks, fields, selected_alcances, id_factory=new_id, today_value=None):
    created_at = today_value or today()
    project_id = id_factory()
    project = {
        "id": project_id,
        "name": fields.get("name", "").strip(),
        "clave": fields.get("clave", "").strip(),
        "client": fields.get("client", "").strip(),
        "version": fields.get("version", "V1").strip(),
        "fecha": fields.get("fecha", "").strip(),
        "alcances": list(selected_alcances),
        "notes": fields.get("notes", "").strip(),
        "folder_num": f"{next_folder_number(projects):03d}",
        "closed_at": None,
        "created_at": created_at,
    }
    updated_tasks = list(tasks)
    for alcance_id in selected_alcances:
        updated_tasks.append(
            build_scope_task(project_id, alcance_id, "Creado con el proyecto", id_factory, created_at)
        )
    return project, updated_tasks


def sync_project_alcances(project, tasks, new_alcances, id_factory=new_id, today_value=None):
    change_date = today_value or today()
    new_alcances = list(new_alcances)
    old_alcances = project.get("alcances", [])
    added = [alcance for alcance in new_alcances if alcance not in old_alcances]
    removed = [alcance for alcance in old_alcances if alcance not in new_alcances]
    updated_tasks = list(tasks)

    for alcance_id in added:
        updated_tasks.append(
            build_scope_task(project["id"], alcance_id, "Alcance agregado al proyecto", id_factory, change_date)
        )

    removed_ids = {
        task["id"]
        for task in updated_tasks
        if task["project_id"] == project["id"] and task.get("alcance") in removed and not task.get("parent_task_id")
    }
    updated_tasks = [
        task for task in updated_tasks if task["id"] not in removed_ids and task.get("parent_task_id") not in removed_ids
    ]
    project["alcances"] = new_alcances
    return {"added": added, "removed": removed, "tasks": updated_tasks}


def build_checklist_items(checklist_text, id_factory=new_id):
    return [
        {"id": id_factory(), "text": line.strip(), "done": False, "done_at": None}
        for line in str(checklist_text or "").splitlines()
        if line.strip()
    ]


def build_edited_checklist_items(checklist_text, existing_items, id_factory=new_id):
    remaining = list(existing_items or [])
    edited = []
    for line in str(checklist_text or "").splitlines():
        text = line.strip()
        if not text:
            continue
        match = next((item for item in remaining if item.get("text") == text), None)
        if match:
            remaining.remove(match)
            edited.append({
                "id": match.get("id") or id_factory(),
                "text": text,
                "done": bool(match.get("done")),
                "done_at": match.get("done_at"),
            })
        else:
            edited.append({"id": id_factory(), "text": text, "done": False, "done_at": None})
    return edited


def apply_task_status_change(
    tasks,
    project_id,
    task_id,
    new_status,
    note="",
    checklist_text="",
    id_factory=new_id,
    today_value=None,
):
    change_date = today_value or today()
    updated_tasks = list(tasks)
    task = next((item for item in updated_tasks if item["id"] == task_id), None)
    if not task:
        return {"task": None, "tasks": updated_tasks, "blocked": False, "created_observation": None}

    main_tasks = [item for item in updated_tasks if item["project_id"] == project_id and not item.get("parent_task_id")]
    if new_status in ("En progreso", "Revisión") and check_blocked(task, main_tasks):
        return {"task": task, "tasks": updated_tasks, "blocked": True, "created_observation": None}

    old_status = task["status"]
    clean_note = str(note or "").strip()
    task["status"] = new_status
    task.setdefault("history", []).append({
        "from": old_status,
        "to": new_status,
        "date": change_date,
        "note": clean_note or f"Cambio: {old_status} → {new_status}",
    })

    created_observation = None
    should_create_observation = (
        new_status == "Observaciones"
        and (old_status != "Observaciones" or clean_note or str(checklist_text or "").strip())
    )
    if should_create_observation:
        obs_num = sum(1 for item in updated_tasks if item.get("parent_task_id") == task_id) + 1
        created_observation = {
            "id": id_factory(),
            "project_id": project_id,
            "alcance": task["alcance"],
            "title": f"Obs. #{obs_num} — {task['title']}",
            "source": "propia",
            "external_dep": None,
            "status": "Pendiente",
            "parent_task_id": task_id,
            "notes": clean_note,
            "checklist": build_checklist_items(checklist_text, id_factory),
            "history": [{"from": None, "to": "Pendiente", "date": change_date, "note": f"Subtarea observación #{obs_num}"}],
            "created_at": change_date,
        }
        updated_tasks.append(created_observation)

    return {
        "task": task,
        "tasks": updated_tasks,
        "blocked": False,
        "created_observation": created_observation,
    }


def update_observation_details(tasks, project_id, observation_id, note="", checklist_text="", id_factory=new_id, today_value=None):
    change_date = today_value or today()
    updated_tasks = list(tasks)
    observation = next(
        (
            item
            for item in updated_tasks
            if item["id"] == observation_id
            and item["project_id"] == project_id
            and item.get("parent_task_id")
        ),
        None,
    )
    if not observation:
        return {"task": None, "tasks": updated_tasks}

    old_status = observation.get("status", "Pendiente")
    observation["notes"] = str(note or "").strip()
    checklist = build_edited_checklist_items(checklist_text, observation.get("checklist", []), id_factory)
    observation["checklist"] = checklist
    if checklist:
        observation["status"] = "Aprobado" if all(item.get("done") for item in checklist) else "Pendiente"
    else:
        observation["status"] = "Pendiente"
    observation.setdefault("history", []).append({
        "from": old_status,
        "to": observation["status"],
        "date": change_date,
        "note": "Observación editada",
    })
    return {"task": observation, "tasks": updated_tasks}


def update_observation_checklist_item(tasks, project_id, observation_id, item_id, done, today_value=None):
    change_date = today_value or today()
    updated_tasks = list(tasks)
    observation = next(
        (
            item
            for item in updated_tasks
            if item["id"] == observation_id
            and item["project_id"] == project_id
            and item.get("parent_task_id")
        ),
        None,
    )
    if not observation:
        return {"task": None, "tasks": updated_tasks}

    checklist = observation.get("checklist", [])
    target = next((item for item in checklist if item.get("id") == item_id), None)
    if not target:
        return {"task": observation, "tasks": updated_tasks}

    target["done"] = bool(done)
    target["done_at"] = change_date if done else None

    if checklist:
        old_status = observation.get("status", "Pendiente")
        new_status = "Aprobado" if all(item.get("done") for item in checklist) else "Pendiente"
        if old_status != new_status:
            observation["status"] = new_status
            observation.setdefault("history", []).append({
                "from": old_status,
                "to": new_status,
                "date": change_date,
                "note": "Checklist completado" if new_status == "Aprobado" else "Checklist reabierto",
            })

    return {"task": observation, "tasks": updated_tasks}
