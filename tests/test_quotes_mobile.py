"""Integration tests for the mobile quote blueprint (Fase 10)."""

import io
import unittest
from unittest.mock import patch

PROJECT = {
    "id": "PROJ-MOB",
    "name": "Oficina Norte",
    "client": "Cliente SA",
    "clave": "OFN",
    "version": "V1",
    "folder_num": "001",
    "closed_at": None,
}
ITEM_A = {
    "id": "ITEM-A",
    "nombre": "Silla ergonómica",
    "descripcion": "Silla de oficina",
    "unidad": "pza",
    "precio": 1500.0,
    "disciplina": "Mobiliario",
}
ITEM_B = {
    "id": "ITEM-B",
    "nombre": "Mesa de trabajo",
    "descripcion": "Mesa 120x60",
    "unidad": "pza",
    "precio": 3000.0,
    "disciplina": "Mobiliario",
}
CATALOG = [ITEM_A, ITEM_B]
CATALOG_BY_ID = {i["id"]: i for i in CATALOG}

DRAFT_QUOTE = {
    "id": "DRAFT-1",
    "project_id": "PROJ-MOB",
    "status": "draft",
    "quote_type": "General",
    "quote_number": "",
    "version": "V1",
    "client": "Cliente SA",
    "project_name": "Oficina Norte",
    "date": "2026-06-18",
    "valid_until": "",
    "currency": "MXN",
    "tax_rate": 16.0,
    "items": [
        {
            "catalog_item_id": "ITEM-A",
            "description": "Silla ergonómica",
            "unit": "pza",
            "qty": "2",
            "price": "1500.0",
            "total": 3000.0,
            "section": "",
            "catalog_description": "Silla de oficina",
        }
    ],
    "subtotal": 3000.0,
    "tax": 480.0,
    "total": 3480.0,
    "notes": "",
    "project_basis_note": "",
    "created_at": "2026-06-18",
}


class MobileRouteTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app
        app.config["TESTING"] = True
        app.config["LOGIN_DISABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()


# ---------------------------------------------------------------------------
# Paso 1 — project selection
# ---------------------------------------------------------------------------

class MobileProjectsTest(MobileRouteTestBase):
    def _fake_load(self, key):
        if key == "projects":
            return [PROJECT]
        if key == "quotes":
            return []
        return []

    def test_projects_page_200(self):
        with patch("tracker.routes.quotes_mobile.load", side_effect=self._fake_load):
            resp = self.client.get("/cotizar/mobile/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Oficina Norte", resp.data)

    def test_draft_badge_shown_when_draft_exists(self):
        def fake_load_with_draft(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return [DRAFT_QUOTE]
            return []

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load_with_draft):
            resp = self.client.get("/cotizar/mobile/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"1 ", resp.data)

    def test_closed_projects_not_shown(self):
        closed = dict(PROJECT, closed_at="2026-01-01")
        with patch("tracker.routes.quotes_mobile.load", side_effect=lambda k: [closed] if k == "projects" else []):
            resp = self.client.get("/cotizar/mobile/")
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn(b"Oficina Norte", resp.data)


# ---------------------------------------------------------------------------
# Paso 2 — items browse
# ---------------------------------------------------------------------------

class MobileItemsTest(MobileRouteTestBase):
    def _fake_load(self, key):
        if key == "projects":
            return [PROJECT]
        if key == "quotes":
            return []
        if key == "catalogo":
            return CATALOG
        return []

    def test_items_page_200_no_draft(self):
        with patch("tracker.routes.quotes_mobile.load", side_effect=self._fake_load):
            resp = self.client.get("/cotizar/mobile/PROJ-MOB/items")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Silla", resp.data)

    def test_unknown_project_redirects(self):
        with patch("tracker.routes.quotes_mobile.load", side_effect=lambda k: [] if k == "projects" else []):
            resp = self.client.get("/cotizar/mobile/BADID/items")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/cotizar/mobile/", resp.location)

    def test_draft_banner_shown_when_draft_exists(self):
        def fake_load_with_draft(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return [DRAFT_QUOTE]
            if key == "catalogo":
                return CATALOG
            return []

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load_with_draft):
            resp = self.client.get("/cotizar/mobile/PROJ-MOB/items")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"borrador", resp.data)

    def test_nueva_param_discards_draft_and_redirects(self):
        saved = {}
        def fake_load(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return [dict(DRAFT_QUOTE)]
            if key == "catalogo":
                return CATALOG
            return []

        def fake_save(key, data):
            saved[key] = data

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load), \
             patch("tracker.routes.quotes_mobile.save", side_effect=fake_save):
            resp = self.client.get("/cotizar/mobile/PROJ-MOB/items?nueva=1")

        self.assertEqual(resp.status_code, 302)
        self.assertNotIn(
            DRAFT_QUOTE["id"],
            [q.get("id") for q in saved.get("quotes", [])],
        )

    def test_discipline_filter_shows_only_matching_items(self):
        catalog_mixed = [
            dict(ITEM_A, disciplina="Mobiliario"),
            dict(ITEM_B, disciplina="Instalaciones"),
        ]

        def fake_load(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return []
            if key == "catalogo":
                return catalog_mixed
            return []

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load):
            resp = self.client.get("/cotizar/mobile/PROJ-MOB/items?disciplina=Mobiliario")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Silla", resp.data)
        self.assertNotIn(b"Mesa", resp.data)


# ---------------------------------------------------------------------------
# POST add item
# ---------------------------------------------------------------------------

class MobileAddItemTest(MobileRouteTestBase):
    def test_add_item_creates_draft_and_redirects(self):
        saved = {}

        def fake_load(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return []
            return []

        def fake_save(key, data):
            saved[key] = data

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load), \
             patch("tracker.routes.quotes_mobile.save", side_effect=fake_save), \
             patch("tracker.routes.quotes_mobile.catalog_maps", return_value=(CATALOG_BY_ID, {})):
            resp = self.client.post(
                "/cotizar/mobile/PROJ-MOB/items",
                data={"item_id": "ITEM-A", "qty": "2"},
            )

        self.assertEqual(resp.status_code, 302)
        quotes = saved.get("quotes", [])
        self.assertEqual(len(quotes), 1)
        draft = quotes[0]
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["items"][0]["catalog_item_id"], "ITEM-A")
        self.assertEqual(draft["items"][0]["qty"], "2")

    def test_add_item_unknown_project_redirects_to_projects(self):
        with patch("tracker.routes.quotes_mobile.load", side_effect=lambda k: []):
            resp = self.client.post(
                "/cotizar/mobile/BADID/items",
                data={"item_id": "ITEM-A", "qty": "1"},
            )
        self.assertEqual(resp.status_code, 302)
        self.assertIn("/cotizar/mobile/", resp.location)

    def test_add_item_empty_item_id_no_save(self):
        saved = {}

        def fake_load(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return []
            return []

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load), \
             patch("tracker.routes.quotes_mobile.save", side_effect=lambda k, d: saved.update({k: d})), \
             patch("tracker.routes.quotes_mobile.catalog_maps", return_value=(CATALOG_BY_ID, {})):
            resp = self.client.post(
                "/cotizar/mobile/PROJ-MOB/items",
                data={"item_id": "", "qty": "1"},
            )

        self.assertEqual(resp.status_code, 302)
        self.assertNotIn("quotes", saved)


