import unittest

from werkzeug.datastructures import MultiDict

from tracker.validators import validate_ldm_form, validate_project_form, validate_quote_form


class ValidatorsTest(unittest.TestCase):
    def test_project_requires_name_clave_scope_and_valid_short_date(self):
        result = validate_project_form(
            MultiDict({"name": "", "clave": "", "fecha": "2026-04-24"}),
            [],
            {"contactos"},
        )

        self.assertFalse(result["ok"])
        self.assertIn("El nombre del proyecto es requerido.", result["errors"])
        self.assertIn("La clave del proyecto es requerida.", result["errors"])
        self.assertIn("Selecciona al menos un alcance.", result["errors"])
        self.assertIn("La fecha del proyecto debe usar formato AAMMDD, por ejemplo 260424.", result["errors"])

    def test_quote_ignores_default_empty_row_but_requires_real_items(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_rate", "16"),
                ("currency", "MXN"),
                ("item_desc[]", ""),
                ("item_unit[]", "pza"),
                ("item_qty[]", "1"),
                ("item_price[]", "0"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["items"], [])
        self.assertEqual(result["errors"], ["Agrega al menos una partida a la cotización."])

    def test_quote_validates_numbers_and_tax_range(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_rate", "150"),
                ("currency", "MXN"),
                ("item_desc[]", "Interruptor"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "dos"),
                ("item_price[]", "-5"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertFalse(result["ok"])
        self.assertIn("IVA debe estar entre 0 y 100.", result["errors"])
        self.assertIn("Fila 1: cantidad debe ser un número válido.", result["errors"])
        self.assertIn("Fila 1: cantidad debe ser mayor a 0.", result["errors"])
        self.assertIn("Fila 1: precio unitario no puede ser negativo.", result["errors"])

    def test_quote_accepts_valid_item_and_computes_subtotal(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_rate", "16"),
                ("currency", "MXN"),
                ("project_basis_note", "Plano autorizado"),
                ("item_desc[]", "Interruptor"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "2"),
                ("item_price[]", "10.50"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["project_basis_note"], "Plano autorizado")
        self.assertEqual(result["subtotal"], 21.0)
        self.assertEqual(result["items"][0]["total"], 21.0)

    def test_quote_assigns_items_to_section_rows(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_rate", "16"),
                ("currency", "MXN"),
                ("item_kind[]", "section"),
                ("item_section[]", "Bodega de alcohol"),
                ("item_desc[]", ""),
                ("item_unit[]", ""),
                ("item_qty[]", ""),
                ("item_price[]", ""),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
                ("item_kind[]", "item"),
                ("item_section[]", ""),
                ("item_desc[]", "Salida eléctrica"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "2"),
                ("item_price[]", "750"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["items"][0]["section"], "Bodega de alcohol")
        self.assertEqual(result["subtotal"], 1500.0)

    def test_ldm_requires_supplier_and_real_items(self):
        result = validate_ldm_form(
            MultiDict([
                ("proveedor", ""),
                ("fecha", "2026-04-24"),
                ("item_desc[]", ""),
                ("item_unit[]", "pza"),
                ("item_qty[]", "1"),
                ("item_catalog_id[]", ""),
            ])
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["items"], [])
        self.assertIn("Proveedor es requerido.", result["errors"])
        self.assertIn("Agrega al menos un artículo a la lista de materiales.", result["errors"])

    def test_ldm_accepts_valid_item(self):
        result = validate_ldm_form(
            MultiDict([
                ("proveedor", "Proveedor Uno"),
                ("fecha", "2026-04-24"),
                ("item_desc[]", "Cable"),
                ("item_unit[]", "m"),
                ("item_qty[]", "12.5"),
                ("item_catalog_id[]", ""),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["items"][0]["qty"], 12.5)


if __name__ == "__main__":
    unittest.main()
