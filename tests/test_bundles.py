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


class QuoteItemBundleBreakdownTest(unittest.TestCase):
    def test_breakdown_multiplies_component_quantities_without_prices(self):
        bundle = b.create_bundle("COT-1", "Instalacion", [
            {"catalog_item_id": "MAT-1", "qty": 2},
            {"catalog_item_id": "MAT-2", "qty": 1.5, "waste_pct": 10},
        ])
        rows = b.quote_item_bundle_breakdown(
            {"catalog_item_id": "COT-1", "qty": 3},
            b.bundle_by_catalog_item_id([bundle]),
            {
                "MAT-1": {"nombre": "Salida contacto", "unidad": "pza", "precio": 99},
                "MAT-2": {"nombre": "Tuberia EMT", "unidad": "m", "precio": 20},
            },
        )

        self.assertEqual(rows[0], {
            "catalog_item_id": "MAT-1",
            "description": "Salida contacto",
            "unit": "pza",
            "qty": 6.0,
            "qty_display": "6",
        })
        self.assertAlmostEqual(rows[1]["qty"], 4.5)
        self.assertEqual(rows[1]["qty_display"], "4.5")
        for row in rows:
            self.assertNotIn("price", row)
            self.assertNotIn("total", row)

    def test_breakdown_prefers_snapshot_when_present(self):
        bundle = b.create_bundle("COT-1", "Instalacion", [{"catalog_item_id": "MAT-LIVE", "qty": 20}])
        item = {
            "catalog_item_id": "COT-1",
            "qty": 3,
            "bundle_snapshot": {
                "components": [
                    {"catalog_item_id": "MAT-SNAP", "description": "Snapshot item", "unit": "pza", "qty": 7}
                ]
            },
        }

        rows = b.quote_item_bundle_breakdown(item, b.bundle_by_catalog_item_id([bundle]), {})

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["catalog_item_id"], "MAT-SNAP")
        self.assertEqual(rows[0]["qty"], 7.0)

    def test_breakdown_missing_bundle_returns_empty_list(self):
        rows = b.quote_item_bundle_breakdown({"catalog_item_id": "NOPE", "qty": 1}, {}, {})

        self.assertEqual(rows, [])

    def test_hydrate_quote_bundle_breakdowns_keeps_totals_and_sections(self):
        quote = {
            "subtotal": 100,
            "tax": 16,
            "total": 116,
            "items": [
                {"kind": "section", "section": "Instalaciones"},
                {"catalog_item_id": "COT-1", "description": "Bundle", "section": "Instalaciones", "qty": 2, "total": 100},
            ],
            "sections": [
                {"name": "Instalaciones", "items": [], "subtotal": 100},
            ],
        }
        bundle = b.create_bundle("COT-1", "Bundle", [{"catalog_item_id": "MAT-1", "qty": 3}])

        hydrated = b.hydrate_quote_bundle_breakdowns(quote, [bundle], {"MAT-1": {"nombre": "Material", "unidad": "m"}})

        self.assertEqual(hydrated["subtotal"], 100)
        self.assertEqual(hydrated["tax"], 16)
        self.assertEqual(hydrated["total"], 116)
        item = hydrated["sections"][0]["items"][0]
        self.assertTrue(item["has_bundle_breakdown"])
        self.assertEqual(item["bundle_breakdown"][0]["description"], "Material")
        self.assertEqual(item["bundle_breakdown"][0]["qty"], 6.0)


