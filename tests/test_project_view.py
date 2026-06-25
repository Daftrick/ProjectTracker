import unittest
from unittest.mock import patch

from tracker.project_view import (
    build_consistency_view,
    build_ldm_row_views,
    build_project_detail_context,
    build_quote_row_views,
    build_task_row_views,
)


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
            "materiales": [{
                "project_id": "PRJ1",
                "subtotal_cot": 900,
                "seq": 1,
                "items": [
                    {"description": "Cable"},
                    {"description": "Artículo viejo", "catalog_deleted": True},
                ],
            }],
            "fichas": [
                {"id": "F1", "projects": ["PRJ1"]},
                {"id": "F2", "projects": []},
            ],
            "team": [{"id": "M1", "name": "Ana"}],
            "bundles": [],
        }

        def fake_load(key):
            return data[key]

        with patch("tracker.project_view.load", side_effect=fake_load), \
             patch("tracker.project_view.catalog_maps", return_value=({}, {})), \
             patch("tracker.project_view.hydrate_quote", side_effect=lambda quote, *_: quote), \
             patch("tracker.project_view.hydrate_ldm", side_effect=lambda ldm, *_: ldm), \
             patch("tracker.project_view.today", return_value="2026-04-28"):
            context = build_project_detail_context(project)

        self.assertEqual(context["project"], project)
        self.assertEqual([task["id"] for task in context["main_tasks"]], ["T1", "T2"])
        self.assertEqual([row["task"]["id"] for row in context["task_rows"]], ["T1", "T2"])
        self.assertEqual(context["task_rows"][0]["active_observations"][0]["task"]["id"], "OBS1")
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
        self.assertEqual(context["ldm_rows"][0]["item_count"], 2)
        self.assertEqual(context["ldm_rows"][0]["deleted_catalog_count"], 1)
        self.assertEqual(context["folder_name"], "IE-004-OM001")
        self.assertEqual(context["file_ie"], "IE-OM001-V2-260428.dwg")
        self.assertEqual(context["file_xref"], "XREF-OM001-V2-260428.dwg")

    def test_build_task_row_views_precomputes_observation_values(self):
        task = {
            "id": "T1",
            "source": "",
            "info_status": "",
            "status": "Pendiente",
            "_blocked": True,
            "history": [{"date": "2026-05-06", "from": "Pendiente", "to": "En progreso"}],
        }
        rows = build_task_row_views([task], {
            "T1": [
                {
                    "id": "OBS1",
                    "status": "Pendiente",
                    "checklist": [
                        {"text": "Revisar plano", "done": True},
                        {"text": "Enviar PDF", "done": False},
                    ],
                },
                {"id": "OBS2", "status": "Aprobado"},
            ]
        })

        self.assertTrue(rows[0]["blocked"])
        self.assertEqual(rows[0]["source"], "propia")
        self.assertEqual(rows[0]["info_status"], "Pendiente")
        self.assertEqual(rows[0]["last_history"]["to"], "En progreso")
        self.assertTrue(rows[0]["has_detail"])
        self.assertEqual(len(rows[0]["active_observations"]), 1)
        self.assertEqual(rows[0]["active_observations"][0]["checklist_text"], "Revisar plano\nEnviar PDF")
        self.assertEqual(rows[0]["active_observations"][0]["done_count"], 1)
        self.assertEqual(rows[0]["active_observations"][0]["checklist_count"], 2)

    def test_build_ldm_row_views_precomputes_materials_template_values(self):
        rows = build_ldm_row_views([
            {
                "id": "L1",
                "items": [
                    {"description": "Conduit"},
                    {"description": "Descontinuado", "catalog_deleted": True},
                ],
            },
            {"id": "L2"},
        ])

        self.assertEqual(rows[0]["item_count"], 2)
        self.assertEqual(rows[0]["deleted_catalog_count"], 1)
        self.assertEqual(rows[0]["deleted_catalog_items"][0]["description"], "Descontinuado")
        self.assertEqual(rows[1]["item_count"], 0)
        self.assertEqual(rows[1]["deleted_catalog_items"], [])

    def test_build_quote_row_views_precomputes_deleted_catalog_values(self):
        rows = build_quote_row_views([
            {
                "id": "Q1",
                "items": [
                    {"description": "Tablero"},
                    {"description": "Artículo removido", "catalog_deleted": True},
                ],
            },
            {"id": "Q2"},
        ])

        self.assertEqual(rows[0]["item_count"], 2)
        self.assertEqual(rows[0]["deleted_catalog_count"], 1)
        self.assertEqual(rows[0]["deleted_catalog_items"][0]["description"], "Artículo removido")
        self.assertEqual(rows[1]["item_count"], 0)
        self.assertEqual(rows[1]["deleted_catalog_items"], [])

    def test_build_consistency_view_prepares_template_rows(self):
        view = build_consistency_view({
            "status": "warning",
            "quote_unlinked": {"count": 1, "total": 50},
            "ldm_unlinked": {"count": 0, "total": 0},
        })

        self.assertEqual(view["badge_color"], "warning")
        self.assertEqual(view["badge_icon"], "exclamation-triangle-fill")
        self.assertTrue(view["has_unlinked_rows"])

    def test_build_consistency_view_prepares_visual_review_helpers(self):
        view = build_consistency_view({
            "status": "ok",
            "coverage": {
                "quote_catalog_coverage_pct": 100,
                "ldm_catalog_coverage_pct": 50,
            },
            "visual_warnings": [{"title": "Sin LDM", "level": "warning"}],
        })

        self.assertEqual(view["quote_coverage_color"], "success")
        self.assertEqual(view["ldm_coverage_color"], "warning")
        self.assertTrue(view["has_visual_warnings"])
        self.assertEqual(view["visual_warnings"][0]["title"], "Sin LDM")


if __name__ == "__main__":
    unittest.main()
