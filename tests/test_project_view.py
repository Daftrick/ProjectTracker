import unittest
from unittest.mock import patch

from tracker.project_view import build_project_detail_context


class ProjectViewTest(unittest.TestCase):
    def test_build_project_detail_context_groups_and_calculates_totals(self):
        project = {
            "id": "PRJ1",
            "clave": "OM001",
            "version": "V2",
            "fecha": "260428",
            "folder_num": "004",
        }
        data = {
            "tasks": [
                {"id": "T1", "project_id": "PRJ1", "alcance": "contactos", "status": "Aprobado", "parent_task_id": None},
                {"id": "T2", "project_id": "PRJ1", "alcance": "cotizacion", "status": "Aprobado", "parent_task_id": None},
                {"id": "OBS1", "project_id": "PRJ1", "alcance": "contactos", "status": "Pendiente", "parent_task_id": "T1"},
                {"id": "OTHER", "project_id": "OTHER", "alcance": "contactos", "status": "Pendiente", "parent_task_id": None},
            ],
            "deliveries": [{"project_id": "PRJ1", "date": "2026-04-28", "dtype": "completa"}],
            "quotes": [{"project_id": "PRJ1", "total": 1500, "created_at": "2026-04-28"}],
            "materiales": [{"project_id": "PRJ1", "subtotal_cot": 900, "seq": 1}],
            "fichas": [
                {"id": "F1", "projects": ["PRJ1"]},
                {"id": "F2", "projects": []},
            ],
            "team": [{"id": "M1", "name": "Ana"}],
            "bundles": [],
            "comparison_rules": [],
        }

        def fake_load(key):
            return data[key]

        with patch("tracker.project_view.load", side_effect=fake_load), \
             patch("tracker.project_view.catalog_maps", return_value=({}, {})), \
             patch("tracker.project_view.hydrate_quote", side_effect=lambda quote, *_: quote), \
             patch("tracker.project_view.hydrate_ldm", side_effect=lambda ldm, *_: ldm), \
             patch("tracker.project_view.load_config", return_value={"drive_projects_path": "", "drive_fichas_path": ""}), \
             patch("tracker.project_view.scan_drive_folder", return_value={"files": []}), \
             patch("tracker.project_view.find_delivery_files", return_value={"ie_pdf": "IE.pdf"}), \
             patch("tracker.project_view.today", return_value="2026-04-28"):
            context = build_project_detail_context(project)

        self.assertEqual(context["project"], project)
        self.assertEqual([task["id"] for task in context["main_tasks"]], ["T1", "T2"])
        self.assertEqual(context["subtasks"]["T1"][0]["id"], "OBS1")
        self.assertEqual(context["delete_preview"]["tasks"], 3)
        self.assertEqual(context["delete_preview"]["quotes"], 1)
        self.assertEqual(context["delete_preview"]["ldms"], 1)
        self.assertEqual(context["delete_preview"]["deliveries"], 1)
        self.assertEqual(context["delete_preview"]["linked_fichas"], 1)
        self.assertTrue(context["can_close"])
        self.assertEqual(context["linked_fichas"][0]["id"], "F1")
        self.assertEqual(context["unlinked_fichas"][0]["id"], "F2")
        self.assertEqual(context["total_cotizado"], 1500)
        self.assertEqual(context["costo_proveedor"], 900)
        self.assertEqual(context["margen"], 600)
        self.assertEqual(context["folder_name"], "IE-004-OM001")
        self.assertEqual(context["file_ie"], "IE-OM001-V2-260428")
        self.assertEqual(context["file_xref"], "XREF-OM001-V2-260428")


if __name__ == "__main__":
    unittest.main()
