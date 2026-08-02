"""item_desc[] (columna "Nombre / Descripción" de cada partida) es un
<textarea> auto-expandible en el editor de cotización, para poder revisar
conceptos largos completos en varios renglones antes de terminar de editar
(antes era un <input> de una sola línea que recortaba/hacía scroll horizontal
del texto)."""

from pathlib import Path
import unittest

from tracker import create_app
from tracker.storage import load, save

PROJECT = {
    "id": "TXT001TEST",
    "name": "Test Textarea Proyecto",
    "clave": "TXT",
    "client": "Cliente Test",
    "folder_num": "106",
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

LONG_DESC = (
    "Proyecto arquitectónico, se realizará un proyecto para una vivienda "
    "unifamiliar de dos niveles, incluyendo planos estructurales."
)

QUOTE = {
    "id": "TXTQ001TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "TXT-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 0,
    "approval_status": "draft",
    "items": [{"description": LONG_DESC, "qty": 1, "price": 100, "total": 100}],
    "created_at": "2026-01-01",
}


class QuoteDescTemplateSourceTest(unittest.TestCase):
    def test_form_uses_textarea_for_item_desc_not_input(self):
        template = Path("templates/quote_project_form.html").read_text(encoding="utf-8")
        self.assertIn('<textarea name="item_desc[]"', template)
        # Guarda contra una regresión a <input> de una sola línea.
        self.assertNotIn('<input name="item_desc[]"', template)

    def test_form_has_autogrow_wiring(self):
        template = Path("templates/quote_project_form.html").read_text(encoding="utf-8")
        self.assertIn("_acAutoGrow", template)


class QuoteDescTextareaRouteTest(unittest.TestCase):
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

    def test_edit_form_renders_textarea_with_content(self):
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/edit")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('<textarea name="item_desc[]"', text)
        self.assertIn("Proyecto arquitect", text)

    def test_new_quote_form_renders_empty_textarea(self):
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/new")
        self.assertEqual(response.status_code, 200)
        self.assertIn('<textarea name="item_desc[]"', response.get_data(as_text=True))

    def test_description_with_special_chars_is_escaped_as_text_content(self):
        risky = 'Concepto con <script>alert(1)</script> & "comillas"'
        quotes = load("quotes")
        for q in quotes:
            if q["id"] == QUOTE["id"]:
                q["items"][0]["description"] = risky
        save("quotes", quotes)
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/edit")
        text = response.get_data(as_text=True)
        self.assertNotIn("<script>alert(1)</script>", text)
        self.assertIn("&lt;script&gt;", text)

    def test_multiline_description_round_trips_through_save(self):
        multiline = "Línea uno\nLínea dos\nLínea tres con detalle adicional"
        form = {
            "quote_type": "Proyecto",
            "date": "2026-02-01",
            "currency": "MXN",
            "tax_enabled": "on",
            "discount_pct": "0",
            "item_desc[]": multiline,
            "item_unit[]": "pza",
            "item_qty[]": "1",
            "item_precio_costo[]": "500",
            "item_catalog_id[]": "",
            "item_desc2[]": "",
        }
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/edit",
            data=form,
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        updated = next(q for q in load("quotes") if q["id"] == QUOTE["id"])
        self.assertEqual(updated["items"][0]["description"], multiline)

    def test_quote_view_page_preserves_line_breaks_visually(self):
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view")
        self.assertEqual(response.status_code, 200)
        self.assertIn("white-space:pre-line", response.get_data(as_text=True))


if __name__ == "__main__":
    unittest.main()
