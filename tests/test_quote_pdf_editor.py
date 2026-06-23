import unittest
from unittest.mock import patch


PROJECT = {
    "id": "PROJ1",
    "clave": "OM001",
    "name": "Proyecto Editor",
    "client": "Cliente Test",
    "version": "V1",
    "folder_num": "001",
}

QUOTE = {
    "id": "Q1",
    "project_id": "PROJ1",
    "quote_number": "COT-OM001-G01-20260622",
    "quote_type": "General",
    "version": "V1",
    "client": "Cliente Test",
    "project_name": "Proyecto Editor",
    "date": "2026-06-22",
    "currency": "MXN",
    "tax_rate": 16.0,
    "items": [
        {
            "catalog_item_id": "CAT1",
            "description": "Salida Eléctrica para Luminaria",
            "unit": "pza",
            "qty": 10.0,
            "price": 900.0,
            "total": 9000.0,
            "catalog_description": "Omniious | Incluye Mano de Obra",
            "section": "",
        }
    ],
    "subtotal": 9000.0,
    "tax": 1440.0,
    "total": 10440.0,
    "notes": "",
    "specs": {},
    "created_at": "2026-06-22",
    "approval_status": "active",
}

CATALOG = [
    {
        "id": "CAT1",
        "nombre": "Salida Eléctrica para Luminaria",
        "descripcion": "Omniious | Incluye Mano de Obra",
        "unidad": "pza",
        "precio": 900.0,
        "categoria": "Instalacion",
    }
]


def _fake_load(key):
    return {"projects": [PROJECT], "quotes": [QUOTE], "catalogo": CATALOG}.get(key, [])


class QuotePdfEditorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        app.config["TESTING"] = True
        app.config["LOGIN_DISABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()

    def test_get_renders_editor(self):
        with patch("tracker.routes.quotes.load", side_effect=_fake_load), \
             patch("tracker.company_config.get_company", return_value={"name": "Test Co"}):
            resp = self.client.get("/projects/PROJ1/quote/Q1/pdf-editor")
        self.assertEqual(resp.status_code, 200)
        body = resp.data.decode("utf-8")
        self.assertIn("Editor PDF", body)
        self.assertIn("COT-OM001-G01-20260622", body)
        self.assertIn("Salida El", body)
        self.assertIn("Portada", body)
        self.assertIn("Alcance", body)
        self.assertIn("Condiciones", body)
        self.assertIn("Notas", body)

    def test_get_shows_pdf_preview_elements(self):
        with patch("tracker.routes.quotes.load", side_effect=_fake_load), \
             patch("tracker.company_config.get_company", return_value={"name": "Test Co"}):
            resp = self.client.get("/projects/PROJ1/quote/Q1/pdf-editor")
        body = resp.data.decode("utf-8")
        self.assertIn("prevBasisNote", body)
        self.assertIn("prevAlcanceBody", body)
        self.assertIn("prevTermsBody", body)
        self.assertIn("prevNotesSection", body)
        self.assertIn("PROPUESTA ECONÓMICA", body)

    def test_post_saves_specs_and_notes(self):
        saved = []

        def _fake_save(key, data):
            if key == "quotes":
                saved.append(data)

        form = {
            "notes": "Nota de prueba",
            "alcance_custom": "Párrafo personalizado de alcance.",
            "condiciones_pago": "50% anticipo.",
            "exclusiones": "Obra civil.",
            "validez": "30 días.",
            "forma_entrega": "En sitio.",
            "contacto": "ricardo@test.com",
            "project_basis_note": "IE-OM001-V2",
        }
        with patch("tracker.routes.quotes.load", side_effect=_fake_load), \
             patch("tracker.routes.quotes.save", side_effect=_fake_save), \
             patch("tracker.company_config.get_company", return_value={"name": "Test Co"}):
            resp = self.client.post(
                "/projects/PROJ1/quote/Q1/pdf-editor",
                data=form,
            )

        self.assertEqual(resp.status_code, 302)
        self.assertIn("pdf-editor", resp.headers["Location"])
        self.assertEqual(len(saved), 1)
        q = next(item for item in saved[0] if item["id"] == "Q1")
        self.assertEqual(q["notes"], "Nota de prueba")
        self.assertEqual(q["specs"]["alcance_custom"], "Párrafo personalizado de alcance.")
        self.assertEqual(q["specs"]["condiciones_pago"], "50% anticipo.")
        self.assertEqual(q["specs"]["basis_note_override"], "IE-OM001-V2")

    def test_post_extraordinaria_saves_project_basis_note(self):
        quote_ext = dict(QUOTE, id="Q2", quote_type="Extraordinaria",
                         quote_number="COT-OM001-E01-20260622")
        saved = []

        def _fake_load_ext(key):
            return {"projects": [PROJECT], "quotes": [quote_ext], "catalogo": CATALOG}.get(key, [])

        def _fake_save(key, data):
            if key == "quotes":
                saved.append(data)

        with patch("tracker.routes.quotes.load", side_effect=_fake_load_ext), \
             patch("tracker.routes.quotes.save", side_effect=_fake_save), \
             patch("tracker.company_config.get_company", return_value={"name": "Test Co"}):
            resp = self.client.post(
                "/projects/PROJ1/quote/Q2/pdf-editor",
                data={"project_basis_note": "Orden de cambio #5"},
            )

        self.assertEqual(resp.status_code, 302)
        q = next(item for item in saved[0] if item["id"] == "Q2")
        self.assertEqual(q["project_basis_note"], "Orden de cambio #5")

    def test_get_unknown_quote_redirects(self):
        with patch("tracker.routes.quotes.load", side_effect=_fake_load):
            resp = self.client.get("/projects/PROJ1/quote/NOPE/pdf-editor")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/", resp.headers["Location"])


if __name__ == "__main__":
    unittest.main()
