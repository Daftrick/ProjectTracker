import unittest

from tracker import create_app
from tracker.project_view import build_quote_row_views
from tracker.quote_status_labels import (
    DEFAULT_LABELS,
    get_quote_status_labels,
    quote_status_view,
    save_quote_status_labels,
)
from tracker.storage import load, save

PROJECT = {
    "id": "STA001TEST",
    "name": "Test Nomenclatura Proyecto",
    "clave": "STA",
    "client": "Cliente Test",
    "folder_num": "099",
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
    "id": "STAQ001TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "STA-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 0,
    "approval_status": "active",
    "items": [{"description": "Concepto de prueba", "qty": 1, "price": 1000, "total": 1000}],
    "created_at": "2026-01-01",
}


class QuoteStatusLabelsModelTest(unittest.TestCase):
    def setUp(self):
        self._saved = load("quote_status_labels")
        save("quote_status_labels", {})

    def tearDown(self):
        save("quote_status_labels", self._saved)

    def test_defaults_when_nothing_saved(self):
        self.assertEqual(get_quote_status_labels(), DEFAULT_LABELS)

    def test_save_and_get_roundtrip(self):
        save_quote_status_labels({"draft": "En espera", "active": "Vigente", "obsolete": "Cancelada"})
        labels = get_quote_status_labels()
        self.assertEqual(labels["draft"], "En espera")
        self.assertEqual(labels["active"], "Vigente")
        self.assertEqual(labels["obsolete"], "Cancelada")

    def test_blank_values_fall_back_to_defaults(self):
        save_quote_status_labels({"draft": "", "active": "  ", "obsolete": "Cancelada"})
        labels = get_quote_status_labels()
        self.assertEqual(labels["draft"], DEFAULT_LABELS["draft"])
        self.assertEqual(labels["active"], DEFAULT_LABELS["active"])
        self.assertEqual(labels["obsolete"], "Cancelada")

    def test_quote_status_view_unknown_status_defaults_to_draft(self):
        view = quote_status_view("weird-status")
        self.assertEqual(view["status"], "draft")
        self.assertEqual(view["label"], DEFAULT_LABELS["draft"])

    def test_quote_status_view_uses_saved_label(self):
        save_quote_status_labels({"active": "Vigente"})
        view = quote_status_view("active")
        self.assertEqual(view["label"], "Vigente")
        self.assertEqual(view["badge"], "success")
        self.assertEqual(view["icon"], "check-circle")


class QuoteRowNomenclatureUnificationTest(unittest.TestCase):
    """Antes: cotizaciones base decían 'Aprobada/Obsoleta' y extraordinarias
    decían 'Activa/Inactiva' para el mismo approval_status — inconsistente.
    Ahora ambas deben mostrar exactamente la misma etiqueta."""

    def setUp(self):
        self._saved = load("quote_status_labels")
        save("quote_status_labels", {})

    def tearDown(self):
        save("quote_status_labels", self._saved)

    def test_base_and_extra_quote_share_label_for_same_status(self):
        rows = build_quote_row_views([
            {"id": "Q1", "quote_type": "General", "approval_status": "active", "items": []},
            {"id": "Q2", "quote_type": "Extraordinaria", "approval_status": "active", "items": []},
        ])
        self.assertEqual(rows[0]["approval_label"], rows[1]["approval_label"])
        self.assertEqual(rows[0]["approval_label"], "Activa")

    def test_base_and_extra_quote_share_label_for_obsolete(self):
        rows = build_quote_row_views([
            {"id": "Q1", "quote_type": "General", "approval_status": "obsolete", "items": []},
            {"id": "Q2", "quote_type": "Extraordinaria", "approval_status": "obsolete", "items": []},
        ])
        self.assertEqual(rows[0]["approval_label"], rows[1]["approval_label"])
        self.assertEqual(rows[0]["approval_label"], "Obsoleta")

    def test_custom_label_reflected_in_row_views(self):
        save_quote_status_labels({"active": "Vigente"})
        rows = build_quote_row_views([
            {"id": "Q1", "quote_type": "General", "approval_status": "active", "items": []},
        ])
        self.assertEqual(rows[0]["approval_label"], "Vigente")


class QuoteStatusLabelsRouteTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        self._saved_projects = load("projects")
        self._saved_quotes = load("quotes")
        self._saved_labels = load("quote_status_labels")
        save("projects", [p for p in self._saved_projects if p["id"] != PROJECT["id"]] + [dict(PROJECT)])
        save("quotes", [q for q in self._saved_quotes if q["id"] != QUOTE["id"]] + [dict(QUOTE)])
        save("quote_status_labels", {})

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)
        save("quote_status_labels", self._saved_labels)

    def test_settings_page_loads_with_defaults(self):
        response = self.client.get("/configuracion/nomenclatura-cotizaciones")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('value="Borrador"', text)
        self.assertIn('value="Activa"', text)
        self.assertIn('value="Obsoleta"', text)

    def test_post_saves_custom_labels(self):
        response = self.client.post(
            "/configuracion/nomenclatura-cotizaciones",
            data={"draft": "Pendiente", "active": "Vigente", "obsolete": "Cancelada"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_quote_status_labels(), {
            "draft": "Pendiente", "active": "Vigente", "obsolete": "Cancelada",
        })

    def test_quote_detail_page_reflects_custom_active_label(self):
        save_quote_status_labels({"active": "Vigente"})
        response = self.client.get(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Vigente", text)
        self.assertNotIn("Aprobada", text)


if __name__ == "__main__":
    unittest.main()