class SeededBundlesTest(unittest.TestCase):
    """Cobertura de los bundles reales en data/bundles.json."""

    @classmethod
    def setUpClass(cls):
        root = Path(__file__).resolve().parents[1]
        cls.bundles = json.loads((root / "data" / "bundles.json").read_text(encoding="utf-8"))

    def _expand(self, catalog_item_id, qty):
        quote = {"items": [{"catalog_item_id": catalog_item_id, "qty": qty}]}
        return b.expand_quote_bundles(quote, self.bundles, {})

    def test_tubo_conduit_16mm_expands_all_components(self):
        result = self._expand("81F2CB4E", 10)
        items = result["items"]
        self.assertEqual(result["unmapped_quote_items"], [])
        self.assertEqual(result["invalid_components"], [])
        # tubo: 0.3333 * 10 = 3.333 rounded to 4 dp
        self.assertAlmostEqual(items["92218A02"]["qty"], 3.333, places=3)
        # conector y abrazadera: 1.0 y 2.0 por metro
        self.assertAlmostEqual(items["E32BE145"]["qty"], 10.0, places=3)
        self.assertAlmostEqual(items["1D5577C3"]["qty"], 20.0, places=3)
        # soporte: 0.1666 * 10 = 1.666
        self.assertAlmostEqual(items["9AC13BC2"]["qty"], 1.666, places=3)

    def test_salida_luminaria_expands_all_components(self):
        result = self._expand("42075597", 5)
        items = result["items"]
        self.assertEqual(result["unmapped_quote_items"], [])
        self.assertEqual(result["invalid_components"], [])
        # caja: 1.0 por salida
        self.assertAlmostEqual(items["92218A02"]["qty"], 5.0, places=3)
        # cable fase/neutro: 6.0 por salida
        self.assertAlmostEqual(items["18C5C03E"]["qty"], 30.0, places=3)
        # conductor desnudo: 3.0 por salida
        self.assertAlmostEqual(items["2325432B"]["qty"], 15.0, places=3)
        # soporte: 0.1666 * 5 = 0.833
        self.assertAlmostEqual(items["9AC13BC2"]["qty"], 0.833, places=3)

    def test_all_seeded_bundles_have_valid_active_version(self):
        for bundle in self.bundles:
            av = b.get_active_bundle_version(bundle)
            self.assertIsNotNone(av, f"Bundle {bundle.get('id')} sin versión activa")
            self.assertTrue(len(av.get("components", [])) > 0,
                            f"Bundle {bundle.get('id')} sin componentes")

    def test_no_duplicate_catalog_item_ids_in_index(self):
        index = b.bundle_by_catalog_item_id(self.bundles)
        self.assertEqual(len(index), len(self.bundles),
                         "Hay catalog_item_ids duplicados en bundles.json")


class BundleEdgeCasesTest(unittest.TestCase):
    """Casos borde de expand_quote_bundles y versionado."""

    def test_component_with_zero_qty_goes_to_invalid(self):
        bundle = b.create_bundle("COT-X", "Test", [
            {"catalog_item_id": "MAT-GOOD", "qty": 2},
            {"catalog_item_id": "MAT-ZERO", "qty": 0},
        ])
        quote = {"items": [{"catalog_item_id": "COT-X", "qty": 3}]}
        result = b.expand_quote_bundles(quote, [bundle], {})
        self.assertEqual(result["items"].get("MAT-GOOD", {}).get("qty"), 6.0)
        self.assertNotIn("MAT-ZERO", result["items"])
        self.assertEqual(len(result["invalid_components"]), 1)
        self.assertEqual(result["invalid_components"][0]["reason"], "invalid_component")

    def test_component_with_empty_catalog_item_id_goes_to_invalid(self):
        bundle = b.create_bundle("COT-Y", "Test", [
            {"catalog_item_id": "", "qty": 1},
        ])
        quote = {"items": [{"catalog_item_id": "COT-Y", "qty": 1}]}
        result = b.expand_quote_bundles(quote, [bundle], {})
        self.assertEqual(result["items"], {})
        self.assertEqual(len(result["invalid_components"]), 1)

    def test_bundle_with_no_versions_goes_to_invalid(self):
        bundle = {"id": "B-EMPTY", "catalog_item_id": "COT-Z", "active_version": 0, "versions": []}
        quote = {"items": [{"catalog_item_id": "COT-Z", "qty": 2}]}
        result = b.expand_quote_bundles(quote, [bundle], {})
        self.assertEqual(result["items"], {})
        self.assertEqual(len(result["invalid_components"]), 1)
        self.assertEqual(result["invalid_components"][0]["reason"], "bundle_without_active_version")

    def test_activate_nonexistent_version_raises(self):
        bundle = b.create_bundle("COT-1", "Test", [])
        with self.assertRaises(ValueError):
            b.activate_bundle_version(bundle, 99)

    def test_delete_nonexistent_version_raises(self):
        bundle = b.create_bundle("COT-1", "Test", [])
        bundle = b.add_bundle_version(bundle, [])
        with self.assertRaises(ValueError):
            b.delete_bundle_version(bundle, 99)

    def test_waste_pct_applied_correctly(self):
        bundle = b.create_bundle("COT-W", "Waste test", [
            {"catalog_item_id": "MAT-W", "qty": 10, "waste_pct": 15},
        ])
        quote = {"items": [{"catalog_item_id": "COT-W", "qty": 2}]}
        result = b.expand_quote_bundles(quote, [bundle], {})
        # 2 * 10 * (1 + 15/100) = 23.0
        self.assertAlmostEqual(result["items"]["MAT-W"]["qty"], 23.0, places=4)

    def test_section_markers_are_skipped(self):
        quote = {"items": [
            {"catalog_item_id": "", "kind": "section", "description": "== Sección ==", "qty": 0},
            {"catalog_item_id": "COT-1", "qty": 1},
        ]}
        bundle = b.create_bundle("COT-1", "Item", [{"catalog_item_id": "MAT-1", "qty": 2}])
        result = b.expand_quote_bundles(quote, [bundle], {})
        self.assertIn("MAT-1", result["items"])
        self.assertEqual(len(result["unmapped_quote_items"]) + len(result["bundle_quote_items"]), 1)


