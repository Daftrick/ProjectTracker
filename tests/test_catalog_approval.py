import unittest

from tracker.catalog import (
    APPROVAL_ACTIVE,
    APPROVAL_DRAFT,
    APPROVAL_OBSOLETE,
    approve_quote,
    is_base_quote_type,
    migrate_quote_approval,
    next_quote_number,
    quote_type_code,
    quote_type_has_quantities,
)


def _q(qid, project_id, qtype, status=None, date="2026-01-01", created_at="2026-01-01"):
    q = {"id": qid, "project_id": project_id, "quote_type": qtype, "date": date, "created_at": created_at}
    if status is not None:
        q["approval_status"] = status
    return q


class ApproveQuoteTest(unittest.TestCase):
    def test_approving_proyecto_does_not_affect_obra_or_servicio(self):
        quotes = [
            _q("p1", "proj", "Proyecto", APPROVAL_DRAFT),
            _q("o1", "proj", "Obra", APPROVAL_ACTIVE),
            _q("s1", "proj", "Servicio", APPROVAL_ACTIVE),
        ]
        approve_quote("p1", quotes)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["p1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["o1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["s1"]["approval_status"], APPROVAL_ACTIVE)

    def test_approving_proyecto_does_not_obsolete_other_proyecto(self):
        # Aprobación libre: varias cotizaciones del MISMO tipo pueden quedar
        # activas a la vez; aprobar una no toca a las demás.
        quotes = [
            _q("p1", "proj", "Proyecto", APPROVAL_ACTIVE),
            _q("p2", "proj", "Proyecto", APPROVAL_DRAFT),
        ]
        approve_quote("p2", quotes)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["p1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["p2"]["approval_status"], APPROVAL_ACTIVE)

    def test_approving_extraordinaria_toggles_only_itself(self):
        quotes = [
            _q("e1", "proj", "Extraordinaria", APPROVAL_DRAFT),
            _q("p1", "proj", "Proyecto", APPROVAL_ACTIVE),
        ]
        approve_quote("e1", quotes)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["e1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["p1"]["approval_status"], APPROVAL_ACTIVE)

    def test_approving_obra_does_not_affect_proyecto_or_other_obra(self):
        quotes = [
            _q("p1", "proj", "Proyecto", APPROVAL_ACTIVE),
            _q("o1", "proj", "Obra", APPROVAL_DRAFT),
            _q("o2", "proj", "Obra", APPROVAL_ACTIVE),
        ]
        approve_quote("o1", quotes)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["p1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["o1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["o2"]["approval_status"], APPROVAL_ACTIVE)

    def test_approving_active_base_quote_toggles_it_off(self):
        # Igual que las extraordinarias: aprobar una cotización base ya activa
        # la regresa a obsolete (toggle libre, sin excepción por tipo).
        quotes = [_q("p1", "proj", "Proyecto", APPROVAL_ACTIVE)]
        approve_quote("p1", quotes)
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_OBSOLETE)

    def test_approve_does_not_touch_other_project(self):
        quotes = [
            _q("p1", "proj1", "Proyecto", APPROVAL_DRAFT),
            _q("p2", "proj2", "Proyecto", APPROVAL_ACTIVE),
        ]
        approve_quote("p1", quotes)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["p2"]["approval_status"], APPROVAL_ACTIVE)


