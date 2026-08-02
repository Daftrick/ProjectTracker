"""Selector libre de estado de cotización en la columna Estado.

Antes sólo existía approve_quote(): un toggle binario active↔obsolete que no
permitía volver a "borrador" ni elegir el estado directamente. Ahora
set_quote_status() permite ir a cualquiera de los 3 estados en cualquier
momento, expuesto como un <select> en la columna Estado de la lista de
cotizaciones (project_detail.html) y en la vista de cotización individual
(quote_project_detail.html).
"""

import unittest

from tracker import create_app
from tracker.catalog import (
    APPROVAL_ACTIVE,
    APPROVAL_DRAFT,
    APPROVAL_OBSOLETE,
    VALID_APPROVAL_STATUSES,
    set_quote_status,
)
from tracker.storage import load, save

PROJECT = {
    "id": "SEL001TEST",
    "name": "Test Selector Estado Proyecto",
    "clave": "SEL",
    "client": "Cliente Test",
    "folder_num": "104",
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

QUOTE = {
    "id": "SELQ001TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "SEL-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 0,
    "approval_status": "draft",
    "items": [{"description": "Concepto de prueba", "qty": 1, "price": 1000, "total": 1000}],
    "created_at": "2026-01-01",
}


class SetQuoteStatusModelTest(unittest.TestCase):
    def test_valid_statuses_constant(self):
        self.assertEqual(set(VALID_APPROVAL_STATUSES), {"draft", "active", "obsolete"})

    def test_draft_to_active(self):
        quotes = [{"id": "Q1", "approval_status": APPROVAL_DRAFT}]
        self.assertTrue(set_quote_status("Q1", quotes, APPROVAL_ACTIVE))
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_ACTIVE)

    def test_active_to_draft_directly(self):
        # Esto era imposible con el toggle binario anterior (approve_quote).
        quotes = [{"id": "Q1", "approval_status": APPROVAL_ACTIVE}]
        self.assertTrue(set_quote_status("Q1", quotes, APPROVAL_DRAFT))
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_DRAFT)

    def test_active_to_obsolete(self):
        quotes = [{"id": "Q1", "approval_status": APPROVAL_ACTIVE}]
        self.assertTrue(set_quote_status("Q1", quotes, APPROVAL_OBSOLETE))
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_OBSOLETE)

    def test_obsolete_to_draft_directly(self):
        quotes = [{"id": "Q1", "approval_status": APPROVAL_OBSOLETE}]
        self.assertTrue(set_quote_status("Q1", quotes, APPROVAL_DRAFT))
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_DRAFT)

    def test_same_status_is_a_noop(self):
        quotes = [{"id": "Q1", "approval_status": APPROVAL_ACTIVE}]
        self.assertFalse(set_quote_status("Q1", quotes, APPROVAL_ACTIVE))
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_ACTIVE)

    def test_invalid_status_rejected(self):
        quotes = [{"id": "Q1", "approval_status": APPROVAL_DRAFT}]
        self.assertFalse(set_quote_status("Q1", quotes, "algo-raro"))
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_DRAFT)

    def test_unknown_quote_id_returns_false(self):
        quotes = [{"id": "Q1", "approval_status": APPROVAL_DRAFT}]
        self.assertFalse(set_quote_status("no-existe", quotes, APPROVAL_ACTIVE))

    def test_does_not_affect_other_quotes(self):
        # Aprobación libre e independiente: activar una no debe tocar las demás,
        # a diferencia de la competencia entre bases del flujo antiguo.
        quotes = [
            {"id": "Q1", "quote_type": "Proyecto", "approval_status": APPROVAL_ACTIVE},
            {"id": "Q2", "quote_type": "Proyecto", "approval_status": APPROVAL_DRAFT},
        ]
        set_quote_status("Q2", quotes, APPROVAL_ACTIVE)
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(quotes[1]["approval_status"], APPROVAL_ACTIVE)


class SetQuoteStatusRouteTest(unittest.TestCase):
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

    def _status(self):
        return next(q for q in load("quotes") if q["id"] == QUOTE["id"])["approval_status"]

    def test_set_status_to_active(self):
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/status",
            data={"status": "active"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._status(), "active")

    def test_set_status_back_to_draft_from_active(self):
        self.client.post(f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/status", data={"status": "active"})
        self.assertEqual(self._status(), "active")
        self.client.post(f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/status", data={"status": "draft"})
        self.assertEqual(self._status(), "draft")

    def test_set_status_to_obsolete_directly_from_draft(self):
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/status",
            data={"status": "obsolete"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self._status(), "obsolete")

    def test_invalid_status_flashes_error_and_does_not_change(self):
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/status",
            data={"status": "no-es-un-estado"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Estado no válido", response.get_data(as_text=True))
        self.assertEqual(self._status(), "draft")

    def test_unknown_quote_flashes_not_found(self):
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/no-existe/status",
            data={"status": "active"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cotización no encontrada", response.get_data(as_text=True))

    def test_redirects_to_next_url_when_provided(self):
        custom_next = f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view"
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/status",
            data={"status": "active", "next": custom_next},
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(custom_next, response.headers["Location"])

    def test_project_detail_page_has_status_select_with_current_value(self):
        response = self.client.get(f"/projects/{PROJECT['id']}")
        text = response.get_data(as_text=True)
        self.assertIn("quote-status-form", text)
        self.assertIn(f"quote/{QUOTE['id']}/status", text)

    def test_quote_detail_page_has_status_select(self):
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view")
        text = response.get_data(as_text=True)
        self.assertIn("quote-status-form", text)

    def test_closed_project_shows_readonly_badge_not_select(self):
        projects = load("projects")
        for p in projects:
            if p["id"] == PROJECT["id"]:
                p["closed_at"] = "2026-06-01"
        save("projects", projects)
        response = self.client.get(f"/projects/{PROJECT['id']}")
        text = response.get_data(as_text=True)
        self.assertNotIn("quote-status-form", text)
        self.assertIn("Borrador", text)


if __name__ == "__main__":
    unittest.main()
