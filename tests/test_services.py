import unittest

from tracker.services import (
    apply_task_status_change,
    create_project_with_tasks,
    sync_project_alcances,
    update_observation_details,
    update_observation_checklist_item,
)


class IdFactory:
    def __init__(self):
        self.value = 0

    def __call__(self):
        self.value += 1
        return f"ID{self.value}"


class ProjectServicesTest(unittest.TestCase):
    def test_create_project_assigns_next_folder_and_tasks(self):
        ids = IdFactory()
        existing_projects = [{"id": "OLD", "folder_num": "007"}]
        project, tasks = create_project_with_tasks(
            existing_projects,
            [],
            {
                "name": " Proyecto ",
                "clave": " PRJ ",
                "client": " Cliente ",
                "version": " V2 ",
                "fecha": "2026-04-24",
                "notes": " Nota ",
            },
            ["contactos", "cotizacion"],
            id_factory=ids,
            today_value="2026-04-24",
        )

        self.assertEqual(project["id"], "ID1")
        self.assertEqual(project["folder_num"], "008")
        self.assertEqual(project["name"], "Proyecto")
        self.assertEqual(project["alcances"], ["contactos", "cotizacion"])
        self.assertEqual([task["id"] for task in tasks], ["ID2", "ID3"])
        self.assertEqual([task["project_id"] for task in tasks], ["ID1", "ID1"])
        self.assertEqual(tasks[0]["history"][0]["note"], "Creado con el proyecto")

    def test_sync_project_alcances_adds_and_removes_tasks_with_children(self):
        ids = IdFactory()
        project = {"id": "PRJ1", "alcances": ["contactos", "hvac"]}
        tasks = [
            {"id": "T1", "project_id": "PRJ1", "alcance": "contactos", "parent_task_id": None},
            {"id": "T1A", "project_id": "PRJ1", "alcance": "contactos", "parent_task_id": "T1"},
            {"id": "T2", "project_id": "PRJ1", "alcance": "hvac", "parent_task_id": None},
            {"id": "OTHER", "project_id": "OTHER", "alcance": "contactos", "parent_task_id": None},
        ]

        result = sync_project_alcances(
            project,
            tasks,
            ["hvac", "cotizacion"],
            id_factory=ids,
            today_value="2026-04-24",
        )

        self.assertEqual(result["added"], ["cotizacion"])
        self.assertEqual(result["removed"], ["contactos"])
        self.assertEqual(project["alcances"], ["hvac", "cotizacion"])
        self.assertEqual({task["id"] for task in result["tasks"]}, {"T2", "OTHER", "ID1"})
        added_task = next(task for task in result["tasks"] if task["id"] == "ID1")
        self.assertEqual(added_task["title"], "Cotización")

    def test_apply_task_status_blocks_dependency(self):
        tasks = [
            {"id": "DEP", "project_id": "PRJ1", "alcance": "contactos", "status": "Pendiente", "parent_task_id": None},
            {
                "id": "MAIN",
                "project_id": "PRJ1",
                "alcance": "cuadro_cargas",
                "status": "Pendiente",
                "parent_task_id": None,
            },
        ]

        result = apply_task_status_change(tasks, "PRJ1", "MAIN", "En progreso", today_value="2026-04-24")

        self.assertTrue(result["blocked"])
        self.assertEqual(result["task"]["status"], "Pendiente")
        self.assertEqual(len(result["tasks"]), 2)

    def test_apply_task_status_creates_observation_child(self):
        ids = IdFactory()
        tasks = [
            {
                "id": "MAIN",
                "project_id": "PRJ1",
                "alcance": "contactos",
                "title": "IE - Contactos",
                "status": "Revisión",
                "parent_task_id": None,
                "history": [],
            }
        ]

        result = apply_task_status_change(
            tasks,
            "PRJ1",
            "MAIN",
            "Observaciones",
            "Corregir plano",
            id_factory=ids,
            today_value="2026-04-24",
        )

        self.assertFalse(result["blocked"])
        self.assertEqual(result["task"]["status"], "Observaciones")
        self.assertEqual(len(result["tasks"]), 2)
        self.assertEqual(result["created_observation"]["id"], "ID1")
        self.assertEqual(result["created_observation"]["parent_task_id"], "MAIN")
        self.assertEqual(result["created_observation"]["notes"], "Corregir plano")

    def test_apply_task_status_creates_observation_checklist(self):
        ids = IdFactory()
        tasks = [
            {
                "id": "MAIN",
                "project_id": "PRJ1",
                "alcance": "contactos",
                "title": "IE - Contactos",
                "status": "Revisión",
                "parent_task_id": None,
                "history": [],
            }
        ]

        result = apply_task_status_change(
            tasks,
            "PRJ1",
            "MAIN",
            "Observaciones",
            "Corregir plano",
            "Ajustar contactos\n\nActualizar cuadro",
            id_factory=ids,
            today_value="2026-04-24",
        )

        checklist = result["created_observation"]["checklist"]
        self.assertEqual(result["created_observation"]["id"], "ID1")
        self.assertEqual([item["id"] for item in checklist], ["ID2", "ID3"])
        self.assertEqual([item["text"] for item in checklist], ["Ajustar contactos", "Actualizar cuadro"])
        self.assertFalse(any(item["done"] for item in checklist))

    def test_apply_task_status_does_not_generate_checklist_from_note(self):
        ids = IdFactory()
        tasks = [
            {
                "id": "MAIN",
                "project_id": "PRJ1",
                "alcance": "contactos",
                "title": "IE - Contactos",
                "status": "Revisión",
                "parent_task_id": None,
                "history": [],
            }
        ]

        result = apply_task_status_change(
            tasks,
            "PRJ1",
            "MAIN",
            "Observaciones",
            "Generar plano. Verificar alturas, ubicaciones y circuitos.",
            id_factory=ids,
            today_value="2026-04-24",
        )

        checklist = result["created_observation"]["checklist"]
        self.assertEqual(checklist, [])

    def test_apply_task_status_creates_new_observation_when_already_in_observations(self):
        ids = IdFactory()
        tasks = [
            {
                "id": "MAIN",
                "project_id": "PRJ1",
                "alcance": "contactos",
                "title": "IE - Contactos",
                "status": "Observaciones",
                "parent_task_id": None,
                "history": [],
            },
            {"id": "OBS1", "project_id": "PRJ1", "alcance": "contactos", "parent_task_id": "MAIN"},
        ]

        result = apply_task_status_change(
            tasks,
            "PRJ1",
            "MAIN",
            "Observaciones",
            "Nueva observación",
            "Punto nuevo",
            id_factory=ids,
            today_value="2026-04-24",
        )

        self.assertEqual(len(result["tasks"]), 3)
        self.assertEqual(result["created_observation"]["title"], "Obs. #2 — IE - Contactos")
        self.assertEqual(result["created_observation"]["status"], "Pendiente")

    def test_update_observation_details_edits_note_and_checklist(self):
        ids = IdFactory()
        tasks = [
            {
                "id": "OBS1",
                "project_id": "PRJ1",
                "alcance": "contactos",
                "title": "Obs. #1",
                "status": "Aprobado",
                "parent_task_id": "MAIN",
                "notes": "Antes",
                "history": [],
                "checklist": [
                    {"id": "C1", "text": "Punto existente", "done": True, "done_at": "2026-04-24"},
                ],
            }
        ]

        result = update_observation_details(
            tasks,
            "PRJ1",
            "OBS1",
            "Después",
            "Punto existente\nPunto nuevo",
            id_factory=ids,
            today_value="2026-04-25",
        )

        self.assertEqual(result["task"]["notes"], "Después")
        self.assertEqual(result["task"]["status"], "Pendiente")
        self.assertEqual(result["task"]["checklist"][0]["id"], "C1")
        self.assertTrue(result["task"]["checklist"][0]["done"])
        self.assertEqual(result["task"]["checklist"][1]["id"], "ID1")
        self.assertFalse(result["task"]["checklist"][1]["done"])

    def test_update_observation_checklist_item_updates_status(self):
        tasks = [
            {
                "id": "OBS1",
                "project_id": "PRJ1",
                "alcance": "contactos",
                "title": "Obs. #1",
                "status": "Pendiente",
                "parent_task_id": "MAIN",
                "history": [],
                "checklist": [
                    {"id": "C1", "text": "Ajustar contactos", "done": False, "done_at": None},
                    {"id": "C2", "text": "Actualizar cuadro", "done": False, "done_at": None},
                ],
            }
        ]

        partial = update_observation_checklist_item(tasks, "PRJ1", "OBS1", "C1", True, today_value="2026-04-24")
        self.assertEqual(partial["task"]["status"], "Pendiente")
        self.assertEqual(partial["task"]["checklist"][0]["done_at"], "2026-04-24")

        completed = update_observation_checklist_item(
            partial["tasks"],
            "PRJ1",
            "OBS1",
            "C2",
            True,
            today_value="2026-04-25",
        )
        self.assertEqual(completed["task"]["status"], "Aprobado")
        self.assertEqual(completed["task"]["history"][-1]["note"], "Checklist completado")

        reopened = update_observation_checklist_item(
            completed["tasks"],
            "PRJ1",
            "OBS1",
            "C1",
            False,
            today_value="2026-04-26",
        )
        self.assertEqual(reopened["task"]["status"], "Pendiente")
        self.assertEqual(reopened["task"]["checklist"][0]["done_at"], None)
        self.assertEqual(reopened["task"]["history"][-1]["note"], "Checklist reabierto")


if __name__ == "__main__":
    unittest.main()
