import unittest

from tracker.utils import parse_csv_plano_filename


class ParseCsvPlanoFilenameTest(unittest.TestCase):
    def test_extracts_export_metadata(self):
        parsed = parse_csv_plano_filename("OM001-v2-i3-20260425.csv", "OM001")

        self.assertEqual(parsed["project"], "OM001")
        self.assertEqual(parsed["version"], 2)
        self.assertEqual(parsed["consecutive"], 3)
        self.assertEqual(parsed["date"], "20260425")
        self.assertEqual(parsed["date_label"], "25/04/2026")

    def test_rejects_cot_csv(self):
        self.assertIsNone(parse_csv_plano_filename("OM001-v2-i1-COT-20260527.csv", "OM001"))

    def test_rejects_wrong_clave(self):
        self.assertIsNone(parse_csv_plano_filename("OTRO-v1-i1-20260101.csv", "OM001"))

    def test_case_insensitive(self):
        parsed = parse_csv_plano_filename("OM001-V2-I3-20260425.CSV", "OM001")
        self.assertIsNotNone(parsed)
        self.assertEqual(parsed["version"], 2)


if __name__ == "__main__":
    unittest.main()
