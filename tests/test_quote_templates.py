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
            tmpl = result[qtype]
            self.assertIn("sections_default", tmpl)
            self.assertIn("notes_default", tmpl)
            self.assertIn("specs_default", tmpl)
            self.assertIn("terms_default", tmpl)
            self.assertIsInstance(tmpl["sections_default"], list)
            self.assertIsInstance(tmpl["specs_default"], dict)
            self.assertIsInstance(tmpl["terms_default"], list)
            for field in ("condiciones_pago", "exclusiones", "validez", "forma_entrega", "contacto"):
                self.assertIn(field, tmpl["specs_default"])
            self.assertTrue(all("key" in term for term in tmpl["terms_default"]))
            self.assertTrue(all("body" in term for term in tmpl["terms_default"]))
            self.assertTrue(all("enabled" in term for term in tmpl["terms_default"]))

    def test_merges_stored_sections_over_defaults(self):
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
            }
        }
        with patch("tracker.quote_templates_config._load", return_value=stored):
            result = get_quote_templates()
        self.assertEqual(result["Proyecto"]["sections_default"], ["Iluminación", "Contactos"])
        self.assertEqual(result["Proyecto"]["notes_default"], "Nota de prueba")
        self.assertEqual(result["Proyecto"]["specs_default"]["condiciones_pago"], "50% anticipo")
        self.assertEqual(result["Proyecto"]["specs_default"]["validez"], "30 días naturales")
        self.assertEqual(result["Proyecto"]["terms_default"][0]["body"], "Vigencia personalizada")
        self.assertFalse(result["Proyecto"]["terms_default"][0]["enabled"])
        self.assertGreater(len(result["Proyecto"]["terms_default"]), 1)

    def test_non_dict_storage_returns_defaults(self):
        from tracker.quote_templates_config import get_quote_templates
        with patch("tracker.quote_templates_config._load", return_value=["bad"]):
            result = get_quote_templates()
        self.assertIn("Proyecto", result)
        self.assertIsInstance(result["Proyecto"]["sections_default"], list)

    def test_save_calls_storage(self):
        from tracker.quote_templates_config import save_quote_templates
        with patch("tracker.quote_templates_config._save") as mock_save:
            save_quote_templates({"Proyecto": {}})
        mock_save.assert_called_once_with("quote_templates", {"Proyecto": {}})

    def test_get_template_for_type(self):
        from tracker.quote_templates_config import get_template_for_type
        stored = {
            "Proyecto": {
                "sections_default": ["Sección A"],
                "notes_default": "",
                "specs_default": {},
                "terms_default": [],
            }
        }
        with patch("tracker.quote_templates_config._load", return_value=stored):
            result = get_template_for_type("Proyecto")
        self.assertEqual(result["sections_default"], ["Sección A"])

    def test_get_template_for_unknown_type_returns_empty(self):
        from tracker.quote_templates_config import get_template_for_type
        with patch("tracker.quote_templates_config._load", side_effect=Exception("no file")):
            result = get_template_for_type("TipoInexistente")
        self.assertEqual(result, {})


if __name__ == "__main__":
    unittest.main()