class BreakdownQtyRulesTest(unittest.TestCase):
    def test_no_waste_pct_in_live_breakdown(self):
        bundle = b.create_bundle("COT-W", "Bundle con desperdicio", [
            {"catalog_item_id": "MAT-W", "qty": 2.0, "waste_pct": 20},
        ])
        rows = b.quote_item_bundle_breakdown(
            {"catalog_item_id": "COT-W", "qty": 3},
            b.bundle_by_catalog_item_id([bundle]),
            {"MAT-W": {"nombre": "Material", "unidad": "m"}},
        )
        # Without waste: 3 * 2.0 = 6.0 (not 7.2 which would include waste)
        self.assertAlmostEqual(rows[0]["qty"], 6.0)

    def test_discrete_unit_ceil(self):
        bundle = b.create_bundle("COT-D", "Bundle discreto", [
            {"catalog_item_id": "MAT-P", "qty": 1.5},
        ])
        rows = b.quote_item_bundle_breakdown(
            {"catalog_item_id": "COT-D", "qty": 3},
            b.bundle_by_catalog_item_id([bundle]),
            {"MAT-P": {"nombre": "Piezas", "unidad": "pza"}},
        )
        # 3 * 1.5 = 4.5 → ceil → 5 for discrete unit "pza"
        self.assertEqual(rows[0]["qty"], 5)
        self.assertEqual(rows[0]["qty_display"], "5")

    def test_continuous_unit_not_ceiled(self):
        bundle = b.create_bundle("COT-C", "Bundle continuo", [
            {"catalog_item_id": "MAT-M", "qty": 1.5},
        ])
        rows = b.quote_item_bundle_breakdown(
            {"catalog_item_id": "COT-C", "qty": 3},
            b.bundle_by_catalog_item_id([bundle]),
            {"MAT-M": {"nombre": "Metro lineal", "unidad": "m"}},
        )
        self.assertAlmostEqual(rows[0]["qty"], 4.5)


class CaptureBundleSnapshotTest(unittest.TestCase):
    def _make_bundle(self, catalog_item_id, components):
        return b.create_bundle(catalog_item_id, "Bundle", components)

    def test_returns_none_when_no_bundle(self):
        item = {"catalog_item_id": "NOPE", "qty": 1}
        result = b.capture_bundle_snapshot(item, {}, {})
        self.assertIsNone(result)

    def test_returns_none_when_no_catalog_item_id(self):
        result = b.capture_bundle_snapshot({}, {}, {})
        self.assertIsNone(result)

    def test_captures_description_and_unit_from_catalog(self):
        bundle = self._make_bundle("COT-1", [
            {"catalog_item_id": "MAT-A", "qty": 2.0},
            {"catalog_item_id": "MAT-B", "qty": 1.0},
        ])
        catalog_by_id = {
            "MAT-A": {"nombre": "Cable THHN", "unidad": "m"},
            "MAT-B": {"nombre": "Conector", "unidad": "pza"},
        }
        result = b.capture_bundle_snapshot(
            {"catalog_item_id": "COT-1", "qty": 5},
            b.bundle_by_catalog_item_id([bundle]),
            catalog_by_id,
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(result["components"]), 2)
        a = result["components"][0]
        self.assertEqual(a["catalog_item_id"], "MAT-A")
        self.assertEqual(a["description"], "Cable THHN")
        self.assertEqual(a["unit"], "m")
        self.assertEqual(a["qty"], 2.0)

    def test_snapshot_has_bundle_id_and_version(self):
        bundle = self._make_bundle("COT-2", [{"catalog_item_id": "MAT-A", "qty": 1}])
        bundle["id"] = "BNDL-42"
        result = b.capture_bundle_snapshot(
            {"catalog_item_id": "COT-2"},
            b.bundle_by_catalog_item_id([bundle]),
            {"MAT-A": {"nombre": "X", "unidad": "pza"}},
        )
        self.assertEqual(result["bundle_id"], "BNDL-42")
        self.assertEqual(result["bundle_version"], 1)
        self.assertIn("captured_at", result)

    def test_skips_zero_qty_components(self):
        bundle = self._make_bundle("COT-3", [
            {"catalog_item_id": "MAT-OK", "qty": 3.0},
            {"catalog_item_id": "MAT-ZERO", "qty": 0},
        ])
        result = b.capture_bundle_snapshot(
            {"catalog_item_id": "COT-3"},
            b.bundle_by_catalog_item_id([bundle]),
            {"MAT-OK": {"nombre": "OK", "unidad": "m"}},
        )
        self.assertEqual(len(result["components"]), 1)
        self.assertEqual(result["components"][0]["catalog_item_id"], "MAT-OK")


if __name__ == "__main__":
    unittest.main()
