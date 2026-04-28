"""Pruebas para tracker.catalog_search y la API /api/catalogo."""

import unittest

from tracker import catalog_search as cs


class TokenizeTest(unittest.TestCase):
    def test_splits_by_whitespace_and_normalizes(self):
        self.assertEqual(cs.tokenize("Interruptor 30A"), ["interruptor", "30a"])

    def test_strips_diacritics(self):
        self.assertEqual(cs.tokenize("Iluminación LED"), ["iluminacion", "led"])

    def test_collapses_extra_whitespace(self):
        self.assertEqual(cs.tokenize("  cable    14   awg "), ["cable", "14", "awg"])

    def test_empty_query_yields_empty_list(self):
        self.assertEqual(cs.tokenize(""), [])
        self.assertEqual(cs.tokenize("   "), [])


class MatchItemTest(unittest.TestCase):
    SAMPLE = {
        "nombre": "Interruptor termomagnético 30 A 2P",
        "descripcion": "Marca Square D",
        "categoria": "Tableros",
    }

    def test_all_tokens_must_match(self):
        self.assertTrue(cs.match_item(self.SAMPLE, ["interruptor", "30"]))
        self.assertTrue(cs.match_item(self.SAMPLE, ["square", "termomagnetico"]))
        self.assertFalse(cs.match_item(self.SAMPLE, ["interruptor", "40"]))

    def test_diacritics_and_case_ignored(self):
        self.assertTrue(cs.match_item(self.SAMPLE, ["TERMOMAGNETICO"]))
        self.assertTrue(cs.match_item(self.SAMPLE, ["TERMOMAGNÉTICO"]))

    def test_no_tokens_means_match(self):
        self.assertTrue(cs.match_item(self.SAMPLE, []))

    def test_categoria_filter_matches_normalized(self):
        self.assertTrue(cs.match_item(self.SAMPLE, [], categoria="tableros"))
        self.assertTrue(cs.match_item(self.SAMPLE, [], categoria="TABLEROS"))
        self.assertFalse(cs.match_item(self.SAMPLE, [], categoria="Iluminación"))

    def test_tokens_can_match_across_fields(self):
        # 'tableros' está en categoria; 'square' está en descripcion
        self.assertTrue(cs.match_item(self.SAMPLE, ["tableros", "square"]))


class FilterCatalogTest(unittest.TestCase):
    ITEMS = [
        {"nombre": "Foco LED 9W", "descripcion": "Marca Phillips", "categoria": "Iluminación"},
        {"nombre": "Cable 14 AWG", "descripcion": "Cobre", "categoria": "Conductores"},
        {"nombre": "Interruptor termomagnético 30A", "descripcion": "Square D", "categoria": "Tableros"},
        {"nombre": "Apagador sencillo", "descripcion": "", "categoria": "Iluminación"},
    ]

    def test_filters_by_token_and_returns_alphabetical(self):
        # Token 'cable' solo machea con "Cable 14 AWG"
        result = cs.filter_catalog(self.ITEMS, q="cable")
        self.assertEqual([item["nombre"] for item in result], ["Cable 14 AWG"])

    def test_multiple_tokens_must_all_match(self):
        # 'square 30' solo está en Interruptor (descripción + nombre)
        result = cs.filter_catalog(self.ITEMS, q="square 30")
        self.assertEqual([item["nombre"] for item in result], ["Interruptor termomagnético 30A"])

    def test_tokens_match_across_fields_including_category(self):
        # 'iluminacion' está sólo en categoría, sin acentos
        result = cs.filter_catalog(self.ITEMS, q="iluminacion")
        nombres = sorted(item["nombre"] for item in result)
        self.assertEqual(nombres, ["Apagador sencillo", "Foco LED 9W"])

    def test_filter_by_category(self):
        result = cs.filter_catalog(self.ITEMS, categoria="Iluminación")
        self.assertEqual(
            sorted(item["nombre"] for item in result),
            ["Apagador sencillo", "Foco LED 9W"],
        )

    def test_combined_tokens_and_category(self):
        result = cs.filter_catalog(self.ITEMS, q="led", categoria="Iluminación")
        self.assertEqual([item["nombre"] for item in result], ["Foco LED 9W"])

    def test_no_filters_returns_all_sorted(self):
        result = cs.filter_catalog(self.ITEMS)
        self.assertEqual(len(result), len(self.ITEMS))
        nombres = [item["nombre"] for item in result]
        self.assertEqual(nombres, sorted(nombres, key=str.lower))


class ListCategoriesTest(unittest.TestCase):
    def test_returns_unique_sorted_non_empty(self):
        items = [
            {"categoria": "Tableros"},
            {"categoria": "tableros"},  # duplicado por normalización
            {"categoria": "Iluminación"},
            {"categoria": ""},
            {},
            {"categoria": "Conductores"},
        ]
        result = cs.list_categories(items)
        # Conserva la primera capitalización vista por categoría única
        self.assertEqual(result, ["Conductores", "Iluminación", "Tableros"])


class ApiCatalogoTest(unittest.TestCase):
    """Smoke-test del endpoint JSON; no muta datos."""

    @classmethod
    def setUpClass(cls):
        from app import app
        cls.client = app.test_client()

    def test_api_returns_json_list(self):
        response = self.client.get("/api/catalogo")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)

    def test_api_accepts_query_parameters(self):
        # Sólo verificamos que acepte los params sin tronar y respete el shape
        response = self.client.get("/api/catalogo?q=interruptor%20cable&categoria=Tableros")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        # Cada resultado debe contener al menos los tokens en algún campo
        for item in data:
            blob = " ".join(
                str(item.get(field, "") or "")
                for field in ("nombre", "descripcion", "categoria")
            ).lower()
            self.assertIn("interruptor", blob)
            self.assertIn("cable", blob)

    def test_api_categorias_returns_sorted_list(self):
        response = self.client.get("/api/catalogo/categorias")
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIsInstance(data, list)
        # Si hay categorías, deben venir sin duplicados normalizados
        normalized = [c.lower() for c in data]
        self.assertEqual(len(normalized), len(set(normalized)))


if __name__ == "__main__":
    unittest.main()
