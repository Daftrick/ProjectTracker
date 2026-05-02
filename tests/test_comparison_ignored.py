import unittest

from tracker import comparison_ignored as ci


class ComparisonIgnoredTest(unittest.TestCase):
    def test_filters_by_scope_and_active(self):
        items = [
            {"catalog_item_id": "A", "scope": "both", "active": True},
            {"catalog_item_id": "B", "scope": "commercial", "active": True},
            {"catalog_item_id": "C", "scope": "technical", "active": True},
            {"catalog_item_id": "D", "scope": "both", "active": False},
        ]
        self.assertEqual(ci.ignored_catalog_ids(items, scope="commercial"), {"A", "B"})
        self.assertEqual(ci.ignored_catalog_ids(items, scope="technical"), {"A", "C"})

    def test_split_ignored_linked(self):
        kept, ignored = ci.split_ignored_linked({"A": {"qty": 1}, "B": {"qty": 2}}, {"B"})
        self.assertEqual(set(kept), {"A"})
        self.assertEqual(set(ignored), {"B"})

    def test_summarize_ignored(self):
        summary = ci.summarize_ignored(
            {"A": {"qty": 2, "total_cot": 150, "descripciones": ["Material A"]}},
            {"A": {"nombre": "Artículo A", "unidad": "pza"}},
            total_key="total_cot",
        )
        self.assertEqual(summary["count"], 1)
        self.assertEqual(summary["qty"], 2)
        self.assertEqual(summary["total"], 150)
        self.assertEqual(summary["rows"][0]["nombre"], "Artículo A")


if __name__ == "__main__":
    unittest.main()
