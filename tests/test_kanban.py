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



if __name__ == "__main__":
    unittest.main()
