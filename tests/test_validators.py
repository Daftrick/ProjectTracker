import unittest

from werkzeug.datastructures import MultiDict

from tracker.validators import validate_ldm_form, validate_project_form, validate_quote_form


class ValidatorsTest(unittest.TestCase):
    def test_project_requires_name_and_clave(self):
        result = validate_project_form(
            MultiDict({"name": "", "clave": ""}),
        )

        self.assertFalse(result["ok"])
        self.assertIn("El nombre del proyecto es requerido.", result["errors"])
        self.assertIn("La clave del proyecto es requerida.", result["errors"])
        self.assertEqual(result["field_errors"]["name"], "El nombre del proyecto es requerido.")
        self.assertEqual(result["field_errors"]["clave"], "La clave del proyecto es requerida.")

    def test_quote_ignores_default_empty_row_but_requires_real_items(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_enabled", "on"),
                ("currency", "MXN"),
                ("item_desc[]", ""),
                ("item_unit[]", "pza"),
                ("item_qty[]", "1"),
                ("item_precio_costo[]", "0"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertFalse(result["ok"])
        self.assertEqual(result["items"], [])
        self.assertEqual(result["errors"], ["Agrega al menos una partida o sección a la cotización."])

    def test_quote_validates_numbers(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_enabled", "on"),
                ("currency", "MXN"),
                ("item_desc[]", "Interruptor"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "dos"),
                ("item_precio_costo[]", "-5"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertFalse(result["ok"])
        self.assertIn("Fila 1: cantidad debe ser un número válido.", result["errors"])
        self.assertIn("Fila 1: cantidad debe ser mayor a 0.", result["errors"])
        self.assertIn("Fila 1: costo unitario no puede ser negativo.", result["errors"])
        self.assertEqual(result["field_errors"]["items"], "Revisa las partidas marcadas por la validación.")

    def test_quote_tax_rate_is_toggle_not_free_number(self):
        # El IVA ya no se edita como número libre: sólo se activa/desactiva
        # con tax_enabled. Cualquier valor de tax_rate en el form se ignora.
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]

        on_result = validate_quote_form(MultiDict(base_fields + [("tax_enabled", "on")]))
        self.assertEqual(on_result["tax_rate"], 16)

        off_result = validate_quote_form(MultiDict(base_fields))
        self.assertEqual(off_result["tax_rate"], 0.0)

        # Un tax_rate arbitrario en el POST no tiene ningún efecto.
        tampered_result = validate_quote_form(MultiDict(base_fields + [("tax_rate", "999")]))
        self.assertEqual(tampered_result["tax_rate"], 0.0)

    def test_quote_discount_pct_parsed_and_range_validated(self):
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]

        no_discount = validate_quote_form(MultiDict(base_fields))
        self.assertEqual(no_discount["discount_pct"], 0.0)

        with_discount = validate_quote_form(MultiDict(base_fields + [("discount_pct", "15")]))
        self.assertTrue(with_discount["ok"])
        self.assertEqual(with_discount["discount_pct"], 15.0)

        out_of_range = validate_quote_form(MultiDict(base_fields + [("discount_pct", "150")]))
        self.assertFalse(out_of_range["ok"])
        self.assertIn("Descuento debe estar entre 0 y 100.", out_of_range["errors"])
        self.assertEqual(out_of_range["field_errors"]["discount_pct"], "Descuento debe estar entre 0 y 100.")

    def test_quote_client_unchanged_from_project_yields_no_override(self):
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]
        project = {"client": "Cliente Original"}

        # Campo igual al del proyecto (el editor lo precarga así): sin override.
        same = validate_quote_form(MultiDict(base_fields + [("client", "Cliente Original")]), project)
        self.assertEqual(same["client_override"], "")

        # Campo vacío: tampoco hay override, sigue sincronizado.
        blank = validate_quote_form(MultiDict(base_fields + [("client", "")]), project)
        self.assertEqual(blank["client_override"], "")

    def test_quote_client_changed_yields_override(self):
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]
        project = {"client": "Cliente Original"}
        result = validate_quote_form(
            MultiDict(base_fields + [("client", "Cliente Nuevo Editado")]), project
        )
        self.assertEqual(result["client_override"], "Cliente Nuevo Editado")

    def test_quote_client_override_without_project_context(self):
        # Sin project (ej. llamadas legacy/tests), cualquier texto no vacío es override.
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]
        result = validate_quote_form(MultiDict(base_fields + [("client", "Cualquier Cliente")]))
        self.assertEqual(result["client_override"], "Cualquier Cliente")

    def test_quote_proposal_for_defaults_to_cliente_when_absent(self):
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]
        result = validate_quote_form(MultiDict(base_fields))
        self.assertEqual(result["proposal_for_mode"], "cliente")
        self.assertEqual(result["proposal_for_custom"], "")

    def test_quote_proposal_for_personalizado_requires_custom_text(self):
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]
        missing = validate_quote_form(MultiDict(base_fields + [("proposal_for_mode", "personalizado")]))
        self.assertFalse(missing["ok"])
        self.assertIn("proposal_for_custom", missing["field_errors"])

        filled = validate_quote_form(MultiDict(base_fields + [
            ("proposal_for_mode", "personalizado"),
            ("proposal_for_custom", "Arq. Juan Pérez"),
        ]))
        self.assertTrue(filled["ok"])
        self.assertEqual(filled["proposal_for_mode"], "personalizado")
        self.assertEqual(filled["proposal_for_custom"], "Arq. Juan Pérez")

    def test_quote_proposal_for_vacio_is_respected(self):
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]
        result = validate_quote_form(MultiDict(base_fields + [("proposal_for_mode", "")]))
        self.assertTrue(result["ok"])
        self.assertEqual(result["proposal_for_mode"], "")

    def test_quote_proposal_for_invalid_mode_falls_back_to_cliente(self):
        base_fields = [
            ("date", "2026-04-24"),
            ("currency", "MXN"),
            ("item_desc[]", "Interruptor"),
            ("item_unit[]", "pza"),
            ("item_qty[]", "1"),
            ("item_precio_costo[]", "100"),
            ("item_catalog_id[]", ""),
            ("item_desc2[]", ""),
        ]
        result = validate_quote_form(MultiDict(base_fields + [("proposal_for_mode", "algo-raro")]))
        self.assertEqual(result["proposal_for_mode"], "cliente")

    def test_quote_accepts_valid_item_and_computes_subtotal(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_enabled", "on"),
                ("currency", "MXN"),
                ("project_basis_note", "Plano autorizado"),
                ("item_desc[]", "Interruptor"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "2"),
                ("item_precio_costo[]", "10.50"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["project_basis_note"], "Plano autorizado")
        self.assertEqual(result["subtotal"], 21.0)
        self.assertEqual(result["items"][0]["precio_costo"], 10.50)

    def test_quote_parses_integrantes(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_enabled", "on"),
                ("currency", "MXN"),
                ("integrante_0_enabled", "1"),
                ("integrante_0_name", "Ana López"),
                ("integrante_0_role", "Directora"),
                ("integrante_1_name", "Luis Pérez"),
                ("integrante_1_role", "Gerente"),
                ("item_desc[]", "Interruptor"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "1"),
                ("item_precio_costo[]", "10.50"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["specs"]["integrantes"][0], {
            "enabled": True,
            "name": "Ana López",
            "role": "Directora",
        })
        self.assertFalse(result["specs"]["integrantes"][1]["enabled"])
        self.assertEqual(result["specs"]["integrantes"][1]["name"], "Luis Pérez")
        self.assertEqual(result["specs"]["integrantes"][1]["role"], "Gerente")

    def test_quote_preserves_deleted_catalog_snapshot(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_enabled", "on"),
                ("currency", "MXN"),
                ("item_desc[]", "Interruptor histórico"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "2"),
                ("item_precio_costo[]", "10.50"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", "Detalle"),
                ("item_deleted_catalog_id[]", "CAT1"),
                ("item_deleted_catalog_nombre[]", "Interruptor"),
                ("item_deleted_catalog_descripcion[]", "Detalle"),
                ("item_deleted_catalog_unidad[]", "pza"),
                ("item_deleted_catalog_precio[]", "10.50"),
                ("item_deleted_catalog_deleted_at[]", "2026-04-28"),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["items"][0]["catalog_item_id"], "")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["id"], "CAT1")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["precio"], 10.5)

    def test_quote_assigns_items_to_section_rows(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_enabled", "on"),
                ("currency", "MXN"),
                ("item_kind[]", "section"),
                ("item_section[]", "Bodega de alcohol"),
                ("item_desc[]", ""),
                ("item_unit[]", ""),
                ("item_qty[]", ""),
                ("item_precio_costo[]", ""),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
                ("item_kind[]", "item"),
                ("item_section[]", ""),
                ("item_desc[]", "Salida eléctrica"),
                ("item_unit[]", "pza"),
                ("item_qty[]", "2"),
                ("item_precio_costo[]", "750"),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["items"][0], {"kind": "section", "section": "Bodega de alcohol"})
        self.assertEqual(result["items"][1]["section"], "Bodega de alcohol")
        self.assertEqual(result["subtotal"], 1500.0)

    def test_quote_allows_section_without_items(self):
        result = validate_quote_form(
            MultiDict([
                ("date", "2026-04-24"),
                ("tax_enabled", "on"),
                ("currency", "MXN"),
                ("item_kind[]", "section"),
                ("item_section[]", "Areas exteriores"),
                ("item_desc[]", ""),
                ("item_unit[]", ""),
                ("item_qty[]", ""),
                ("item_precio_costo[]", ""),
                ("item_catalog_id[]", ""),
                ("item_desc2[]", ""),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["items"], [{"kind": "section", "section": "Areas exteriores"}])
        self.assertEqual(result["subtotal"], 0.0)

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
        self.assertEqual(result["field_errors"]["proveedor"], "Proveedor es requerido.")
        self.assertEqual(result["field_errors"]["items"], "Agrega al menos un artículo a la lista de materiales.")

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

    def test_ldm_preserves_deleted_catalog_snapshot(self):
        result = validate_ldm_form(
            MultiDict([
                ("proveedor", "Proveedor Uno"),
                ("fecha", "2026-04-24"),
                ("item_desc[]", "Cable histórico"),
                ("item_unit[]", "m"),
                ("item_qty[]", "12.5"),
                ("item_catalog_id[]", ""),
                ("item_deleted_catalog_id[]", "CAT9"),
                ("item_deleted_catalog_nombre[]", "Cable"),
                ("item_deleted_catalog_descripcion[]", "THW"),
                ("item_deleted_catalog_unidad[]", "m"),
                ("item_deleted_catalog_precio[]", "12.5"),
                ("item_deleted_catalog_deleted_at[]", "2026-04-28"),
            ])
        )

        self.assertTrue(result["ok"])
        self.assertEqual(result["items"][0]["catalog_item_id"], "")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["id"], "CAT9")
        self.assertEqual(result["items"][0]["deleted_catalog_item"]["precio"], 12.5)


if __name__ == "__main__":
    unittest.main()
