"""Smoke tests for simplified project detail COT/LDM UI."""

from pathlib import Path
import unittest


class ProjectDetailBundleUITest(unittest.TestCase):
    def test_template_contains_simple_cot_ldm_summary(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("Resumen COT vs LDM", template)
        self.assertIn("COT base", template)
        self.assertIn("Extras activas", template)
        self.assertIn("Costo LDM", template)
        self.assertIn("Cobertura de catálogo", template)
        self.assertIn("Cotizaciones usadas", template)
        self.assertIn("LDM consideradas", template)
        self.assertIn("Imprimir resumen", template)
        self.assertNotIn("technicalConsistencyTable", template)
        self.assertNotIn("technicalConsistencyFilter", template)
        self.assertNotIn("Consistencia técnica por bundles", template)

    def test_materials_tab_exposes_csv_export_for_existing_ldms(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("url_for('ldm_csv'", template)
        self.assertIn("Exportar CSV de esta lista", template)
        self.assertIn("bi-filetype-csv", template)

    def test_materials_tab_exposes_assisted_bundle_sync_review(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("url_for('sync_ldm_bundles'", template)
        self.assertIn("Revisar faltantes desde bundles", template)
        self.assertIn("bi-magic", template)
        self.assertNotIn("Agregar faltantes desde bundles", template)
        self.assertNotIn("Completar LDM", template)


if __name__ == "__main__":
    unittest.main()
