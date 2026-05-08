import os
import tempfile
import unittest

from tracker.quote_csv_import import parse_quote_csv


class QuoteCsvImportTest(unittest.TestCase):
    def test_parse_quote_csv_reads_items_metadata_and_links_catalog(self):
        catalog = [
            {
                "id": "CAT1",
                "nombre": "Metro Lineal de Tuberia Conduit 1",
                "descripcion": "Omniious | Incluye instalacion",
            }
        ]
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-V1-I1-COT-20260508.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(
                    "description,unit,qty,price\n"
                    "#proyecto_clave,OM001,,\n"
                    "#quote_type,General,,\n"
                    "#fecha,2026-05-08,,\n"
                    "Metro Lineal de Tuberia Conduit 1,ml,12.5,150\n"
                )

            result = parse_quote_csv(path, catalog=catalog)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["metadata"]["proyecto_clave"], "OM001")
        self.assertEqual(result["metadata"]["quote_type"], "General")
        self.assertEqual(result["items"][0]["catalog_item_id"], "CAT1")
        self.assertEqual(result["items"][0]["qty"], 12.5)
        self.assertEqual(result["items"][0]["price"], 150.0)
        self.assertEqual(result["items"][0]["total"], 1875.0)

    def test_parse_quote_csv_accepts_spanish_headers_semicolon_and_missing_price(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "cot.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("descripcion;unidad;cantidad\nSalida Electrica;pza;4\n")

            result = parse_quote_csv(path)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["items"][0]["description"], "Salida Electrica")
        self.assertEqual(result["items"][0]["price"], 0.0)

    def test_parse_quote_csv_accepts_metadata_before_header(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "cot.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("#source,lisp_cedularec,,\ndescription,unit,qty,price\nConcepto,pza,1,2\n")

            result = parse_quote_csv(path)

        self.assertEqual(result["errors"], [])
        self.assertEqual(result["metadata"]["source"], "lisp_cedularec")

    def test_parse_quote_csv_reports_missing_required_headers(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "cot.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("description,unit\nConcepto,pza\n")

            result = parse_quote_csv(path)

        self.assertEqual(result["items"], [])
        self.assertIn("El CSV debe incluir una columna qty o cantidad.", result["errors"])


if __name__ == "__main__":
    unittest.main()
