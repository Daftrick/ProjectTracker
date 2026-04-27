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


if __name__ == "__main__":
    unittest.main()
