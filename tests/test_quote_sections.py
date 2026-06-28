from pathlib import Path
import unittest

from tracker.catalog import hydrate_quote, quote_section_groups


class QuoteSectionsTest(unittest.TestCase):
    def test_quote_section_groups_preserve_contiguous_order(self):
        groups = quote_section_groups([
            {"description": "Tablero A", "section": "Tableros", "total": 100},
            {"description": "Sin sección", "section": "", "total": 50},
            {"description": "Tablero B", "section": "Tableros", "total": 75},
        ])

        self.assertEqual([group["name"] for group in groups], ["Tableros", "", "Tableros"])
        self.assertEqual([group["subtotal"] for group in groups], [100.0, 50.0, 75.0])

    def test_quote_section_groups_preserve_empty_section_markers(self):
        groups = quote_section_groups([
            {"kind": "section", "section": "Vestibulo"},
            {"kind": "section", "section": "Terraza"},
            {"description": "Salida", "section": "Terraza", "total": 120},
            {"kind": "section", "section": "Jardin"},
        ])

        self.assertEqual([group["name"] for group in groups], ["Vestibulo", "Terraza", "Jardin"])
        self.assertEqual([len(group["items"]) for group in groups], [0, 1, 0])
        self.assertEqual([group["subtotal"] for group in groups], [0.0, 120.0, 0.0])

    def test_hydrate_quote_keeps_section_markers_out_of_totals(self):
        quote = hydrate_quote({
            "tax_rate": 16,
            "items": [
                {"kind": "section", "section": "Vestibulo"},
                {"description": "Salida", "section": "Vestibulo", "qty": 2, "price": 100},
            ],
        })

        self.assertEqual(quote["subtotal"], 200.0)
        self.assertEqual(quote["sections"][0]["name"], "Vestibulo")
        self.assertEqual(len(quote["sections"][0]["items"]), 1)

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

    def test_quote_form_has_integrantes_editor(self):
        template = Path("templates/quote_project_form.html").read_text(encoding="utf-8")

        self.assertIn("Integrantes de la cotización", template)
        self.assertIn("toggleIntegranteBody", template)
        self.assertIn('name="integrante_{{ loop.index0 }}_name"', template)
        self.assertIn('name="integrante_{{ loop.index0 }}_role"', template)

    def test_quote_views_render_bundle_breakdown_without_price_columns(self):
        form_template = Path("templates/quote_project_form.html").read_text(encoding="utf-8")
        detail_template = Path("templates/quote_project_detail.html").read_text(encoding="utf-8")

        for template in (form_template, detail_template):
            self.assertIn("quote-bundle-includes", template)
            self.assertIn("item.bundle_breakdown", template)
            self.assertIn("<strong>Incluye:</strong>", template)
            self.assertIn("component.qty_display or component.qty", template)
            self.assertNotIn("component.price", template)
            self.assertNotIn("component.total", template)

    def test_quote_form_has_named_template_selector_and_catalog_application(self):
        template = Path("templates/quote_project_form.html").read_text(encoding="utf-8")

        self.assertIn('id="quoteTemplateSelect"', template)
        self.assertIn("QUOTE_TEMPLATES_BY_ID", template)
        self.assertIn("CATALOG_BY_ID", template)
        self.assertIn("applySelectedQuoteTemplate", template)
        self.assertIn("Artículo no encontrado en catálogo", template)

    def test_quote_templates_admin_edits_items_without_prices(self):
        template = Path("templates/quote_templates.html").read_text(encoding="utf-8")

        self.assertIn("template-search-input", template)
        self.assertIn("template-item-qty", template)
        self.assertIn("template-sections-json", template)
        self.assertIn("TEMPLATE_CATALOG", template)
        self.assertNotIn("item.precio", template)
        self.assertNotIn("unit_price", template)


if __name__ == "__main__":
    unittest.main()
