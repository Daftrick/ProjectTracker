"""El cliente (y el nombre de proyecto) se guardan como snapshot dentro de la
cotización al crearla. Si el cliente del proyecto se edita después, todas las
vistas y exportaciones deben reflejar el valor ACTUAL del proyecto, no el
snapshot viejo (VERSIONES.md #11 — "Error en la actualización de cliente en
PDF, si se modifica no se actualiza").
"""

import unittest

from tracker import create_app
from tracker.storage import load, save

PROJECT = {
    "id": "CLI001TEST",
    "name": "Test Cliente Proyecto",
    "clave": "CLI",
    "client": "Cliente Nuevo S.A.",
    "folder_num": "100",
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

# Snapshot histórico de cliente/proyecto, capturado cuando el proyecto todavía
# se llamaba distinto y tenía otro cliente — ya obsoleto.
QUOTE = {
    "id": "CLIQ001TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "CLI-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 0,
    "approval_status": "active",
    "client": "Cliente Viejo Inc.",
    "project_name": "Nombre Viejo del Proyecto",
    "items": [{"description": "Concepto de prueba", "qty": 1, "price": 1000, "total": 1000}],
    "created_at": "2026-01-01",
}


class QuoteWorkbookClientSyncTest(unittest.TestCase):
    def test_workbook_uses_live_project_client_and_name(self):
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font

        from tracker.routes.quotes import _build_quote_workbook

        wb, _filename = _build_quote_workbook(dict(PROJECT), dict(QUOTE), Workbook, Alignment, Font)
        ws = wb.active
        rows = {row[0].value: row[1].value for row in ws.iter_rows(min_row=1, max_row=5)}
        self.assertEqual(rows["Cliente:"], "Cliente Nuevo S.A.")
        self.assertEqual(rows["Proyecto:"], "Test Cliente Proyecto")
        self.assertNotEqual(rows["Cliente:"], "Cliente Viejo Inc.")
        self.assertNotEqual(rows["Proyecto:"], "Nombre Viejo del Proyecto")

    def test_workbook_falls_back_to_snapshot_when_project_missing_data(self):
        from openpyxl import Workbook
        from openpyxl.styles import Alignment, Font

        from tracker.routes.quotes import _build_quote_workbook

        bare_project = dict(PROJECT)
        bare_project["client"] = ""
        bare_project["name"] = ""
        wb, _filename = _build_quote_workbook(bare_project, dict(QUOTE), Workbook, Alignment, Font)
        ws = wb.active
        rows = {row[0].value: row[1].value for row in ws.iter_rows(min_row=1, max_row=5)}
        self.assertEqual(rows["Cliente:"], "Cliente Viejo Inc.")
        self.assertEqual(rows["Proyecto:"], "Nombre Viejo del Proyecto")


class QuoteClientSyncRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        self._saved_projects = load("projects")
        self._saved_quotes = load("quotes")
        save("projects", [p for p in self._saved_projects if p["id"] != PROJECT["id"]] + [dict(PROJECT)])
        save("quotes", [q for q in self._saved_quotes if q["id"] != QUOTE["id"]] + [dict(QUOTE)])

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)

    def test_quote_detail_page_shows_current_client(self):
        response = self.client.get(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Cliente Nuevo S.A.", text)
        self.assertNotIn("Cliente Viejo Inc.", text)

    def test_quote_resumen_page_shows_current_client(self):
        response = self.client.get(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/resumen",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Cliente Nuevo S.A.", text)
        self.assertNotIn("Cliente Viejo Inc.", text)


if __name__ == "__main__":
    unittest.main()
