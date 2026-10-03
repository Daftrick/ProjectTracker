"""Tipo de cotización 'Proyecto Ejecutivo': sin cantidad ni unidad en los
artículos — cada renglón se cotiza a precio fijo tomado del catálogo
(qty=1 implícito). Cubre el flujo completo: alta, numeración y vista.
"""

import unittest

from tracker import create_app
from tracker.storage import load, save

PROJECT = {
    "id": "PEJTEST001",
    "name": "Test Proyecto Ejecutivo",
    "clave": "PEJ",
    "client": "Cliente Ejecutivo",
    "folder_num": "103",
    "alcances": ["cotizacion"],
    "notes": "",
    "closed_at": None,
    "in_obra": False,
    "created_at": "2026-01-01",
    "updated_at": "2026-01-01",
}


class ProyectoEjecutivoQuoteRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self._saved_projects = load("projects")
        self._saved_quotes = load("quotes")
        save("projects", [p for p in self._saved_projects if p["id"] != PROJECT["id"]] + [dict(PROJECT)])

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)

    def _quote_form(self, **overrides):
        data = {
            "quote_type": "Proyecto Ejecutivo",
            "date": "2026-10-03",
            "currency": "MXN",
            "tax_enabled": "on",
            "discount_pct": "0",
            "item_desc[]": "Diseño ejecutivo de instalaciones",
            "item_unit[]": "",
            "item_qty[]": "1",
            "item_precio_costo[]": "75000",
            "item_catalog_id[]": "",
            "item_desc2[]": "",
        }
        data.update(overrides)
        return data

    def test_new_quote_form_offers_proyecto_ejecutivo_option(self):
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/new")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('value="Proyecto Ejecutivo"', text)

    def test_creates_quote_with_j_sequence_and_qty_one(self):
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/new",
            data=self._quote_form(),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        quotes = [q for q in load("quotes") if q["project_id"] == PROJECT["id"]]
        self.assertEqual(len(quotes), 1)
        quote = quotes[0]
        self.assertEqual(quote["quote_type"], "Proyecto Ejecutivo")
        self.assertIn("-J01-", quote["quote_number"])
        self.assertEqual(quote["items"][0]["qty"], 1)
        self.assertEqual(quote["items"][0]["precio_costo"], 75000)
        self._saved_quotes = [q for q in load("quotes") if q["id"] != quote["id"]]

    def test_view_page_hides_unidad_and_cantidad_columns(self):
        self.client.post(
            f"/projects/{PROJECT['id']}/quote/new",
            data=self._quote_form(),
            follow_redirects=True,
        )
        quotes = [q for q in load("quotes") if q["project_id"] == PROJECT["id"]]
        quote_id = quotes[0]["id"]

        response = self.client.get(f"/projects/{PROJECT['id']}/quote/{quote_id}/view")
        text = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(">Unidad<", text)
        self.assertNotIn(">Cantidad<", text)
        self.assertNotIn("Precio unit.", text)
        self.assertIn(">Importe<", text)
        self.assertIn("Diseño ejecutivo de instalaciones", text)
        self._saved_quotes = [q for q in load("quotes") if q["id"] != quote_id]

    def test_second_quote_increments_j_sequence(self):
        self.client.post(
            f"/projects/{PROJECT['id']}/quote/new", data=self._quote_form(), follow_redirects=True
        )
        self.client.post(
            f"/projects/{PROJECT['id']}/quote/new", data=self._quote_form(), follow_redirects=True
        )
        quotes = [q for q in load("quotes") if q["project_id"] == PROJECT["id"]]
        self.assertEqual(len(quotes), 2)
        numbers = sorted(q["quote_number"] for q in quotes)
        self.assertIn("-J01-", numbers[0])
        self.assertIn("-J02-", numbers[1])
        self._saved_quotes = [q for q in load("quotes") if q["project_id"] != PROJECT["id"]]


if __name__ == "__main__":
    unittest.main()
