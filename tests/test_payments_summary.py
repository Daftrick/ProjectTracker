"""Acceso rápido "Pagos" en el panel lateral: vista global (quotes_bp.all_payments,
"/pagos") que lista todos los pagos de todos los proyectos/cotizaciones, análoga
a la vista "Cotizaciones" (all_quotes) ya existente, con enlace directo a la
tarjeta de pagos de cada cotización (#pagos-cotizacion, ver [[quote-payments-link]]).
"""

from pathlib import Path
import unittest

from tracker import create_app
from tracker.payments import add_payment
from tracker.storage import load, save

PROJECT = {
    "id": "PAYSUM01TEST",
    "name": "Test Panel Pagos Proyecto",
    "clave": "PSM",
    "client": "Cliente Test",
    "folder_num": "108",
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
    "id": "PAYSUMQ01TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "PSM-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 0,
    "approval_status": "active",
    "items": [{"description": "Concepto de prueba", "qty": 1, "price": 2000, "total": 2000}],
    "created_at": "2026-01-01",
}


class SidebarPaymentsLinkTemplateSourceTest(unittest.TestCase):
    def test_base_template_has_sidebar_payments_link(self):
        template = Path("templates/base.html").read_text(encoding="utf-8")
        self.assertIn("url_for('quotes_bp.all_payments')", template)
        self.assertIn('data-label="Pagos"', template)


class AllPaymentsRouteTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self._saved_projects = load("projects")
        self._saved_quotes = load("quotes")
        self._saved_payments = load("payments")
        save("projects", [p for p in self._saved_projects if p["id"] != PROJECT["id"]] + [dict(PROJECT)])
        save("quotes", [q for q in self._saved_quotes if q["id"] != QUOTE["id"]] + [dict(QUOTE)])
        save("payments", [p for p in self._saved_payments if p.get("project_id") != PROJECT["id"]])

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)
        save("payments", self._saved_payments)

    def test_all_payments_page_loads_and_lists_registered_payment(self):
        add_payment(PROJECT["id"], QUOTE["id"], "2026-02-01", 500, "Anticipo")
        response = self.client.get("/pagos")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Test Panel Pagos Proyecto", text)
        self.assertIn("PSM-COT-01", text)
        self.assertIn("Anticipo", text)
        self.assertIn("$500.00", text)

    def test_all_payments_page_links_to_quote_payments_card(self):
        add_payment(PROJECT["id"], QUOTE["id"], "2026-02-01", 500, "Anticipo")
        response = self.client.get("/pagos")
        text = response.get_data(as_text=True)
        expected_href = f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view#pagos-cotizacion"
        self.assertIn(expected_href, text)

    def test_all_payments_page_shows_empty_state_without_payments(self):
        response = self.client.get("/pagos")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Sin pagos aún", response.get_data(as_text=True))

    def test_all_payments_page_sums_total_pagado(self):
        add_payment(PROJECT["id"], QUOTE["id"], "2026-02-01", 500, "Anticipo")
        add_payment(PROJECT["id"], QUOTE["id"], "2026-02-15", 300, "Segundo pago")
        response = self.client.get("/pagos")
        text = response.get_data(as_text=True)
        self.assertIn("$800.00", text)

    def test_sidebar_renders_pagos_link_on_dashboard(self):
        response = self.client.get("/")
        text = response.get_data(as_text=True)
        self.assertIn('href="/pagos"', text)


if __name__ == "__main__":
    unittest.main()
