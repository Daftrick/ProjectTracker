from pathlib import Path
import unittest

from tracker.catalog import quote_section_groups


class QuoteSectionsTest(unittest.TestCase):
    def test_quote_section_groups_preserve_contiguous_order(self):
        groups = quote_section_groups([
            {"description": "Tablero A", "section": "Tableros", "total": 100},
            {"description": "Sin sección", "section": "", "total": 50},
            {"description": "Tablero B", "section": "Tableros", "total": 75},
        ])

        self.assertEqual([group["name"] for group in groups], ["Tableros", "", "Tableros"])
        self.assertEqual([group["subtotal"] for group in groups], [100.0, 50.0, 75.0])

    def test_quote_form_rebuilds_repeated_section_headers(self):
        template = Path("templates/quote_project_form.html").read_text(encoding="utf-8")

        self.assertIn("{% set section_ns.current = item_section %}", template)
        self.assertIn("function sectionBlockRows(sectionRow)", template)
        self.assertIn("function draggableRowsFor(row)", template)
        self.assertIn("insertRowsBefore(tbody, draggingRows, anchorForDropTarget(target));", template)

    def test_quote_form_has_quick_copy_to_selected_section(self):
        template = Path("templates/quote_project_form.html").read_text(encoding="utf-8")

        self.assertIn('onclick="copySelectedToSection()"', template)
        self.assertIn("function copySelectedToSection()", template)
        self.assertIn("openCopyToMultiModal()", template)


if __name__ == "__main__":
    unittest.main()
