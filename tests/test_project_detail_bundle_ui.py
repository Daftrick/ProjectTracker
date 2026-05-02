"""Smoke tests for the bundle technical consistency UI in project_detail.html."""

from pathlib import Path
import unittest


class ProjectDetailBundleUITest(unittest.TestCase):
    def test_template_contains_bundle_technical_consistency_section(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("Consistencia técnica por bundles", template)
        self.assertIn("technicalConsistencyTable", template)
        self.assertIn("technicalConsistencyFilter", template)
        self.assertIn("cn.bundle_consistency", template)
        self.assertIn("Materiales evaluados", template)


if __name__ == "__main__":
    unittest.main()
