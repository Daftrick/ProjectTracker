import unittest

from tracker.services import (
    filter_catalog_by_disciplina,
    upsert_mobile_draft,
    remove_item_from_draft,
    finalize_mobile_draft,
)


ITEM_A = {
    "id": "ITEM-A",
    "nombre": "Silla de oficina",
    "descripcion": "Silla ergonómica",
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
ITEM_C = {
    "id": "ITEM-C",
    "nombre": "Cableado red",
    "descripcion": "Cable UTP cat6",
    "unidad": "ml",
    "precio": 45.0,
    "disciplina": "Instalaciones",
}

CATALOG = [ITEM_A, ITEM_B, ITEM_C]
CATALOG_BY_ID = {item["id"]: item for item in CATALOG}

PROJECT = {
    "id": "PROJ-1",
    "name": "Oficina Central",
    "client": "Cliente SA",
    "version": "V1",
    "clave": "OFC",
    "folder_num": "001",
}


class IdFactory:
    def __init__(self, prefix="ID"):
        self.n = 0
        self.prefix = prefix

    def __call__(self):
        self.n += 1
        return f"{self.prefix}{self.n}"


class FilterCatalogTest(unittest.TestCase):
    def test_none_returns_all(self):
        result = filter_catalog_by_disciplina(CATALOG, None)
        self.assertEqual(result, CATALOG)

    def test_todos_returns_all(self):
        result = filter_catalog_by_disciplina(CATALOG, "Todos")
        self.assertEqual(result, CATALOG)

    def test_filters_by_disciplina(self):
        result = filter_catalog_by_disciplina(CATALOG, "Mobiliario")
        self.assertEqual([i["id"] for i in result], ["ITEM-A", "ITEM-B"])

    def test_unknown_disciplina_returns_empty(self):
        result = filter_catalog_by_disciplina(CATALOG, "Electrico")
        self.assertEqual(result, [])

    def test_empty_catalog(self):
        result = filter_catalog_by_disciplina([], "Mobiliario")
        self.assertEqual(result, [])


class UpsertMobileDraftTest(unittest.TestCase):
    def _upsert(self, quotes, item_id, qty=1):
        return upsert_mobile_draft(quotes, PROJECT, CATALOG_BY_ID, item_id, qty)

    def test_creates_draft_when_none_exists(self):
        quotes, draft = self._upsert([], "ITEM-A", qty=2)
        self.assertIsNotNone(draft)
        self.assertEqual(draft["status"], "draft")
        self.assertEqual(draft["project_id"], "PROJ-1")
        self.assertEqual(len(draft["items"]), 1)
        self.assertIn(draft, quotes)

    def test_item_fields_populated_from_catalog(self):
        _, draft = self._upsert([], "ITEM-A", qty=3)
        item = draft["items"][0]
        self.assertEqual(item["catalog_item_id"], "ITEM-A")
        self.assertEqual(item["description"], "Silla de oficina")
        self.assertEqual(item["unit"], "pza")
        self.assertEqual(item["qty"], "3")
        self.assertEqual(item["price"], "1500.0")
        self.assertAlmostEqual(item["total"], 4500.0)

    def test_totals_calculated(self):
        _, draft = self._upsert([], "ITEM-A", qty=2)
        self.assertAlmostEqual(draft["subtotal"], 3000.0)
        self.assertAlmostEqual(draft["tax"], 480.0)
        self.assertAlmostEqual(draft["total"], 3480.0)

    def test_second_item_appended_to_existing_draft(self):
        quotes, draft = self._upsert([], "ITEM-A", qty=1)
        quotes2, draft2 = upsert_mobile_draft(quotes, PROJECT, CATALOG_BY_ID, "ITEM-B", 2)
        self.assertIs(draft, draft2)
        self.assertEqual(len(draft2["items"]), 2)
        self.assertAlmostEqual(draft2["subtotal"], 7500.0)

    def test_re_adding_same_item_updates_qty(self):
        quotes, _ = self._upsert([], "ITEM-A", qty=1)
        quotes2, draft = self._upsert(quotes, "ITEM-A", qty=5)
        self.assertEqual(len(draft["items"]), 1)
        self.assertEqual(draft["items"][0]["qty"], "5")
        self.assertAlmostEqual(draft["subtotal"], 7500.0)

    def test_unknown_item_id_is_no_op(self):
        quotes_before = []
        quotes, draft = upsert_mobile_draft(
            quotes_before, PROJECT, CATALOG_BY_ID, "NONEXISTENT", 1
        )
        self.assertIsNone(draft)
        self.assertEqual(quotes, quotes_before)

    def test_draft_defaults(self):
        _, draft = self._upsert([], "ITEM-A")
        self.assertEqual(draft["quote_type"], "Proyecto")
        self.assertEqual(draft["currency"], "MXN")
        self.assertAlmostEqual(draft["tax_rate"], 16.0)
        self.assertEqual(draft["project_name"], "Oficina Central")
        self.assertEqual(draft["client"], "Cliente SA")

    def test_original_quotes_list_not_mutated(self):
        original = []
        quotes, _ = self._upsert(original, "ITEM-A")
        self.assertEqual(original, [])
        self.assertEqual(len(quotes), 1)

    def test_only_one_draft_created_per_project(self):
        quotes, _ = self._upsert([], "ITEM-A")
        quotes, _ = self._upsert(quotes, "ITEM-B")
        quotes, _ = self._upsert(quotes, "ITEM-C")
        drafts = [q for q in quotes if q.get("status") == "draft"]
        self.assertEqual(len(drafts), 1)

    def test_non_draft_quotes_untouched(self):
        existing_real = {"id": "QQ1", "project_id": "PROJ-1", "status": None}
        quotes, draft = upsert_mobile_draft(
            [existing_real], PROJECT, CATALOG_BY_ID, "ITEM-A", 1
        )
        self.assertIn(existing_real, quotes)
        self.assertEqual(len(quotes), 2)


class RemoveItemFromDraftTest(unittest.TestCase):
    def _setup(self):
        quotes, _ = upsert_mobile_draft([], PROJECT, CATALOG_BY_ID, "ITEM-A", 2)
        quotes, _ = upsert_mobile_draft(quotes, PROJECT, CATALOG_BY_ID, "ITEM-B", 1)
        return quotes

    def test_removes_item_and_recalculates(self):
        quotes = self._setup()
        quotes2, draft = remove_item_from_draft(quotes, "PROJ-1", "ITEM-A")
        ids = [i["catalog_item_id"] for i in draft["items"]]
        self.assertNotIn("ITEM-A", ids)
        self.assertIn("ITEM-B", ids)
        self.assertAlmostEqual(draft["subtotal"], 3000.0)

    def test_no_op_when_item_not_in_draft(self):
        quotes = self._setup()
        quotes2, draft = remove_item_from_draft(quotes, "PROJ-1", "ITEM-C")
        self.assertEqual(len(draft["items"]), 2)

    def test_returns_none_when_no_draft_exists(self):
        quotes, draft = remove_item_from_draft([], "PROJ-1", "ITEM-A")
        self.assertIsNone(draft)

    def test_empty_items_after_last_removal(self):
        quotes, _ = upsert_mobile_draft([], PROJECT, CATALOG_BY_ID, "ITEM-A", 1)
        quotes, draft = remove_item_from_draft(quotes, "PROJ-1", "ITEM-A")
        self.assertEqual(draft["items"], [])
        self.assertAlmostEqual(draft["subtotal"], 0.0)
        self.assertAlmostEqual(draft["total"], 0.0)


class FinalizeMobileDraftTest(unittest.TestCase):
    def test_finalize_removes_status_field(self):
        quotes, draft = upsert_mobile_draft([], PROJECT, CATALOG_BY_ID, "ITEM-A", 1)
        draft_id = draft["id"]
        quotes2, finalized = finalize_mobile_draft(
            quotes, PROJECT, draft_id, today_value="2026-06-18"
        )
        self.assertNotIn("status", finalized)

    def test_finalize_assigns_quote_number(self):
        quotes, draft = upsert_mobile_draft([], PROJECT, CATALOG_BY_ID, "ITEM-A", 1)
        draft_id = draft["id"]
        quotes2, finalized = finalize_mobile_draft(
            quotes, PROJECT, draft_id, today_value="2026-06-18"
        )
        self.assertIsNotNone(finalized.get("quote_number"))
        self.assertTrue(len(finalized["quote_number"]) > 0)

    def test_finalize_returns_none_for_unknown_id(self):
        quotes2, finalized = finalize_mobile_draft([], PROJECT, "NONEXISTENT")
        self.assertIsNone(finalized)
        self.assertEqual(quotes2, [])


if __name__ == "__main__":
    unittest.main()
