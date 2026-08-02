import unittest

from tracker.domain import project_stage
from tracker import create_app
from tracker.storage import load, save


PROJECT = {
    "id": "KANBAN01",
    "name": "Test Project",
    "clave": "TEST",
    "client": "Cliente",
    "folder_num": "099",
    "version": "V1",
    "fecha": "260101",
    "alcances": ["cotizacion"],
    "notes": "",
    "closed_at": None,
    "in_obra": False,
    "created_at": "2026-01-01",
}

def _task(alcance, status):
    return {
        "id": f"T-{alcance}",
        "project_id": "KANBAN01",
        "alcance": alcance,
        "title": alcance,
        "status": status,
        "source": "propia",
        "external_dep": None,
        "parent_task_id": None,
        "notes": "",
        "history": [],
        "created_at": "2026-01-01",
    }


class ProjectStageTest(unittest.TestCase):

    def test_no_tasks_returns_cotizacion(self):
        self.assertEqual(project_stage(PROJECT, []), "Cotización")

    def test_cot_pendiente_returns_cotizacion(self):
        tasks = [_task("cotizacion", "Pendiente")]
        self.assertEqual(project_stage(PROJECT, tasks), "Cotización")

    def test_cot_en_progreso_returns_cotizacion(self):
        tasks = [_task("cotizacion", "En progreso")]
        self.assertEqual(project_stage(PROJECT, tasks), "Cotización")

    def test_cot_aprobado_only_returns_entregado(self):
        tasks = [_task("cotizacion", "Aprobado")]
        self.assertEqual(project_stage(PROJECT, tasks), "Entregado")

    def test_cot_aprobado_design_pending_returns_diseno(self):
        tasks = [
            _task("cotizacion", "Aprobado"),
            _task("iluminacion", "Pendiente"),
        ]
        self.assertEqual(project_stage(PROJECT, tasks), "Diseño")

    def test_cot_aprobado_design_en_progreso_returns_diseno(self):
        tasks = [
            _task("cotizacion", "Aprobado"),
            _task("iluminacion", "En progreso"),
            _task("contactos", "Pendiente"),
        ]
        self.assertEqual(project_stage(PROJECT, tasks), "Diseño")

    def test_all_aprobado_returns_entregado(self):
        tasks = [
            _task("cotizacion", "Aprobado"),
            _task("iluminacion", "Aprobado"),
            _task("contactos", "Aprobado"),
        ]
        self.assertEqual(project_stage(PROJECT, tasks), "Entregado")

    def test_in_obra_true_overrides_derived_stage(self):
        p = {**PROJECT, "in_obra": True}
        tasks = [_task("cotizacion", "Pendiente")]
        self.assertEqual(project_stage(p, tasks), "Obra")

    def test_in_obra_true_even_with_no_tasks(self):
        p = {**PROJECT, "in_obra": True}
        self.assertEqual(project_stage(p, []), "Obra")

    def test_subtasks_not_counted(self):
        parent = _task("cotizacion", "Aprobado")
        child = {**_task("cotizacion", "Pendiente"), "id": "T-child", "parent_task_id": "T-cotizacion"}
        self.assertEqual(project_stage(PROJECT, [parent, child]), "Entregado")



class KanbanRoutesTest(unittest.TestCase):
    """Cubre las rutas /kanban y toggle_obra restauradas (el template
    kanban.html había quedado huérfano tras un refactor previo)."""

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        projects = load("projects")
        self._saved_projects = [p for p in projects if p["id"] != PROJECT["id"]]
        save("projects", self._saved_projects + [dict(PROJECT)])

    def tearDown(self):
        save("projects", self._saved_projects)

    def _get_project(self):
        return next(p for p in load("projects") if p["id"] == PROJECT["id"])

    def test_kanban_page_loads_and_lists_project_in_cotizacion(self):
        response = self.client.get("/kanban")
        self.assertEqual(response.status_code, 200)
        body = response.get_data(as_text=True)
        self.assertIn(PROJECT["clave"], body)
        self.assertIn("Portafolio", body)

    def test_toggle_obra_moves_project_to_obra_and_back(self):
        response = self.client.post(f"/projects/{PROJECT['id']}/toggle_obra", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self._get_project()["in_obra"])

        response = self.client.get("/kanban")
        self.assertIn(PROJECT["clave"], response.get_data(as_text=True))

        response = self.client.post(f"/projects/{PROJECT['id']}/toggle_obra", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(self._get_project()["in_obra"])

    def test_toggle_obra_unknown_project_does_not_crash(self):
        response = self.client.post("/projects/does-not-exist/toggle_obra", follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
