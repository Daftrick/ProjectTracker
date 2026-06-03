import unittest

from tracker.csv_catalog_validation import validate_csv_catalog_items


CATALOG = [
    {
        "id": "CAT-PZA",
        "nombre": "Salida Eléctrica para Contacto",
        "unidad": "pza",
    },
    {
        "id": "CAT-ML",
        "nombre": "Instalación de Metro Lineal de Tira LED",
        "unidad": "ml",
    },
    {
        "id": "CAT-M",
        "nombre": "Cable de Cobre | THHW-LS | Calibre 12 AWG",
        "unidad": "m",
    },
    {
        "id": "CAT-NOUNIT",
        "nombre": "Articulo Sin Unidad",
        "unidad": "",
    },
]


class CsvCatalogValidationTest(unittest.TestCase):
    def test_accepts_normalized_name_and_matching_unit(self):
        result = validate_csv_catalog_items(
            [{"description": "Salida Electrica para Contacto", "unit": "pza", "csv_row_number": 2}],
            CATALOG,
            kind="LDM",
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["errors"], [])

    def test_blocks_missing_catalog_name(self):
        result = validate_csv_catalog_items(
            [{"description": "Concepto Inexistente", "unit": "pza", "csv_row_number": 5}],
            CATALOG,
        )

        self.assertFalse(result["ok"])
        self.assertIn("Fila 5", result["errors"][0])
        self.assertIn("no tiene coincidencia exacta", result["errors"][0])

    def test_blocks_unit_mismatch(self):
        result = validate_csv_catalog_items(
            [{"description": "Salida Eléctrica para Contacto", "unit": "m", "csv_row_number": 3}],
            CATALOG,
        )

        self.assertFalse(result["ok"])
        self.assertIn('CSV="m", catálogo="pza"', result["errors"][0])

    def test_accepts_unit_case_insensitive(self):
        result = validate_csv_catalog_items(
            [{"description": "Instalacion de Metro Lineal de Tira LED", "unit": "ML"}],
            CATALOG,
        )

        self.assertTrue(result["ok"])

    def test_rejects_m_and_ml_as_different_units(self):
        result = validate_csv_catalog_items(
            [{"description": "Cable de Cobre | THHW-LS | Calibre 12 AWG", "unit": "ml"}],
            CATALOG,
        )

        self.assertFalse(result["ok"])
        self.assertIn('CSV="ml", catálogo="m"', result["errors"][0])

    def test_blocks_catalog_item_without_unit(self):
        result = validate_csv_catalog_items(
            [{"description": "Articulo Sin Unidad", "unit": "pza"}],
            CATALOG,
        )

        self.assertFalse(result["ok"])
        self.assertIn("no tiene unidad configurada", result["errors"][0])


if __name__ == "__main__":
    unittest.main()
