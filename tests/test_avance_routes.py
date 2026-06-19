import unittest

from tracker import create_app
from tracker.storage import load, save

PROJECT = {
    "id": "AVZ001TEST",
    "name": "Test Avance Proyecto",
    "clave": "AVZ",
    "client": "Cliente Test",
    "folder_num": "097",
    "version": "V1",
    "fecha": "260101",
    "alcances": ["cotizacion"],
    "notes": "",
    "closed_at": None,
    "in_obra": False,
    "template_id": "residencial",
    "drive_url": "",
    "created_at": "2026-01-01",
    "updated_at": "2026-01-01",
}


class AvanceRoutesTest(unittest.TestCase):

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        projects = load("projects")
        self._saved_projects = [p for p in projects if p["id"] != PROJECT["id"]]
        projects_with_test = self._saved_projects + [dict(PROJECT)]
        save("projects", projects_with_test)

    def tearDown(self):
        save("projects", self._saved_projects)

    def _get_project(self):
        return next(p for p in load("projects") if p["id"] == PROJECT["id"])

    # ── stage_status ──────────────────────────────────────────────────────

    def test_update_stage_status_sets_stage(self):
        r = self.client.post(
            f"/projects/{PROJECT['id']}/stage-status",
            data={"stage": "Diseño", "status": "in_progress", "date": "2026-06-19"},
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        self.assertEqual(p["stage_status"]["Diseño"]["status"], "in_progress")
        self.assertEqual(p["stage_status"]["Diseño"]["date"], "2026-06-19")

    def test_update_stage_status_empty_date_stored_as_none(self):
        r = self.client.post(
            f"/projects/{PROJECT['id']}/stage-status",
            data={"stage": "Obra", "status": "done", "date": ""},
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        self.assertIsNone(p["stage_status"]["Obra"]["date"])

    def test_update_stage_status_ignores_empty_stage(self):
        r = self.client.post(
            f"/projects/{PROJECT['id']}/stage-status",
            data={"stage": "", "status": "done", "date": "2026-06-19"},
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        self.assertFalse(p.get("stage_status"))

    def test_update_stage_status_unknown_project_redirects(self):
        r = self.client.post(
            "/projects/NONEXISTENT/stage-status",
            data={"stage": "Obra", "status": "done"},
        )
        self.assertEqual(r.status_code, 302)

    # ── docs_checklist ────────────────────────────────────────────────────

    def test_add_doc_checklist_appends_item(self):
        r = self.client.post(
            f"/projects/{PROJECT['id']}/docs-checklist/add",
            data={"name": "Plano eléctrico"},
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        self.assertEqual(len(p["docs_checklist"]), 1)
        self.assertEqual(p["docs_checklist"][0]["name"], "Plano eléctrico")
        self.assertFalse(p["docs_checklist"][0]["done"])
        self.assertIn("id", p["docs_checklist"][0])

    def test_add_doc_checklist_ignores_empty_name(self):
        r = self.client.post(
            f"/projects/{PROJECT['id']}/docs-checklist/add",
            data={"name": "   "},
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        self.assertFalse(p.get("docs_checklist"))

    def test_toggle_doc_checklist_flips_done(self):
        self.client.post(
            f"/projects/{PROJECT['id']}/docs-checklist/add",
            data={"name": "Memoria técnica"},
        )
        p = self._get_project()
        item_id = p["docs_checklist"][0]["id"]
        self.assertFalse(p["docs_checklist"][0]["done"])

        self.client.post(
            f"/projects/{PROJECT['id']}/docs-checklist/toggle",
            data={"item_id": item_id},
        )
        self.assertTrue(self._get_project()["docs_checklist"][0]["done"])

        self.client.post(
            f"/projects/{PROJECT['id']}/docs-checklist/toggle",
            data={"item_id": item_id},
        )
        self.assertFalse(self._get_project()["docs_checklist"][0]["done"])

    def test_delete_doc_checklist_removes_item(self):
        self.client.post(
            f"/projects/{PROJECT['id']}/docs-checklist/add",
            data={"name": "Doc a eliminar"},
        )
        p = self._get_project()
        item_id = p["docs_checklist"][0]["id"]

        r = self.client.post(f"/projects/{PROJECT['id']}/docs-checklist/delete/{item_id}")
        self.assertEqual(r.status_code, 302)
        self.assertEqual(len(self._get_project().get("docs_checklist") or []), 0)

    def test_add_multiple_docs_independent(self):
        self.client.post(f"/projects/{PROJECT['id']}/docs-checklist/add", data={"name": "Doc A"})
        self.client.post(f"/projects/{PROJECT['id']}/docs-checklist/add", data={"name": "Doc B"})
        p = self._get_project()
        self.assertEqual(len(p["docs_checklist"]), 2)
        ids = {item["id"] for item in p["docs_checklist"]}
        self.assertEqual(len(ids), 2)

    # ── stage_budget ──────────────────────────────────────────────────────

    def test_update_stage_budget_persists_values(self):
        # residencial template stages: Diseño, Permisos, Obra, Entrega
        r = self.client.post(
            f"/projects/{PROJECT['id']}/stage-budget",
            data={
                "planned_Diseño": "100000",
                "actual_Diseño": "90000",
                "planned_Permisos": "0",
                "actual_Permisos": "0",
                "planned_Obra": "0",
                "actual_Obra": "0",
                "planned_Entrega": "0",
                "actual_Entrega": "0",
            },
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        self.assertIn("stage_budget", p)
        self.assertAlmostEqual(p["stage_budget"]["Diseño"]["planned"], 100000.0)
        self.assertAlmostEqual(p["stage_budget"]["Diseño"]["actual"], 90000.0)

    def test_update_stage_budget_handles_missing_values_as_zero(self):
        r = self.client.post(
            f"/projects/{PROJECT['id']}/stage-budget",
            data={},
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        # template exists → budget created with 0s
        self.assertIn("stage_budget", p)
        for stage in ["Diseño", "Permisos", "Obra", "Entrega"]:
            self.assertEqual(p["stage_budget"][stage]["planned"], 0.0)

    def test_update_stage_budget_skips_without_template(self):
        projects = load("projects")
        for p in projects:
            if p["id"] == PROJECT["id"]:
                p["template_id"] = ""
        save("projects", projects)

        r = self.client.post(
            f"/projects/{PROJECT['id']}/stage-budget",
            data={"planned_Diseño": "99999"},
        )
        self.assertEqual(r.status_code, 302)
        p = self._get_project()
        self.assertNotIn("stage_budget", p)

    def test_update_stage_budget_unknown_project_redirects(self):
        r = self.client.post("/projects/NONEXISTENT/stage-budget", data={})
        self.assertEqual(r.status_code, 302)

    # ── progress PDF ──────────────────────────────────────────────────────

    def test_progress_pdf_returns_pdf_content(self):
        r = self.client.get(f"/projects/{PROJECT['id']}/reporte.pdf")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.content_type, "application/pdf")
        self.assertGreater(len(r.data), 0)

    def test_progress_pdf_unknown_project_404(self):
        r = self.client.get("/projects/NONEXISTENT/reporte.pdf")
        self.assertEqual(r.status_code, 404)


if __name__ == "__main__":
    unittest.main()