# ---------------------------------------------------------------------------
# Remove item
# ---------------------------------------------------------------------------

class MobileRemoveItemTest(MobileRouteTestBase):
    def test_remove_item_updates_draft_and_redirects_to_review(self):
        saved = {}

        def fake_load(key):
            if key == "quotes":
                return [dict(DRAFT_QUOTE, items=list(DRAFT_QUOTE["items"]))]
            return []

        def fake_save(key, data):
            saved[key] = data

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load), \
             patch("tracker.routes.quotes_mobile.save", side_effect=fake_save):
            resp = self.client.post(
                "/cotizar/mobile/PROJ-MOB/remove_item",
                data={"item_id": "ITEM-A"},
            )

        self.assertEqual(resp.status_code, 302)
        self.assertIn("review", resp.location)
        quotes = saved.get("quotes", [])
        if quotes:
            remaining = [i for i in quotes[0]["items"] if i["catalog_item_id"] == "ITEM-A"]
            self.assertEqual(remaining, [])


# ---------------------------------------------------------------------------
# Paso 3 — review
# ---------------------------------------------------------------------------

class MobileReviewTest(MobileRouteTestBase):
    def _fake_load(self, key):
        if key == "projects":
            return [PROJECT]
        if key == "quotes":
            return [DRAFT_QUOTE]
        return []

    def test_review_page_200_with_draft(self):
        with patch("tracker.routes.quotes_mobile.load", side_effect=self._fake_load):
            resp = self.client.get("/cotizar/mobile/PROJ-MOB/review")
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"Silla", resp.data)
        self.assertIn(b"3,480", resp.data)

    def test_review_no_draft_redirects_to_items(self):
        def fake_load(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return []
            return []

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load):
            resp = self.client.get("/cotizar/mobile/PROJ-MOB/review")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("items", resp.location)

    def test_review_unknown_project_redirects(self):
        with patch("tracker.routes.quotes_mobile.load", side_effect=lambda k: []):
            resp = self.client.get("/cotizar/mobile/BADID/review")
        self.assertEqual(resp.status_code, 302)


# ---------------------------------------------------------------------------
# Paso 4 — generate PDF
# ---------------------------------------------------------------------------

class MobileGeneratePdfTest(MobileRouteTestBase):
    def test_generate_pdf_returns_pdf_bytes(self):
        def fake_load(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return [dict(DRAFT_QUOTE)]
            return []

        fake_hydrated = dict(DRAFT_QUOTE, quote_number="COT-OFN-G01-260618")

        def fake_build_pdf(project, quote, path):
            with open(path, "wb") as f:
                f.write(b"%PDF-1.4 fake")

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load), \
             patch("tracker.routes.quotes_mobile.save"), \
             patch("tracker.routes.quotes_mobile.catalog_maps", return_value=(CATALOG_BY_ID, {})), \
             patch("tracker.routes.quotes_mobile.hydrate_quote", return_value=fake_hydrated), \
             patch("tracker.routes.quotes_mobile.build_quote_pdf", side_effect=fake_build_pdf):
            resp = self.client.post("/cotizar/mobile/PROJ-MOB/generate_pdf")

        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content_type, "application/pdf")
        self.assertIn(b"%PDF", resp.data)

    def test_generate_pdf_no_draft_redirects(self):
        def fake_load(key):
            if key == "projects":
                return [PROJECT]
            if key == "quotes":
                return []
            return []

        with patch("tracker.routes.quotes_mobile.load", side_effect=fake_load):
            resp = self.client.post("/cotizar/mobile/PROJ-MOB/generate_pdf")
        self.assertEqual(resp.status_code, 302)
        self.assertIn("items", resp.location)

    def test_generate_pdf_unknown_project_redirects(self):
        with patch("tracker.routes.quotes_mobile.load", side_effect=lambda k: []):
            resp = self.client.post("/cotizar/mobile/BADID/generate_pdf")
        self.assertEqual(resp.status_code, 302)


if __name__ == "__main__":
    unittest.main()
