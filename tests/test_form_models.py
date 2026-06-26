import unittest

from werkzeug.datastructures import MultiDict

from tracker.form_models import ldm_from_form, quote_from_form


class FormModelsTest(unittest.TestCase):
    def test_quote_from_form_preserves_sections_and_items(self):
        result = quote_from_form(
            MultiDict([
                ("quote_type", "Extraordinaria"),
                ("quote_number", " COT-OM001-E01-20260428 "),
                ("version", " V2 "),
                ("date", "2026-04-28"),
                ("currency", "USD"),
                ("tax_rate", "8"),
                ("project_basis_note", " Plano base "),
                ("item_kind[]", "section"),
                ("item_section[]", "Tableros"),
                ("item_desc[]", ""),
                ("item_unit[]", ""),
                ("item_qty[]", ""),
                ("item_precio_costo[]", ""),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
                ("item_kind[]", "item"),
                ("item_section[]", ""),
                ("item_desc[]", " Interruptor "),
                ("item_unit[]", "pza"),
                ("item_qty[]", "2"),
                ("item_precio_costo[]", "150.5"),
                ("item_catalog_id[]", "ABC123"),
                ("item_desc2[]", "Detalle"),
            ])
        )

        self.assertEqual(result["quote_type"], "Extraordinaria")
        self.assertEqual(result["quote_number"], "COT-OM001-E01-20260428")
        self.assertEqual(result["items"][0], {"kind": "section", "section": "Tableros"})
        self.assertEqual(result["items"][1]["section"], "Tableros")
        self.assertEqual(result["items"][1]["precio_costo"], "150.5")
        self.assertEqual(result["items"][1]["catalog_item_id"], "ABC123")

    def test_quote_from_form_preserves_section_without_items(self):
        result = quote_from_form(
            MultiDict([
                ("date", "2026-04-28"),
                ("item_kind[]", "section"),
                ("item_section[]", "Vestibulo"),
                ("item_desc[]", ""),
                ("item_unit[]", ""),
                ("item_qty[]", ""),
                ("item_precio_costo[]", ""),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertEqual(result["items"], [{"kind": "section", "section": "Vestibulo"}])

    def test_quote_from_form_preserves_deleted_catalog_snapshot(self):
        result = quote_from_form(
            MultiDict([
                ("date", "2026-04-28"),
                ("item_desc[]", "Interruptor"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "1"),
                ("item_precio_costo[]", "100"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", "3P"),
                ("item_deleted_catalog_id[]", "CAT1"),
                ("item_deleted_catalog_nombre[]", "Interruptor"),
                ("item_deleted_catalog_descripcion[]", "3P"),
                ("item_deleted_catalog_unidad[]", "pza"),
                ("item_deleted_catalog_precio[]", "100"),
                ("item_deleted_catalog_deleted_at[]", "2026-04-28"),
            ])
        )

        self.assertEqual(result["items"][0]["catalog_item_id"], "")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["id"], "CAT1")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["precio"], 100.0)

    def test_quote_from_form_parses_specs(self):
        result = quote_from_form(
            MultiDict([
                ("date", "2026-04-28"),
                ("specs_condiciones_pago", "50% anticipo"),
                ("specs_exclusiones", "Sin materiales"),
                ("specs_validez", "30 días"),
                ("specs_forma_entrega", "PDF"),
                ("specs_contacto", "Ing. López"),
                ("item_desc[]", "Interruptor"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "1"),
                ("item_precio_costo[]", "100"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )
        self.assertEqual(result["specs"]["condiciones_pago"], "50% anticipo")
        self.assertEqual(result["specs"]["exclusiones"], "Sin materiales")
        self.assertEqual(result["specs"]["validez"], "30 días")
        self.assertEqual(result["specs"]["forma_entrega"], "PDF")
        self.assertEqual(result["specs"]["contacto"], "Ing. López")

    def test_quote_from_form_specs_defaults_to_empty_strings(self):
        result = quote_from_form(MultiDict([
            ("date", "2026-04-28"),
            ("item_desc[]", "X"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "1"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]))
        self.assertIn("specs", result)
        for field in ("condiciones_pago", "exclusiones", "validez", "forma_entrega", "contacto"):
            self.assertEqual(result["specs"][field], "")

    def test_ldm_from_form_preserves_fallback_and_items(self):
        result = ldm_from_form(
            MultiDict([
                ("proveedor", " Proveedor Uno "),
                ("fecha", "2026-04-28"),
                ("notes", " Requiere entrega parcial "),
                ("item_desc[]", " Cable "),
                ("item_unit[]", "m"),
                ("item_qty[]", "25"),
                ("item_catalog_id[]", "CAB001"),
            ]),
            fallback_ldm={"id": "LDM1", "ldm_number": "LDM-OM001-01"},
        )

        self.assertEqual(result["id"], "LDM1")
        self.assertEqual(result["ldm_number"], "LDM-OM001-01")
        self.assertEqual(result["proveedor"], "Proveedor Uno")
        self.assertEqual(result["items"][0]["description"], "Cable")
        self.assertEqual(result["items"][0]["qty"], "25")

    def test_ldm_from_form_preserves_deleted_catalog_snapshot(self):
        result = ldm_from_form(
            MultiDict([
                ("proveedor", "Proveedor Uno"),
                ("fecha", "2026-04-28"),
                ("item_desc[]", "Cable histórico"),
                ("item_unit[]", "m"),
                ("item_qty[]", "25"),
                ("item_catalog_id[]", ""),
                ("item_deleted_catalog_id[]", "CAT9"),
                ("item_deleted_catalog_nombre[]", "Cable"),
                ("item_deleted_catalog_descripcion[]", "THW"),
                ("item_deleted_catalog_unidad[]", "m"),
                ("item_deleted_catalog_precio[]", "12.5"),
                ("item_deleted_catalog_deleted_at[]", "2026-04-28"),
            ])
        )

        self.assertEqual(result["items"][0]["catalog_item_id"], "")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["id"], "CAT9")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["precio"], 12.5)


if __name__ == "__main__":
    unittest.main()
