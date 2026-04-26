import os
import tempfile
import unittest

from tracker.drive import decorate_csv_plano, parse_csv_plano_filename, scan_drive_folder


class DriveCsvStatusTest(unittest.TestCase):
    def test_parse_csv_plano_filename_extracts_export_metadata(self):
        parsed = parse_csv_plano_filename("OM001-v2-i3-20260425.csv", "OM001")

        self.assertEqual(parsed["project"], "OM001")
        self.assertEqual(parsed["version"], 2)
        self.assertEqual(parsed["consecutive"], 3)
        self.assertEqual(parsed["date"], "20260425")
        self.assertEqual(parsed["date_label"], "25/04/2026")

    def test_decorate_csv_marks_imported_outdated_and_pending_update(self):
        files = [
            {"name": "OM001-v2-i1-20260420.csv", "size_str": "10 KB", "mtime_str": "20-Apr-2026 10:00"},
            {"name": "OM001-v2-i2-20260424.csv", "size_str": "12 KB", "mtime_str": "24-Apr-2026 10:00"},
        ]
        ldms = [{"ldm_number": "LDM-OM001-01", "csv_origen": "OM001-v2-i1-20260420.csv"}]

        result = decorate_csv_plano(files, ldms, "OM001")

        self.assertEqual(result[0]["status"], "desactualizado")
        self.assertEqual(result[0]["linked_ldm"], "LDM-OM001-01")
        self.assertEqual(result[1]["status"], "pendiente")
        self.assertEqual(result[1]["status_label"], "Actualización")

    def test_scan_drive_folder_includes_csv_status(self):
        with tempfile.TemporaryDirectory() as root:
            os.mkdir(os.path.join(root, "IE-001-OM001"))
            csv_path = os.path.join(root, "IE-001-OM001", "OM001-v1-i1-20260420.csv")
            with open(csv_path, "w", encoding="utf-8") as handle:
                handle.write("codigo_item,descripcion,unidad,cantidad\n")

            result = scan_drive_folder("IE-001-OM001", root, [], clave="OM001")

        self.assertEqual(len(result["csv_plano"]), 1)
        self.assertEqual(result["csv_plano"][0]["status"], "pendiente")


if __name__ == "__main__":
    unittest.main()
