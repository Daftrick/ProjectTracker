"""Botón "Pagos" en la fila de cada cotización (lista de cotizaciones,
project_detail.html) que lleva directo a la tarjeta de pagos de esa
cotización específica en quote_project_detail.html (vista de una sola
cotización, ya existente vía la ruta quotes_bp.view_quote). Antes sólo
existía la pestaña general de Pagos del proyecto (mezcla pagos de todas
las cotizaciones); esto agrega el acceso directo por cotización sin crear
una página nueva, reutilizando la tarjeta de pagos ya presente en esa vista.
"""

from pathlib import Path
import unittest

from tracker import create_app
from tracker.storage import load, save

PROJECT = {
    "id": "PAYLNK01TEST",
    "name": "Test Boton Pagos Proyecto",
    "clave": "PLK",
    "client": "Cliente Test",
    "folder_num": "107",
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
    "id": "PAYLNKQ01TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "PLK-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 0,
    "approval_status": "active",
    "items": [{"description": "Concepto de prueba", "qty": 1, "price": 1000, "total": 1000}],
    "created_at": "2026-01-01",
}


class QuotePaymentsLinkTemplateSourceTest(unittest.TestCase):
    def test_project_detail_has_payments_button_linking_to_view_quote_anchor(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("Pagos de esta cotización", template)
        self.assertIn(
            "url_for('quotes_bp.view_quote', project_id=project.id, quote_id=q.id) }}#pagos-cotizacion",
            template,
        )

    def test_quote_project_detail_has_payments_card_anchor_id(self):
        template = Path("templates/quote_project_detail.html").read_text(encoding="utf-8")
        self.assertIn('id="pagos-cotizacion"', template)
        # El id debe estar en la misma tarjeta que el encabezado "Pagos".
        idx = template.index('id="pagos-cotizacion"')
        nearby = template[idx: idx + 200]
        self.assertIn("Pagos", nearby)
        # scroll-margin-top para que la topbar fija no tape la tarjeta al
        # llegar por el anchor.
        self.assertIn("#pagos-cotizacion{ scroll-margin-top", template)


class QuotePaymentsLinkRouteTest(unittest.TestCase):
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

    def test_project_detail_page_renders_payments_button_for_quote_row(self):
        response = self.client.get(f"/projects/{PROJECT['id']}")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        expected_href = (
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view#pagos-cotizacion"
        )
        self.assertIn(expected_href, text)
        self.assertIn("Pagos de esta cotización", text)

    def test_view_quote_page_has_payments_anchor(self):
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view")
        self.assertEqual(response.status_code, 200)
        self.assertIn('id="pagos-cotizacion"', response.get_data(as_text=True))

    def test_payments_button_visible_even_for_closed_project(self):
        projects = load("projects")
        for p in projects:
            if p["id"] == PROJECT["id"]:
                p["closed_at"] = "2026-06-01"
        save("projects", projects)
        response = self.client.get(f"/projects/{PROJECT['id']}")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        expected_href = (
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view#pagos-cotizacion"
        )
        self.assertIn(expected_href, text)


if __name__ == "__main__":
    unittest.main()