class MigrateQuoteApprovalTest(unittest.TestCase):
    def test_each_type_migrates_independently(self):
        quotes = [
            _q("p1", "proj", "Proyecto", date="2026-01-01"),
            _q("o1", "proj", "Obra", date="2026-02-01"),
            _q("s1", "proj", "Servicio", date="2026-03-01"),
        ]
        changed = migrate_quote_approval(quotes)
        self.assertTrue(changed)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["p1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["o1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["s1"]["approval_status"], APPROVAL_ACTIVE)

    def test_two_proyecto_quotes_only_newest_active(self):
        quotes = [
            _q("p1", "proj", "Proyecto", date="2026-01-01"),
            _q("p2", "proj", "Proyecto", date="2026-06-01"),
        ]
        migrate_quote_approval(quotes)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["p1"]["approval_status"], APPROVAL_OBSOLETE)
        self.assertEqual(by_id["p2"]["approval_status"], APPROVAL_ACTIVE)

    def test_extraordinaria_always_active(self):
        quotes = [
            _q("e1", "proj", "Extraordinaria"),
            _q("e2", "proj", "Extraordinaria"),
        ]
        migrate_quote_approval(quotes)
        for q in quotes:
            self.assertEqual(q["approval_status"], APPROVAL_ACTIVE)

    def test_already_has_status_not_touched(self):
        quotes = [
            _q("p1", "proj", "Proyecto", status=APPROVAL_OBSOLETE, date="2026-06-01"),
        ]
        changed = migrate_quote_approval(quotes)
        self.assertFalse(changed)
        self.assertEqual(quotes[0]["approval_status"], APPROVAL_OBSOLETE)


class NextQuoteNumberTest(unittest.TestCase):
    def _project(self):
        return {"id": "proj", "clave": "OM001"}

    def test_no_collision_preliminar_then_proyecto(self):
        project = self._project()
        existing = [
            {"project_id": "proj", "quote_type": "Preliminar", "quote_number": "COT-OM001-P01-20260101"},
        ]
        number = next_quote_number(project, existing, "Proyecto", "2026-06-18")
        self.assertIn("P02", number)

    def test_first_proyecto_in_clean_project(self):
        project = self._project()
        number = next_quote_number(project, [], "Proyecto", "2026-06-18")
        self.assertIn("P01", number)

    def test_obra_independent_counter(self):
        project = self._project()
        existing = [
            {"project_id": "proj", "quote_type": "Proyecto", "quote_number": "COT-OM001-P01-20260101"},
        ]
        number = next_quote_number(project, existing, "Obra", "2026-06-18")
        self.assertIn("O01", number)

    def test_servicio_counter(self):
        project = self._project()
        number = next_quote_number(project, [], "Servicio", "2026-06-18")
        self.assertIn("S01", number)

    def test_does_not_count_other_project_quotes(self):
        project = self._project()
        other = [{"project_id": "OTHER", "quote_type": "Proyecto"}]
        number = next_quote_number(project, other, "Proyecto", "2026-06-18")
        self.assertIn("P01", number)

    def test_proyecto_ejecutivo_counter(self):
        project = self._project()
        number = next_quote_number(project, [], "Proyecto Ejecutivo", "2026-06-18")
        self.assertIn("J01", number)


class ProyectoEjecutivoQuoteTypeTest(unittest.TestCase):
    def test_code_is_j_and_distinct_from_proyecto(self):
        self.assertEqual(quote_type_code("Proyecto Ejecutivo"), "J")
        self.assertNotEqual(quote_type_code("Proyecto Ejecutivo"), quote_type_code("Proyecto"))

    def test_has_no_quantities(self):
        self.assertFalse(quote_type_has_quantities("Proyecto Ejecutivo"))
        self.assertTrue(quote_type_has_quantities("Proyecto"))
        self.assertTrue(quote_type_has_quantities("Obra"))
        self.assertTrue(quote_type_has_quantities("Servicio"))

    def test_is_a_base_quote_type(self):
        self.assertTrue(is_base_quote_type("Proyecto Ejecutivo"))

    def test_approving_does_not_affect_other_types(self):
        quotes = [
            _q("je1", "proj", "Proyecto Ejecutivo", APPROVAL_DRAFT),
            _q("p1", "proj", "Proyecto", APPROVAL_ACTIVE),
        ]
        approve_quote("je1", quotes)
        by_id = {q["id"]: q for q in quotes}
        self.assertEqual(by_id["je1"]["approval_status"], APPROVAL_ACTIVE)
        self.assertEqual(by_id["p1"]["approval_status"], APPROVAL_ACTIVE)


if __name__ == "__main__":
    unittest.main()
