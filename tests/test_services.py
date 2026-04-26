import unittest

from tracker.services import apply_task_status_change, create_project_with_tasks, sync_project_alcances


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


if __name__ == "__main__":
    unittest.main()
