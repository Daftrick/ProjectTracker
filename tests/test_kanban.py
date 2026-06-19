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


class KanbanRouteTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

    def test_kanban_page_200(self):
        r = self.client.get("/kanban")
        self.assertEqual(r.status_code, 200)

    def test_kanban_shows_all_stage_columns(self):
        r = self.client.get("/kanban")
        body = r.data.decode()
        for stage in ("Cotización", "Diseño", "Entregado", "Obra"):
            self.assertIn(stage, body)

    def test_toggle_obra_sets_in_obra(self):
        projects = load("projects")
        target = next((p for p in projects if not p.get("closed_at")), None)
        if not target:
            self.skipTest("No open projects in test data")
        pid = target["id"]
        original = target.get("in_obra", False)
        try:
            r = self.client.post(f"/projects/{pid}/toggle_obra")
            self.assertEqual(r.status_code, 302)
            updated = next(p for p in load("projects") if p["id"] == pid)
            self.assertEqual(updated["in_obra"], not original)
        finally:
            projects = load("projects")
            for p in projects:
                if p["id"] == pid:
                    p["in_obra"] = original
            save("projects", projects)

    def test_toggle_obra_unknown_project_404(self):
        r = self.client.post("/projects/NONEXISTENT/toggle_obra")
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
