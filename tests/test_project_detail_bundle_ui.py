"""Smoke tests for the bundle technical consistency UI in project_detail.html."""

from pathlib import Path
import unittest


class ProjectDetailBundleUITest(unittest.TestCase):
    def test_template_contains_bundle_technical_consistency_section(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("Consistencia técnica por bundles", template)
        self.assertIn("technicalConsistencyTable", template)
        self.assertIn("technicalConsistencyFilter", template)
        self.assertIn("cv.technical", template)
        self.assertIn("Materiales evaluados", template)

    def test_materials_tab_exposes_csv_export_for_existing_ldms(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("url_for('ldm_csv'", template)
        self.assertIn("Exportar CSV de esta lista", template)
        self.assertIn("bi-filetype-csv", template)

    def test_materials_tab_exposes_partial_bundle_sync(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("url_for('sync_ldm_bundles'", template)
        self.assertIn("Agregar faltantes desde bundles", template)
        self.assertIn("Completar LDM", template)


if __name__ == "__main__":
    unittest.main()
