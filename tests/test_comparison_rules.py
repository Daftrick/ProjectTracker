import unittest

from tracker import comparison_rules as cr


class ConversionRulesTest(unittest.TestCase):
    def test_ldm_piece_to_cot_linear_meter(self):
        rule = {
            "id": "R1",
            "cot_catalog_item_id": "TUBO-ML",
            "ldm_catalog_item_id": "TUBO-PZA",
            "factor": 3,
            "direction": "ldm_to_cot",
            "rounding": "none",
        }
        self.assertEqual(cr.convert_qty(10, rule, to_expected=True), 30)

    def test_aggregate_ldm_converts_to_expected_id(self):
        ldms = [{"ldm_number": "LDM-1", "items": [
            {"catalog_item_id": "TUBO-PZA", "description": "Tubo tramo", "qty": 4},
            {"catalog_item_id": "CABLE", "description": "Cable", "qty": 20},
        ]}]
        rules = [{
            "id": "R1",
            "cot_catalog_item_id": "TUBO-ML",
            "ldm_catalog_item_id": "TUBO-PZA",
            "factor": 3,
            "direction": "ldm_to_cot",
        }]
        actual = cr.aggregate_ldm_for_expected_items(ldms, rules, {})["items"]
        self.assertEqual(actual["TUBO-ML"]["qty"], 12)
        self.assertEqual(actual["CABLE"]["qty"], 20)

    def test_compare_expected_vs_actual_marks_shortage_and_excess(self):
        expected = {
            "A": {"qty": 100, "sources": []},
            "B": {"qty": 10, "sources": []},
        }
        actual = {
            "A": {"qty": 90, "sources": []},
            "C": {"qty": 5, "sources": []},
        }
        result = cr.compare_expected_vs_actual(expected, actual, [], {})
        issues = {row["catalog_item_id"]: row["issue"] for row in result["rows"]}
        self.assertEqual(issues["A"], "qty_shortage")
        self.assertEqual(issues["B"], "missing_in_ldm")
        self.assertEqual(issues["C"], "extra_in_ldm")
        self.assertEqual(result["status"], "critical")

    def test_tolerance_accepts_small_differences(self):
        expected = {"A": {"qty": 100, "sources": []}}
        actual = {"A": {"qty": 96, "sources": []}}
        rules = [{"cot_catalog_item_id": "A", "ldm_catalog_item_id": "AX", "tolerance_pct": 5}]
        result = cr.compare_expected_vs_actual(expected, actual, rules, {})
        self.assertEqual(result["rows"][0]["status"], "ok")


if __name__ == "__main__":
    unittest.main()
