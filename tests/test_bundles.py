import unittest
import json
from pathlib import Path

from tracker import bundles as b


class BundleVersioningTest(unittest.TestCase):
    def test_create_bundle_has_active_v1(self):
        bundle = b.create_bundle("COT-1", "Salida contacto", [{"catalog_item_id": "MAT-1", "qty": 2}])
        self.assertEqual(bundle["active_version"], 1)
        self.assertEqual(bundle["versions"][0]["status"], "active")
        self.assertEqual(bundle["versions"][0]["components"][0]["qty"], 2)

    def test_add_activate_and_delete_version(self):
        bundle = b.create_bundle("COT-1", "Salida contacto", [{"catalog_item_id": "MAT-1", "qty": 2}])
        bundle = b.add_bundle_version(bundle, [{"catalog_item_id": "MAT-2", "qty": 3}], make_active=True)
        self.assertEqual(bundle["active_version"], 2)
        self.assertEqual(b.get_active_bundle_version(bundle)["components"][0]["catalog_item_id"], "MAT-2")
        self.assertEqual(bundle["versions"][0]["status"], "archived")
        bundle = b.delete_bundle_version(bundle, 1)
        self.assertEqual(len(bundle["versions"]), 1)
        self.assertEqual(bundle["active_version"], 2)

    def test_cannot_delete_only_version(self):
        bundle = b.create_bundle("COT-1", "Salida contacto", [])
        with self.assertRaises(ValueError):
            b.delete_bundle_version(bundle, 1)


class ExpandQuoteBundlesTest(unittest.TestCase):
    def test_expands_quote_bundle_components(self):
        quote = {"items": [{"catalog_item_id": "COT-1", "description": "Salida", "qty": 10}]}
        bundles = [b.create_bundle("COT-1", "Salida", [
            {"catalog_item_id": "MAT-1", "qty": 6},
            {"catalog_item_id": "MAT-2", "qty": 3, "waste_pct": 10},
        ])]
        result = b.expand_quote_bundles(quote, bundles, {
            "MAT-1": {"nombre": "Cable", "unidad": "m"},
            "MAT-2": {"nombre": "Tierra", "unidad": "m"},
        })
        self.assertEqual(result["items"]["MAT-1"]["qty"], 60)
        self.assertEqual(result["items"]["MAT-2"]["qty"], 33)
        self.assertEqual(len(result["bundle_quote_items"]), 1)
        self.assertEqual(result["unmapped_quote_items"], [])

    def test_unmapped_quote_items_are_preserved(self):
        quote = {"items": [{"catalog_item_id": "SIMPLE", "qty": 1}]}
        result = b.expand_quote_bundles(quote, [], {})
        self.assertEqual(len(result["unmapped_quote_items"]), 1)
        self.assertEqual(result["items"], {})

    def test_seeded_circuit_bundles_expand_catalog_materials(self):
        root = Path(__file__).resolve().parents[1]
        bundles = json.loads((root / "data" / "bundles.json").read_text(encoding="utf-8"))
        quote = {
            "items": [
                {"catalog_item_id": "6CA7BF58", "description": "Circuito iluminación", "qty": 1},
                {"catalog_item_id": "5C329F0A", "description": "Circuito contactos", "qty": 1},
                {"catalog_item_id": "374DD97B", "description": "Circuito HVAC", "qty": 1},
            ]
        }

        result = b.expand_quote_bundles(quote, bundles, {})

        self.assertEqual(result["items"]["18C5C03E"]["qty"], 40)
        self.assertEqual(result["items"]["047C8246"]["qty"], 40)
        self.assertEqual(result["items"]["EFF4FECF"]["qty"], 40)
        self.assertEqual(result["items"]["2325432B"]["qty"], 50)
        self.assertEqual(result["unmapped_quote_items"], [])


if __name__ == "__main__":
    unittest.main()
