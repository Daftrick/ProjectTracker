import os
import tempfile
import unittest

from tracker.catalog import catalog_name_key
from tracker.quote_csv_import import parse_quote_csv


class QuoteCsvImportTest(unittest.TestCase):
    def test_catalog_name_key_normalizes_accents_and_special_separators(self):
        self.assertEqual(
            catalog_name_key('Tubería | 27 [mm] (1")'),
            catalog_name_key("Tuberia 27 mm 1"),
        )
        self.assertEqual(
            catalog_name_key("Instalación de Metro Lineal de Tira LED"),
            catalog_name_key("Instalacion de Metro Lineal de Tira Led"),
        )

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



    def test_parse_quote_csv_returns_error_on_ansi_encoding(self):
        """CSV escrito en cp1252 (fallback ANSI del LISP) debe retornar error
        legible en lugar de lanzar UnicodeDecodeError al servidor."""
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-V1-I1-COT-20260426.csv")
            # Simular fallback ANSI: cp1252 con acento 0xF3 (ó)
            with open(path, "wb") as handle:
                handle.write(b"description,unit,qty,price\r\nInstalaci\xf3n,pza,5,0\r\n")

            result = parse_quote_csv(path)

        self.assertEqual(result["items"], [])
        self.assertEqual(len(result["errors"]), 1)
        self.assertIn("codificación no compatible", result["errors"][0])


SYMBOL_CATALOG = [
    {
        "id": "SALLUM",
        "nombre": "Salida Eléctrica para Luminaria",
        "descripcion": "Omniious | Incluye Herramienta y Mano de Obra",
        "unidad": "pza",
    },
    {
        "id": "INSTLUM",
        "nombre": "Instalación de Luminaria",
        "descripcion": "Omniious | Incluye Herramienta y Mano de Obra",
        "unidad": "pza",
    },
    {
        "id": "INSTLED",
        "nombre": "Instalación de Metro Lineal de Tira LED",
        "descripcion": "Omniious | Incluye Herramienta y Mano de Obra",
        "unidad": "ml",
    },
    {
        "id": "APA",
        "nombre": "Salida Eléctrica para Apagador",
        "descripcion": "Omniious | Incluye Herramienta y Mano de Obra",
        "unidad": "pza",
    },
    {
        "id": "CTK",
        "nombre": "Salida Eléctrica para Contacto",
        "descripcion": "Omniious | Incluye Herramienta y Mano de Obra",
        "unidad": "pza",
    },
]


class QuoteSymbolFixturesTest(unittest.TestCase):
    def _parse_symbol_rows(self, rows):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-V1-I1-COT-SIMBOLOGIA.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("description,unit,qty,price\n")
                for description, unit, qty in rows:
                    handle.write(f"{description},{unit},{qty},\n")
            return parse_quote_csv(path, catalog=SYMBOL_CATALOG)

    def assert_symbol_ids(self, rows, expected_ids):
        result = self._parse_symbol_rows(rows)

        self.assertEqual(result["errors"], [])
        self.assertEqual([item["catalog_item_id"] for item in result["items"]], expected_ids)

    def test_smb01_links_luminaria_and_installation(self):
        self.assert_symbol_ids(
            [
                ("Salida Electrica para Luminaria", "pza", "4"),
                ("Instalacion de Luminaria", "pza", "4"),
            ],
            ["SALLUM", "INSTLUM"],
        )

    def test_smb02_links_apagador_and_contacto(self):
        self.assert_symbol_ids(
            [
                ("Salida Electrica para Apagador", "pza", "2"),
                ("Salida Electrica para Contacto", "pza", "5"),
            ],
            ["APA", "CTK"],
        )

    def test_smb03_led_links_luminaria_and_led_installation(self):
        self.assert_symbol_ids(
            [
                ("Salida Electrica para Luminaria", "pza", "3"),
                ("Instalacion de Metro Lineal de Tira LED", "ml", "18.5"),
            ],
            ["SALLUM", "INSTLED"],
        )

    def test_smb03_non_led_links_luminaria_and_installation(self):
        self.assert_symbol_ids(
            [
                ("Salida Electrica para Luminaria", "pza", "6"),
                ("Instalacion de Luminaria", "pza", "6"),
            ],
            ["SALLUM", "INSTLUM"],
        )


if __name__ == "__main__":
    unittest.main()
