import unittest

from tracker.catalog import hydrate_ldm_item, hydrate_quote_item
from tracker.deletions import delete_catalog_items_data, delete_project_data, purge_deleted_catalog_items_from_record


class DeletionsTest(unittest.TestCase):
    def test_delete_project_cascades_and_unlinks_fichas(self):
        result = delete_project_data(
            "PRJ1",
            projects=[{"id": "PRJ1"}, {"id": "PRJ2"}],
            tasks=[{"project_id": "PRJ1"}, {"project_id": "PRJ2"}],
            deliveries=[{"project_id": "PRJ1"}],
            quotes=[{"project_id": "PRJ1"}, {"project_id": "PRJ2"}],
            materiales=[{"project_id": "PRJ1"}],
            fichas=[{"id": "F1", "projects": ["PRJ1", "PRJ2"]}, {"id": "F2", "projects": ["PRJ1"]}],
        )

        self.assertEqual(result["projects"], [{"id": "PRJ2"}])
        self.assertEqual(result["tasks"], [{"project_id": "PRJ2"}])
        self.assertEqual(result["quotes"], [{"project_id": "PRJ2"}])
        self.assertEqual(result["fichas"][0]["projects"], ["PRJ2"])
        self.assertEqual(result["fichas"][1]["projects"], [])
        self.assertEqual(result["counts"]["ficha_refs"], 2)

    def test_delete_catalog_items_marks_quote_and_ldm_refs_as_deleted_snapshots(self):
        result = delete_catalog_items_data(
            {"CAT1"},
            catalogo=[
                {
                    "id": "CAT1",
                    "nombre": "Interruptor",
                    "descripcion": "3P 100A",
                    "unidad": "pza",
                    "precio": 1500,
                },
                {"id": "CAT2", "nombre": "Cable"},
            ],
            quotes=[{"items": [{"catalog_item_id": "CAT1", "description": "Interruptor"}, {"catalog_item_id": "CAT2"}]}],
            materiales=[{"items": [{"catalog_item_id": "CAT1", "description": "Interruptor"}]}],
            today_value="2026-04-28",
        )

        quote_item = result["quotes"][0]["items"][0]
        ldm_item = result["materiales"][0]["items"][0]
        deleted_snapshot = {
            "id": "CAT1",
            "nombre": "Interruptor",
            "descripcion": "3P 100A",
            "unidad": "pza",
            "precio": 1500,
            "deleted_at": "2026-04-28",
        }

        self.assertEqual(result["catalogo"], [{"id": "CAT2", "nombre": "Cable"}])
        self.assertEqual(quote_item["catalog_item_id"], "")
        self.assertEqual(quote_item["deleted_catalog_item"], deleted_snapshot)
        self.assertEqual(result["quotes"][0]["items"][1]["catalog_item_id"], "CAT2")
        self.assertEqual(ldm_item["catalog_item_id"], "")
        self.assertEqual(ldm_item["deleted_catalog_item"], deleted_snapshot)
        self.assertEqual(result["counts"]["quote_refs"], 1)
        self.assertEqual(result["counts"]["material_refs"], 1)

    def test_hydrate_items_flags_deleted_catalog_snapshot_without_relinking(self):
        deleted_snapshot = {"id": "CAT1", "descripcion": "Artículo eliminado", "deleted_at": "2026-04-28"}
        quote_item = hydrate_quote_item(
            {
                "catalog_item_id": "",
                "description": "Interruptor histórico",
                "unit": "pza",
                "qty": 2,
                "price": 100,
                "deleted_catalog_item": deleted_snapshot,
            },
            {"CAT1": {"id": "CAT1", "nombre": "Nuevo catálogo"}},
            {},
        )
        ldm_item = hydrate_ldm_item(
            {
                "catalog_item_id": "",
                "description": "Interruptor histórico",
                "unit": "pza",
                "qty": 2,
                "deleted_catalog_item": deleted_snapshot,
            },
            {"CAT1": {"id": "CAT1", "nombre": "Nuevo catálogo"}},
            {},
        )

        self.assertFalse(quote_item["catalog_linked"])
        self.assertFalse(quote_item["catalog_missing"])
        self.assertTrue(quote_item["catalog_deleted"])
        self.assertEqual(quote_item["catalog_item_id"], "")
        self.assertFalse(ldm_item["catalog_linked"])
        self.assertFalse(ldm_item["catalog_missing"])
        self.assertTrue(ldm_item["catalog_deleted"])
        self.assertEqual(ldm_item["catalog_item_id"], "")

    def test_purge_deleted_catalog_items_removes_only_marked_rows(self):
        record = {
            "id": "DOC1",
            "items": [
                {"description": "Vivo", "catalog_item_id": "CAT2"},
                {"description": "Borrado", "catalog_item_id": "", "deleted_catalog_item": {"id": "CAT1"}},
                {"description": "Manual", "catalog_item_id": ""},
            ],
        }

        updated, removed = purge_deleted_catalog_items_from_record(record)

        self.assertEqual(removed, 1)
        self.assertEqual([item["description"] for item in updated["items"]], ["Vivo", "Manual"])
        self.assertEqual(len(record["items"]), 3)


if __name__ == "__main__":
    unittest.main()
