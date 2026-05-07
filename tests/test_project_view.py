import unittest
from unittest.mock import patch

from tracker.project_view import (
    build_consistency_view,
    build_drive_scan_view,
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
            "comparison_rules": [],
            "comparison_ignored_items": [],
        }

        def fake_load(key):
            return data[key]

        with patch("tracker.project_view.load", side_effect=fake_load), \
             patch("tracker.project_view.catalog_maps", return_value=({}, {})), \
             patch("tracker.project_view.hydrate_quote", side_effect=lambda quote, *_: quote), \
             patch("tracker.project_view.hydrate_ldm", side_effect=lambda ldm, *_: ldm), \
             patch("tracker.project_view.load_config", return_value={"drive_projects_path": "", "drive_fichas_path": ""}), \
             patch("tracker.project_view.scan_drive_folder", return_value={
                 "files": [],
                 "csv_plano": [
                     {"name": "nuevo.csv", "linked_ldm": "", "status_label": "Listo"},
                     {"name": "vinculado.csv", "linked_ldm": "LDM-OM001-01", "status_label": "Usado"},
                 ],
             }), \
             patch("tracker.project_view.find_delivery_files", return_value={"ie_pdf": "IE.pdf"}), \
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
        self.assertEqual([item["name"] for item in context["importable_csvs"]], ["nuevo.csv"])
        self.assertFalse(context["scan"]["has_ldm_documents"])
        self.assertEqual(context["ldm_rows"][0]["item_count"], 2)
        self.assertEqual(context["ldm_rows"][0]["deleted_catalog_count"], 1)
        self.assertEqual(context["folder_name"], "IE-004-OM001")
        self.assertEqual(context["file_ie"], "IE-OM001-V2-260428")
        self.assertEqual(context["file_xref"], "XREF-OM001-V2-260428")

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

    def test_build_drive_scan_view_precomputes_display_classes(self):
        scan = build_drive_scan_view({
            "ie_files": [
                {"name": "IE-OM001.pdf", "highlight": True},
                {"name": "IE-OM001.dwg", "highlight": True},
                {"name": "old.txt", "highlight": False},
            ],
            "provider_quote_files": [{"name": "PROV.pdf", "linked": True}],
            "csv_plano": [
                {"name": "COT.csv", "status": "importado"},
                {"name": "OLD.csv", "status": "desactualizado"},
                {"name": "NEW.csv", "status": "nuevo"},
            ],
        })

        self.assertEqual(
            [file["display_class"] for file in scan["ie_files"]],
            ["drive-code-ie-pdf", "drive-code-ie-dwg", "drive-code-muted"],
        )
        self.assertEqual(scan["provider_quote_files"][0]["display_class"], "drive-code-prov")
        self.assertEqual(
            [file["display_class"] for file in scan["csv_plano"]],
            ["drive-code-cot", "drive-code-prov", "drive-code-muted"],
        )
        self.assertTrue(scan["has_ldm_documents"])

    def test_build_consistency_view_prepares_template_rows(self):
        view = build_consistency_view({
            "status": "warning",
            "items": [{
                "catalog_item_id": "CAT1",
                "nombre": "Cable THW",
                "categoria": "Cable",
                "status": "warning",
                "issues": ["low_margin"],
                "ldm_numbers": ["LDM-01"],
                "qty_delta": 2,
                "issue_details": [{"issue": "low_margin", "label": "Margen bajo"}],
                "primary_action": {"text": "Revisar precio."},
            }],
            "ignored": {
                "commercial_quote": {"count": 1, "total": 50, "rows": []},
            },
            "suggested_actions": [{"status": "warning", "count": 1, "label": "Revisar", "text": "Validar margen."}],
            "bundle_consistency": {
                "status": "critical",
                "summary": {"items_total": 1},
                "technical_suggested_actions": [{"status": "critical", "count": 1, "label": "Faltante", "text": "Agregar."}],
                "rows": [{
                    "catalog_item_id": "MAT1",
                    "nombre": "Conduit",
                    "unidad": "ml",
                    "status": "critical",
                    "issue": "missing_in_ldm",
                    "diff_qty": -10,
                    "sources_expected": [
                        {"bundle_name": "Contacto", "ldm_number": "ignored"},
                        {"bundle_name": "Contacto extra"},
                        {"bundle_name": "Contacto spare"},
                    ],
                }],
                "bundle_rows": [{
                    "bundle_catalog_item_id": "CAT1",
                    "component_catalog_item_id": "MAT1",
                    "component_qty": 3,
                    "expected_qty": 10,
                }],
                "bundle_quote_items": [{
                    "catalog_item_id": "CAT1",
                    "description": "Salida contacto",
                    "qty": 1,
                }],
                "invalid_components": [
                    {"reason": "bundle_without_active_version"},
                    {"reason": "missing_catalog_item"},
                ],
            },
        })

        self.assertEqual(view["tab_severity"], "critical")
        self.assertEqual(view["ignored_quote"]["count"], 1)
        self.assertEqual(view["commercial_rows"][0]["color"], "warning")
        self.assertEqual(view["commercial_rows"][0]["issue_details"][0]["color"], "warning")
        self.assertEqual(view["commercial_rows"][0]["primary_action_text"], "Revisar precio.")
        self.assertEqual(view["suggested_actions"][0]["color"], "warning")

        tech_row = view["technical"]["rows"][0]
        self.assertEqual(tech_row["issue_label"], "Faltante en LDM")
        self.assertEqual(tech_row["sources_expected_more_count"], 1)
        self.assertIn("Contacto", tech_row["search_text"])
        self.assertEqual(view["technical"]["bundle_quote_items"][0]["components"][0]["action"], "Agregar material en la LDM del proyecto.")
        self.assertEqual(view["technical"]["technical_suggested_actions"][0]["color"], "danger")
        self.assertEqual(len(view["technical"]["other_invalid_components"]), 1)


if __name__ == "__main__":
    unittest.main()
