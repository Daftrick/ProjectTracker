"""Smoke tests de UI Admin para bundles y reglas COT/LDM."""

import unittest
from unittest.mock import patch


CATALOG = [
    {"id": "COT-1", "nombre": "Salida eléctrica", "unidad": "pza", "descripcion": "", "precio": 0, "categoria": ""},
    {"id": "MAT-1", "nombre": "Tubo 1/2", "unidad": "pza", "descripcion": "", "precio": 0, "categoria": ""},
    {"id": "ML-1", "nombre": "Tubería 1/2 por ml", "unidad": "ml", "descripcion": "", "precio": 0, "categoria": ""},
]


class AdminBundlesRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app
        cls.client = app.test_client()

    def _fake_load(self, key):
        data = {
            "catalogo": CATALOG,
            "bundles": [],
            "comparison_rules": [],
            "proveedores": [],
            "projects": [],
            "fichas": [],
            "team": [],
            "quotes": [],
            "materiales": [],
        }
        return data.get(key, [])

    def test_bundles_page_loads(self):
        with patch("tracker.routes.admin.load", side_effect=self._fake_load):
            response = self.client.get("/bundles")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Bundles", response.data)

    def test_comparison_rules_page_loads(self):
        with patch("tracker.routes.admin.load", side_effect=self._fake_load):
            response = self.client.get("/comparison-rules")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Reglas", response.data)

    def test_create_bundle_persists_bundle(self):
        saved = {}

        def fake_load(key):
            return self._fake_load(key)

        def fake_save(key, value):
            saved[key] = value

        with patch("tracker.routes.admin.load", side_effect=fake_load), \
             patch("tracker.routes.admin.save", side_effect=fake_save), \
             patch("tracker.routes.admin.new_id", return_value="BND1"), \
             patch("tracker.routes.admin.today", return_value="2026-05-02"):
            response = self.client.post("/bundles", data={
                "catalog_item_id": "COT-1",
                "component_catalog_item_id[]": ["MAT-1"],
                "component_qty[]": ["2"],
                "component_waste_pct[]": ["5"],
                "component_comparison_rule_id[]": [""],
                "component_notes[]": ["Base"],
            })

        self.assertEqual(response.status_code, 302)
        self.assertIn("bundles", saved)
        self.assertEqual(saved["bundles"][0]["id"], "BND1")
        self.assertEqual(saved["bundles"][0]["catalog_item_id"], "COT-1")
        self.assertEqual(saved["bundles"][0]["versions"][0]["components"][0]["catalog_item_id"], "MAT-1")

    def test_create_comparison_rule_persists_rule(self):
        saved = {}

        def fake_load(key):
            return self._fake_load(key)

        def fake_save(key, value):
            saved[key] = value

        with patch("tracker.routes.admin.load", side_effect=fake_load), \
             patch("tracker.routes.admin.save", side_effect=fake_save), \
             patch("tracker.routes.admin.new_id", return_value="RULE1"), \
             patch("tracker.routes.admin.today", return_value="2026-05-02"):
            response = self.client.post("/comparison-rules", data={
                "name": "Tubo 1/2 ml vs pza",
                "cot_catalog_item_id": "ML-1",
                "ldm_catalog_item_id": "MAT-1",
                "cot_unit": "ml",
                "ldm_unit": "pza",
                "factor": "3",
                "direction": "ldm_to_cot",
                "rounding": "none",
                "tolerance_pct": "5",
                "active": "1",
            })

        self.assertEqual(response.status_code, 302)
        self.assertIn("comparison_rules", saved)
        self.assertEqual(saved["comparison_rules"][0]["id"], "RULE1")
        self.assertEqual(saved["comparison_rules"][0]["factor"], 3.0)


if __name__ == "__main__":
    unittest.main()
