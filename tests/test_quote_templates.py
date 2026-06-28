import unittest
from unittest.mock import patch


class QuoteTemplatesConfigTest(unittest.TestCase):

    def test_returns_all_types_when_no_file(self):
        from tracker.quote_templates_config import get_quote_templates
        with patch("tracker.quote_templates_config._load", side_effect=Exception("no file")):
            result = get_quote_templates()
        self.assertIn("Proyecto", result)
        self.assertIn("Obra", result)
        self.assertIn("Servicio", result)

    def test_default_structure_has_required_fields(self):
        from tracker.quote_templates_config import get_quote_templates
        with patch("tracker.quote_templates_config._load", side_effect=Exception("no file")):
            result = get_quote_templates()
        for qtype in ("Proyecto", "Obra", "Servicio"):
            self.assertEqual(len(result[qtype]), 1)
            tmpl = result[qtype][0]
            self.assertIn("id", tmpl)
            self.assertIn("name", tmpl)
            self.assertIn("sections_default", tmpl)
            self.assertIn("terms_default", tmpl)
            self.assertIn("contacts_default", tmpl)
            self.assertNotIn("notes_default", tmpl)
            self.assertNotIn("specs_default", tmpl)
            self.assertIsInstance(tmpl["sections_default"], list)
            self.assertIsInstance(tmpl["terms_default"], list)
            self.assertIsInstance(tmpl["contacts_default"], list)
            self.assertEqual(len(tmpl["contacts_default"]), 4)
            self.assertTrue(all("key" in term for term in tmpl["terms_default"]))
            self.assertTrue(all("body" in term for term in tmpl["terms_default"]))
            self.assertTrue(all("enabled" in term for term in tmpl["terms_default"]))
            self.assertTrue(all("enabled" in contact for contact in tmpl["contacts_default"]))
            self.assertTrue(all("name" in contact for contact in tmpl["contacts_default"]))
            self.assertTrue(all("role" in contact for contact in tmpl["contacts_default"]))

    def test_migrates_legacy_dict_and_sections_to_named_list(self):
        from tracker.quote_templates_config import get_quote_templates
        stored = {
            "Proyecto": {
                "sections_default": ["Iluminación", "Contactos"],
                "notes_default": "Nota de prueba",
                "specs_default": {"condiciones_pago": "50% anticipo"},
                "terms_default": [
                    {
                        "key": "vigencia",
                        "title": "Vigencia.",
                        "body": "Vigencia personalizada",
                        "enabled": False,
                    }
                ],
                "contacts_default": [
                    {"enabled": True, "name": "Ana Lopez", "role": "Directora"},
                ],
            }
        }
        with patch("tracker.quote_templates_config._load", return_value=stored):
            result = get_quote_templates()
        tmpl = result["Proyecto"][0]
        self.assertEqual(tmpl["name"], "Proyecto")
        self.assertEqual(tmpl["sections_default"], [
            {"name": "Iluminación", "items": []},
            {"name": "Contactos", "items": []},
        ])
        self.assertNotIn("notes_default", tmpl)
        self.assertNotIn("specs_default", tmpl)
        self.assertEqual(tmpl["terms_default"][0]["body"], "Vigencia personalizada")
        self.assertEqual(tmpl["terms_default"][0]["title"], "Vigencia")
        self.assertFalse(tmpl["terms_default"][0]["enabled"])
        self.assertGreater(len(tmpl["terms_default"]), 1)
        self.assertEqual(tmpl["contacts_default"][0]["name"], "Ana Lopez")
        self.assertEqual(tmpl["contacts_default"][0]["role"], "Directora")
        self.assertTrue(tmpl["contacts_default"][0]["enabled"])
        self.assertEqual(tmpl["contacts_default"][1]["name"], "")
        self.assertFalse(tmpl["contacts_default"][1]["enabled"])

    def test_normalizes_template_items_without_prices(self):
        from tracker.quote_templates_config import get_quote_templates
        stored = {
            "Proyecto": [
                {
                    "id": "tmpl-1",
                    "name": "Completo",
                    "sections_default": [
                        {
                            "name": "Diseño",
                            "items": [
                                {
                                    "catalog_item_id": "CAT-1",
                                    "description": "Proyecto IE",
                                    "unit": "m2",
                                    "qty": "2.5",
                                    "unit_price": 999,
                                },
                                {"description": "sin id", "qty": 1},
                            ],
                        }
                    ],
                }
            ]
        }
        with patch("tracker.quote_templates_config._load", return_value=stored):
            tmpl = get_quote_templates()["Proyecto"][0]
        item = tmpl["sections_default"][0]["items"][0]
        self.assertEqual(item["catalog_item_id"], "CAT-1")
        self.assertEqual(item["qty"], 2.5)
        self.assertNotIn("unit_price", item)
        self.assertEqual(len(tmpl["sections_default"][0]["items"]), 1)

    def test_non_dict_storage_returns_defaults(self):
        from tracker.quote_templates_config import get_quote_templates
        with patch("tracker.quote_templates_config._load", return_value=["bad"]):
            result = get_quote_templates()
        self.assertIn("Proyecto", result)
        self.assertIsInstance(result["Proyecto"][0]["sections_default"], list)

    def test_save_normalizes_before_storage(self):
        from tracker.quote_templates_config import save_quote_templates
        with patch("tracker.quote_templates_config._save") as mock_save:
            save_quote_templates({"Proyecto": {"sections_default": ["Sección A"]}})
        saved = mock_save.call_args.args[1]
        self.assertEqual(mock_save.call_args.args[0], "quote_templates")
        self.assertEqual(saved["Proyecto"][0]["sections_default"], [{"name": "Sección A", "items": []}])

    def test_get_template_for_type_returns_first_template(self):
        from tracker.quote_templates_config import get_template_for_type
        stored = {
            "Proyecto": [
                {
                    "id": "one",
                    "name": "Primera",
                    "sections_default": ["Sección A"],
                    "terms_default": [],
                    "contacts_default": [],
                }
            ]
        }
        with patch("tracker.quote_templates_config._load", return_value=stored):
            result = get_template_for_type("Proyecto")
        self.assertEqual(result["sections_default"], [{"name": "Sección A", "items": []}])

    def test_get_template_by_id(self):
        from tracker.quote_templates_config import get_template_by_id
        stored = {
            "Proyecto": [
                {"id": "one", "name": "Primera"},
                {"id": "two", "name": "Segunda"},
            ]
        }
        with patch("tracker.quote_templates_config._load", return_value=stored):
            result = get_template_by_id("Proyecto", "two")
        self.assertEqual(result["name"], "Segunda")

    def test_get_template_for_unknown_type_returns_empty(self):
        from tracker.quote_templates_config import get_template_for_type
        with patch("tracker.quote_templates_config._load", side_effect=Exception("no file")):
            result = get_template_for_type("TipoInexistente")
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
