import unittest
from unittest.mock import patch


class CompanyConfigTest(unittest.TestCase):

    def test_returns_defaults_when_no_file(self):
        from tracker.company_config import get_company
        with patch("tracker.company_config._load", side_effect=Exception("no file")):
            result = get_company()
        self.assertEqual(result["name"], "Mi Empresa")
        self.assertIn("logo", result)
        self.assertIn("address", result)
        self.assertIn("email", result)
        self.assertIn("phone", result)
        self.assertIn("rut", result)

    def test_merges_stored_values_over_defaults(self):
        from tracker.company_config import get_company
        with patch("tracker.company_config._load", return_value={"name": "ACME Corp", "rut": "12345"}):
            result = get_company()
        self.assertEqual(result["name"], "ACME Corp")
        self.assertEqual(result["rut"], "12345")
        self.assertEqual(result["logo"], "")
        self.assertEqual(result["email"], "")
        self.assertEqual(result["phone"], "")

    def test_non_dict_storage_returns_defaults(self):
        from tracker.company_config import get_company
        with patch("tracker.company_config._load", return_value=["bad data"]):
            result = get_company()
        self.assertEqual(result["name"], "Mi Empresa")

    def test_save_company_calls_storage(self):
        from tracker.company_config import save_company
        with patch("tracker.company_config._save") as mock_save:
            save_company({"name": "Test"})
        mock_save.assert_called_once_with("company", {"name": "Test"})


class ProjectTemplatesTest(unittest.TestCase):

    def test_returns_defaults_when_no_file(self):
        from tracker.templates_config import get_project_templates
        with patch("tracker.templates_config._load", side_effect=Exception("no file")):
            result = get_project_templates()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)
        self.assertIn("stages", result[0])
        self.assertIn("id", result[0])

    def test_returns_defaults_when_empty_list(self):
        from tracker.templates_config import get_project_templates
        with patch("tracker.templates_config._load", return_value=[]):
            result = get_project_templates()
        self.assertGreater(len(result), 0)

    def test_returns_stored_templates(self):
        from tracker.templates_config import get_project_templates
        custom = [{"id": "custom", "name": "Custom", "stages": ["A", "B"]}]
        with patch("tracker.templates_config._load", return_value=custom):
            result = get_project_templates()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "custom")
        self.assertEqual(result[0]["stages"], ["A", "B"])

    def test_default_templates_have_stages_list(self):
        from tracker.templates_config import get_project_templates, DEFAULT_TEMPLATES
        for tmpl in DEFAULT_TEMPLATES:
            self.assertIn("id", tmpl)
            self.assertIn("stages", tmpl)
            self.assertIsInstance(tmpl["stages"], list)
            self.assertGreater(len(tmpl["stages"]), 0)

    def test_save_templates_calls_storage(self):
        from tracker.templates_config import save_project_templates
        with patch("tracker.templates_config._save") as mock_save:
            save_project_templates([{"id": "x"}])
        mock_save.assert_called_once_with("project_templates", [{"id": "x"}])


if __name__ == "__main__":
    unittest.main()
