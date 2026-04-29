import os
import tempfile
import unittest
from unittest.mock import patch

from tracker.drive import (
    active_drive_paths,
    decorate_csv_plano,
    latest_dwg_stem,
    normalize_config,
    parse_csv_plano_filename,
    resolve_config_path,
    scan_drive_folder,
)


class DriveCsvStatusTest(unittest.TestCase):
    def test_config_preserves_distinct_windows_and_macos_drive_paths(self):
        cfg = normalize_config({
            "drive_projects_path": r"H:\My Drive\Omniious\Proyectos IE",
            "drive_fichas_path": r"H:\My Drive\Omniious\Proyectos IE\Fichas Tecnicas",
            "drive_projects_path_macos": "/Users/rick/Library/CloudStorage/GoogleDrive-rick/My Drive/Omniious/Proyectos IE",
            "drive_fichas_path_macos": "/Users/rick/Library/CloudStorage/GoogleDrive-rick/My Drive/Omniious/Proyectos IE/Fichas Tecnicas",
        })

        self.assertEqual(resolve_config_path(cfg, "drive_projects_path", "windows"), r"H:\My Drive\Omniious\Proyectos IE")
        self.assertEqual(
            resolve_config_path(cfg, "drive_projects_path", "macos"),
            "/Users/rick/Library/CloudStorage/GoogleDrive-rick/My Drive/Omniious/Proyectos IE",
        )
        self.assertEqual(resolve_config_path(cfg, "drive_fichas_path", "windows"), r"H:\My Drive\Omniious\Proyectos IE\Fichas Tecnicas")
        self.assertEqual(
            resolve_config_path(cfg, "drive_fichas_path", "macos"),
            "/Users/rick/Library/CloudStorage/GoogleDrive-rick/My Drive/Omniious/Proyectos IE/Fichas Tecnicas",
        )

    def test_active_drive_paths_uses_current_platform_specific_value(self):
        cfg = {
            "drive_projects_path_windows": r"H:\My Drive\Omniious\Proyectos IE",
            "drive_projects_path_macos": "/Users/rick/Drive/Proyectos IE",
            "drive_fichas_path_windows": r"H:\My Drive\Omniious\Fichas",
            "drive_fichas_path_macos": "/Users/rick/Drive/Fichas",
        }

        with patch("tracker.drive.current_platform_key", return_value="macos"):
            paths = active_drive_paths(cfg)

        self.assertEqual(paths["platform"], "macos")
        self.assertEqual(paths["projects"], "/Users/rick/Drive/Proyectos IE")
        self.assertEqual(paths["fichas"], "/Users/rick/Drive/Fichas")

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

    def test_scan_drive_folder_ignores_autocad_auxiliary_files(self):
        with tempfile.TemporaryDirectory() as root:
            folder = os.path.join(root, "IE-001-OM001")
            os.mkdir(folder)
            for filename in ("IE-OM001.dwg.bak", "IE-OM001.dwl", "IE-OM001.dwl2"):
                with open(os.path.join(folder, filename), "w", encoding="utf-8") as handle:
                    handle.write("aux")

            result = scan_drive_folder("IE-001-OM001", root, [], clave="OM001")

        self.assertEqual(result["deliverable"], [])
        self.assertEqual(result["working"], [])
        self.assertEqual(result["other_files"], [])

    def test_latest_dwg_stem_prefers_highest_version_and_omits_extension(self):
        with tempfile.TemporaryDirectory() as folder:
            for filename in ("IE-OM001-V1-260401.dwg", "IE-OM001-V3-260420.dwg", "IE-OM001-V2-260425.dwg"):
                with open(os.path.join(folder, filename), "w", encoding="utf-8") as handle:
                    handle.write("dwg")

            result = latest_dwg_stem(folder)

        self.assertEqual(result, "IE-OM001-V3-260420")


if __name__ == "__main__":
    unittest.main()
