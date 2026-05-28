"""Pruebas de sincronizacion parcial LDM desde bundles."""

import unittest
from unittest.mock import patch

from tracker.ldm_sync import append_missing_bundle_items_to_ldm, missing_ldm_items_from_bundles


PROJECT = {"id": "P1", "clave": "OM001", "name": "Proyecto demo"}
CATALOG = {
    "COT-OUTLET": {"id": "COT-OUTLET", "nombre": "Salida contacto", "unidad": "pza"},
    "TUBO-ML": {"id": "TUBO-ML", "nombre": "Tubo por metro", "unidad": "ml"},
}
QUOTE = {
    "id": "Q1",
    "project_id": "P1",
    "quote_type": "General",
    "date": "2026-05-06",
    "items": [
        {"catalog_item_id": "COT-OUTLET", "description": "Salida contacto", "qty": 4, "price": 100, "total": 400},
    ],
    "subtotal": 400,
}
BUNDLES = [{
    "id": "B1",
    "catalog_item_id": "COT-OUTLET",
    "name": "Salida contacto",
    "active_version": 1,
    "versions": [{
        "version": 1,
        "status": "active",
        "components": [{"catalog_item_id": "TUBO-ML", "qty": 1.5}],
    }],
}]
LDM = {
    "id": "L1",
    "project_id": "P1",
    "ldm_number": "LDM-OM001-01",
    "items": [
        {"catalog_item_id": "TUBO-ML", "description": "Tubo por metro", "unit": "ml", "qty": 2},
    ],
    "subtotal_cot": 0,
}


class LdmSyncTest(unittest.TestCase):
    def test_builds_only_missing_bundle_materials_without_overwriting(self):
        additions = missing_ldm_items_from_bundles(QUOTE, [LDM], BUNDLES, CATALOG)

        self.assertEqual(len(additions), 1)
        self.assertEqual(additions[0]["catalog_item_id"], "TUBO-ML")
        self.assertEqual(additions[0]["qty"], 4)
        self.assertEqual(additions[0]["origen"], "bundle_sync")
        self.assertEqual(additions[0]["sync_expected_catalog_item_id"], "TUBO-ML")

    def test_appends_missing_items_to_copy(self):
        updated, additions = append_missing_bundle_items_to_ldm(LDM, QUOTE, [LDM], BUNDLES, CATALOG)

        self.assertEqual(len(additions), 1)
        self.assertEqual(len(updated["items"]), 2)
        self.assertEqual(len(LDM["items"]), 1)


class MaterialsSyncRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        cls.client = app.test_client()

    def test_route_appends_missing_bundle_materials_to_existing_ldm(self):
        saved = {}
        materiales = [dict(LDM, items=[dict(item) for item in LDM["items"]])]

        def fake_load(key):
            data = {
                "projects": [PROJECT],
                "materiales": materiales,
                "quotes": [QUOTE],
                "bundles": BUNDLES,
            }
            return data.get(key, [])

        def fake_save(key, value):
            saved[key] = value

        with patch("tracker.routes.materials.load", side_effect=fake_load), \
             patch("tracker.routes.materials.save", side_effect=fake_save), \
             patch("tracker.routes.materials.catalog_maps", return_value=(CATALOG, {})):
            response = self.client.post("/projects/P1/ldm/L1/sync-bundles")

        self.assertEqual(response.status_code, 302)
        self.assertIn("materiales", saved)
        self.assertEqual(len(saved["materiales"][0]["items"]), 2)
        self.assertEqual(saved["materiales"][0]["items"][1]["origen"], "bundle_sync")

    def test_new_ldm_can_prefill_bundle_suggestions(self):
        def fake_load(key):
            data = {
                "projects": [PROJECT],
                "materiales": [LDM],
                "quotes": [QUOTE],
                "bundles": BUNDLES,
                "proveedores": [],
            }
            return data.get(key, [])

        with patch("tracker.routes.materials.load", side_effect=fake_load), \
             patch("tracker.routes.materials.catalog_maps", return_value=(CATALOG, {})):
            response = self.client.get("/projects/P1/ldm/new?from_bundles=1")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Tubo por metro", response.data)
        self.assertIn(b"Sugerido desde bundles", response.data)
        self.assertIn(b'value="4.0"', response.data)

    def test_new_ldm_preserves_bundle_suggestion_origin_on_create(self):
        saved = {}
        materiales = []

        def fake_load(key):
            data = {
                "projects": [PROJECT],
                "materiales": materiales,
                "proveedores": [],
            }
            return data.get(key, [])

        def fake_save(key, value):
            saved[key] = value

        form = {
            "proveedor": "Proveedor Demo",
            "fecha": "2026-05-28",
            "item_desc[]": ["Tubo por metro"],
            "item_unit[]": ["ml"],
            "item_qty[]": ["4"],
            "item_catalog_id[]": ["TUBO-ML"],
            "item_origen[]": ["bundle_sync"],
            "item_sync_expected_catalog_item_id[]": ["TUBO-ML"],
            "item_sync_expected_qty[]": ["4"],
            "item_sync_issue[]": ["qty_shortage"],
        }

        with patch("tracker.routes.materials.load", side_effect=fake_load), \
             patch("tracker.routes.materials.save", side_effect=fake_save), \
             patch("tracker.routes.materials.new_id", return_value="LDM2"), \
             patch("tracker.validators.catalog_maps", return_value=(CATALOG, {})):
            response = self.client.post("/projects/P1/ldm/new", data=form)

        self.assertEqual(response.status_code, 302)
        item = saved["materiales"][0]["items"][0]
        self.assertEqual(item["origen"], "bundle_sync")
        self.assertEqual(item["sync_expected_catalog_item_id"], "TUBO-ML")
        self.assertEqual(item["sync_expected_qty"], 4)
        self.assertEqual(item["sync_issue"], "qty_shortage")


if __name__ == "__main__":
    unittest.main()
