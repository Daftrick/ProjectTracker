import os
import tempfile
import unittest

from tracker.catalog import catalog_name_key
from tracker.quote_csv_import import parse_quote_csv, parse_quote_file, parse_quote_xlsx


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
        self.assertEqual(result["items"][0]["csv_row_number"], 5)

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


def _build_export_like_xlsx(path):
    """Crea un .xlsx con el mismo layout que exporta la app (quote_excel):
    filas informativas, encabezado de tabla con columna '#', subtítulos de
    sección, partidas, subtotales de sección y totales finales."""
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = "Cotización"
    ws.append(["Cotización:", "COT-Demo-G01-20260622"])
    ws.append(["Cliente:", "Cliente Demo"])
    ws.append(["Proyecto:", "Proyecto Demo"])
    ws.append(["Fecha:", "2026-06-22"])
    ws.append(["Moneda:", "MXN"])
    ws.append([])
    ws.append(["#", "Sección", "Nombre", "Unidad", "Cantidad", "Precio unitario", "Total"])
    # Sección A
    ws.append(["", "", "ÁREA A", "", "", "", ""])              # subtítulo de sección
    ws.append([1, "ÁREA A", "Salida Eléctrica para Luminaria", "pza", 10, 100, 1000])
    ws.append([2, "ÁREA A", "Instalación de Luminaria", "pza", 5, 50, 250])
    ws.append(["", "", "Subtotal ÁREA A", "", "", "", 1250])    # subtotal de sección
    # Sección B
    ws.append(["", "", "ÁREA B", "", "", "", ""])
    ws.append([3, "ÁREA B", "Salida Eléctrica para Contacto", "pza", 4, 25, 100])
    ws.append(["", "", "Subtotal ÁREA B", "", "", "", 100])
    # Totales finales
    ws.append([])
    ws.append(["", "", "", "", "", "Subtotal", 1350])
    ws.append(["", "", "", "", "", "IVA (16.0%)", 216])
    ws.append(["", "", "", "", "", "TOTAL", 1566])
    wb.save(path)


class QuoteXlsxImportTest(unittest.TestCase):
    def test_parse_quote_file_reads_excel_renamed_to_csv(self):
        """Un Excel exportado por la app (incluso con extensión .csv) debe
        importarse: solo se toman las partidas, no las filas de resumen."""
        with tempfile.TemporaryDirectory() as root:
            # Extensión .csv a propósito: el tipo se detecta por contenido.
            path = os.path.join(root, "COT-Demo-G01-20260622.csv")
            _build_export_like_xlsx(path)

            result = parse_quote_file(path, catalog=[])

        self.assertEqual(result["errors"], [])
        # Exactamente 3 partidas; subtítulos, subtotales y totales se omiten.
        self.assertEqual(len(result["items"]), 3)
        descriptions = [item["description"] for item in result["items"]]
        self.assertNotIn("ÁREA A", descriptions)
        self.assertFalse(any("Subtotal" in d for d in descriptions))
        self.assertNotIn("TOTAL", descriptions)
        # Datos y secciones correctos.
        self.assertEqual(result["items"][0]["qty"], 10.0)
        self.assertEqual(result["items"][0]["price"], 100.0)
        self.assertEqual(result["items"][0]["total"], 1000.0)
        self.assertEqual(result["items"][0]["section"], "ÁREA A")
        self.assertEqual(result["items"][-1]["section"], "ÁREA B")
        self.assertEqual(round(sum(i["total"] for i in result["items"]), 2), 1350.0)
        # Metadatos del encabezado informativo.
        self.assertEqual(result["metadata"].get("currency"), "MXN")
        self.assertEqual(result["metadata"].get("fecha"), "2026-06-22")

    def test_parse_quote_xlsx_links_catalog(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "cot.xlsx")
            _build_export_like_xlsx(path)
            result = parse_quote_xlsx(path, catalog=SYMBOL_CATALOG)

        self.assertEqual(result["errors"], [])
        ids = [item["catalog_item_id"] for item in result["items"]]
        self.assertEqual(ids, ["SALLUM", "INSTLUM", "CTK"])

    def test_old_xls_returns_clear_error(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "viejo.csv")
            with open(path, "wb") as handle:
                handle.write(b"\xd0\xcf\x11\xe0" + b"\x00" * 64)
            result = parse_quote_file(path)

        self.assertEqual(result["items"], [])
        self.assertIn(".xls", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
