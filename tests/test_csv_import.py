import os
import tempfile
import unittest

from tracker.csv_import import parse_ldm_csv


class LdmCsvImportTest(unittest.TestCase):
    def test_parse_ldm_csv_reads_items_and_metadata(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v2-i1-20260426.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    "description,unit,qty\n"
                    "#proveedor,Procables de Mexico,\n"
                    "#fecha,2026-04-26,\n"
                    "\"Tubo Conduit\",pza,70\n"
                )

            result = parse_ldm_csv(path)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["metadata"]["proveedor"], "Procables de Mexico")
        self.assertEqual(result["metadata"]["fecha"], "2026-04-26")
        self.assertEqual(result["items"][0]["description"], "Tubo Conduit")
        self.assertEqual(result["items"][0]["qty"], 70)
        self.assertEqual(result["items"][0]["origen"], "csv")

    def test_parse_ldm_csv_accepts_spanish_headers_and_semicolon(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v2-i1-20260426.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("descripcion;unidad;cantidad\nCable THW-LS;m;125.5\n")

            result = parse_ldm_csv(path)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["items"][0]["description"], "Cable THW-LS")
        self.assertEqual(result["items"][0]["unit"], "m")
        self.assertEqual(result["items"][0]["qty"], 125.5)

    def test_parse_ldm_csv_reports_missing_required_headers(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v2-i1-20260426.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("nombre,unidad\nCable,pza\n")

            result = parse_ldm_csv(path)

        self.assertEqual(result["items"], [])
        self.assertIn("El CSV debe incluir una columna qty o cantidad.", result["errors"])

    def test_parse_ldm_csv_auto_links_catalog_item_id(self):
        catalog = [
            {"id": "3EF4F34C", "nombre": "Tubo Conduit Galvanizado Pared Delgada | 27 [mm] (1\")"},
            {"id": "94B273C0", "nombre": "Monitor Metálico Galvanizado Pared Delgada | 27 [mm] (1\")"},
        ]
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v2-i1-20260426.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    "description,unit,qty\n"
                    "\"Tubo Conduit Galvanizado Pared Delgada | 27 [mm] (1\"\")\",pza,10\n"
                    "\"Artículo Sin Coincidencia\",pza,5\n"
                )

            result = parse_ldm_csv(path, catalog=catalog)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["items"][0]["catalog_item_id"], "3EF4F34C")
        self.assertEqual(result["items"][1]["catalog_item_id"], "")

    def test_parse_ldm_csv_catalog_match_is_case_insensitive(self):
        catalog = [{"id": "ABCD1234", "nombre": "Cable de Cobre | THHW-LS | Calibre 12 AWG"}]
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v2-i1-20260426.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    "description,unit,qty\n"
                    "cable de cobre | thhw-ls | calibre 12 awg,m,100\n"
                )

            result = parse_ldm_csv(path, catalog=catalog)

        self.assertEqual(result["items"][0]["catalog_item_id"], "ABCD1234")

    def test_parse_ldm_csv_without_catalog_sets_empty_catalog_item_id(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-v2-i1-20260426.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("description,unit,qty\nCable THW-LS,m,50\n")

            result = parse_ldm_csv(path)

        self.assertEqual(result["items"][0]["catalog_item_id"], "")


if __name__ == "__main__":
    unittest.main()
