"""Pruebas para tracker.consistency.

Cubre:
    - clasificación de margen (umbrales 30 % / 0 %)
    - selección de cotización activa (General más reciente)
    - agregación de items por catalog_item_id en COT y LDM (varias LDMs)
    - detección de issues por artículo
    - escenarios extremos (sin COT, sin LDM, sólo unlinked)
"""

import unittest

from tracker import consistency as cn


PROJECT = {"id": "P1", "clave": "OM001"}


def _quote(quote_id, qtype, date, items, project_id="P1", subtotal=None, created_at=""):
    items = list(items)
    sub = subtotal if subtotal is not None else round(sum(i.get("total", 0) for i in items), 2)
    return {
        "id": quote_id,
        "project_id": project_id,
        "quote_number": f"COT-X-{quote_id}",
        "quote_type": qtype,
        "date": date,
        "created_at": created_at or date,
        "items": items,
        "subtotal": sub,
        "total": sub,
    }


def _q_item(catalog_item_id, qty, price, description="x", unit="pza"):
    return {
        "catalog_item_id": catalog_item_id,
        "description": description,
        "unit": unit,
        "qty": qty,
        "price": price,
        "total": round(qty * price, 2),
    }


def _ldm(ldm_id, items, ldm_number=None, project_id="P1"):
    items = list(items)
    subtotal = round(sum(i.get("total_cot", 0) for i in items), 2)
    return {
        "id": ldm_id,
        "project_id": project_id,
        "ldm_number": ldm_number or f"LDM-{ldm_id}",
        "items": items,
        "subtotal_cot": subtotal,
    }


def _l_item(catalog_item_id, qty, precio_cot, description="x", unit="pza"):
    return {
        "catalog_item_id": catalog_item_id,
        "description": description,
        "unit": unit,
        "qty": qty,
        "precio_cot": precio_cot,
        "total_cot": round(qty * precio_cot, 2),
    }


class ClassifyMarginTest(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual(cn.classify_margin(None), "no_data")
        self.assertEqual(cn.classify_margin(-1), "critical")
        self.assertEqual(cn.classify_margin(0), "warning")
        self.assertEqual(cn.classify_margin(15), "warning")
        self.assertEqual(cn.classify_margin(29.9), "warning")
        self.assertEqual(cn.classify_margin(30), "ok")
        self.assertEqual(cn.classify_margin(50), "ok")


class PickActiveQuoteTest(unittest.TestCase):
    def test_picks_most_recent_general(self):
        q1 = _quote("A", "General", "2026-01-01", [], created_at="2026-01-01")
        q2 = _quote("B", "General", "2026-03-01", [], created_at="2026-03-01")
        q3 = _quote("C", "Preliminar", "2026-04-01", [], created_at="2026-04-01")
        active = cn.pick_active_quote([q1, q2, q3])
        self.assertEqual(active["id"], "B")

    def test_falls_back_to_any_when_no_general(self):
        q1 = _quote("A", "Preliminar", "2026-01-01", [])
        q2 = _quote("B", "Extraordinaria", "2026-04-01", [])
        active = cn.pick_active_quote([q1, q2])
        self.assertEqual(active["id"], "B")

    def test_no_quotes(self):
        self.assertIsNone(cn.pick_active_quote([]))


class AggregateQuoteItemsTest(unittest.TestCase):
    def test_groups_by_catalog_id_and_handles_unlinked(self):
        quote = _quote("A", "General", "2026-04-01", [
            _q_item("CAT-1", 2, 100),
            _q_item("CAT-1", 3, 100),  # se suma cantidad
            _q_item("CAT-2", 5, 50),
            _q_item("", 1, 999, description="Manual"),  # unlinked
        ])
        linked, unlinked = cn.aggregate_quote_items(quote)
        self.assertEqual(set(linked), {"CAT-1", "CAT-2"})
        self.assertEqual(linked["CAT-1"]["qty"], 5)
        self.assertEqual(linked["CAT-1"]["total"], 500)
        self.assertEqual(linked["CAT-1"]["price_avg"], 100)
        self.assertEqual(unlinked["count"], 1)
        self.assertEqual(unlinked["total"], 999)

    def test_no_quote(self):
        linked, unlinked = cn.aggregate_quote_items(None)
        self.assertEqual(linked, {})
        self.assertEqual(unlinked, {"count": 0, "total": 0.0})


class AggregateLdmItemsTest(unittest.TestCase):
    def test_aggregates_across_multiple_ldms(self):
        ldm1 = _ldm("L1", [_l_item("CAT-1", 5, 80)])
        ldm2 = _ldm("L2", [_l_item("CAT-1", 5, 90)])
        ldm3 = _ldm("L3", [_l_item("CAT-2", 10, 30), _l_item("", 2, 100)])
        linked, unlinked = cn.aggregate_ldm_items([ldm1, ldm2, ldm3])
        self.assertEqual(linked["CAT-1"]["qty"], 10)
        # Costo promedio ponderado: (5*80 + 5*90)/10 = 85
        self.assertEqual(linked["CAT-1"]["cost_avg"], 85)
        self.assertEqual(sorted(linked["CAT-1"]["ldm_numbers"]), ["LDM-L1", "LDM-L2"])
        self.assertEqual(unlinked["count"], 1)
        self.assertEqual(unlinked["total"], 200)


class CompareItemsTest(unittest.TestCase):
    def test_detects_all_issue_types(self):
        # CAT-1: en COT y LDM con qty igual y precio venta > costo  → ok
        # CAT-2: en COT, no en LDM (5 cot vs 0 ldm)                → missing_in_ldm
        # CAT-3: en LDM, no en COT                                 → missing_in_cot
        # CAT-4: en COT y LDM con qty diferente                    → qty_mismatch
        # CAT-5: en COT y LDM, COT.price < LDM.cost_avg             → below_cost
        quote = _quote("A", "General", "2026-04-01", [
            _q_item("CAT-1", 10, 100),
            _q_item("CAT-2", 5, 50),
            _q_item("CAT-4", 8, 200),
            _q_item("CAT-5", 4, 30),
        ])
        ldm = _ldm("L1", [
            _l_item("CAT-1", 10, 60),
            _l_item("CAT-3", 7, 20),
            _l_item("CAT-4", 6, 100),
            _l_item("CAT-5", 4, 50),
        ])
        q_linked, _ = cn.aggregate_quote_items(quote)
        l_linked, _ = cn.aggregate_ldm_items([ldm])

        rows = cn.compare_items(q_linked, l_linked, catalog_by_id={
            "CAT-1": {"nombre": "Cable", "categoria": "Conductores", "unidad": "m"},
        })
        by_id = {row["catalog_item_id"]: row for row in rows}

        self.assertEqual(by_id["CAT-1"]["issues"], [])
        self.assertEqual(by_id["CAT-1"]["status"], "ok")
        self.assertIn("missing_in_ldm", by_id["CAT-2"]["issues"])
        self.assertEqual(by_id["CAT-2"]["status"], "critical")
        self.assertIn("missing_in_cot", by_id["CAT-3"]["issues"])
        self.assertIn("qty_mismatch", by_id["CAT-4"]["issues"])
        self.assertIn("below_cost", by_id["CAT-5"]["issues"])
        self.assertEqual(by_id["CAT-5"]["status"], "critical")
        # Catálogo enriquece la fila con nombre y categoría
        self.assertEqual(by_id["CAT-1"]["nombre"], "Cable")
        self.assertEqual(by_id["CAT-1"]["categoria"], "Conductores")
        # Severity ordering: criticals primero, luego warnings, luego ok
        statuses = [row["status"] for row in rows]
        self.assertEqual(statuses, sorted(statuses, key=lambda s: {"critical": 0, "warning": 1, "ok": 2}.get(s, 9)))


class ComputeConsistencyTest(unittest.TestCase):
    def test_full_report_with_general_quote(self):
        quote = _quote("Q1", "General", "2026-04-01", [
            _q_item("CAT-1", 10, 100),
            _q_item("CAT-2", 5, 200),
        ])
        # subtotal = 1000 + 1000 = 2000
        ldm = _ldm("L1", [
            _l_item("CAT-1", 10, 60),  # 600
            _l_item("CAT-2", 5, 90),   # 450
        ])
        # ldm subtotal = 1050
        report = cn.compute_consistency(PROJECT, [quote], [ldm], catalog_by_id={})
        self.assertEqual(report["quote_subtotal"], 2000)
        self.assertEqual(report["ldm_subtotal"], 1050)
        self.assertEqual(report["margin_abs"], 950)
        self.assertEqual(report["margin_pct"], 47.5)
        self.assertEqual(report["status"], "ok")
        self.assertTrue(report["has_general_quote"])
        self.assertTrue(report["active_quote_is_general"])
        self.assertEqual(report["summary"]["items_total"], 2)

    def test_warning_threshold(self):
        # Margen exactamente 20%
        quote = _quote("Q1", "General", "2026-04-01", [_q_item("CAT-1", 1, 100)])  # subtotal 100
        ldm = _ldm("L1", [_l_item("CAT-1", 1, 80)])  # subtotal 80
        report = cn.compute_consistency(PROJECT, [quote], [ldm], catalog_by_id={})
        self.assertEqual(report["margin_pct"], 20.0)
        self.assertEqual(report["status"], "warning")

    def test_critical_when_ldm_exceeds_cot(self):
        quote = _quote("Q1", "General", "2026-04-01", [_q_item("CAT-1", 1, 50)])  # 50
        ldm = _ldm("L1", [_l_item("CAT-1", 1, 80)])  # 80
        report = cn.compute_consistency(PROJECT, [quote], [ldm], catalog_by_id={})
        self.assertLess(report["margin_pct"], 0)
        self.assertEqual(report["status"], "critical")

    def test_no_data_when_empty(self):
        report = cn.compute_consistency(PROJECT, [], [], catalog_by_id={})
        self.assertEqual(report["status"], "no_data")
        self.assertIsNone(report["margin_pct"])
        self.assertIsNone(report["active_quote"])
        self.assertEqual(report["summary"]["items_total"], 0)

    def test_no_general_quote_uses_fallback(self):
        prelim = _quote("Q1", "Preliminar", "2026-04-01", [_q_item("CAT-1", 2, 50)])
        report = cn.compute_consistency(PROJECT, [prelim], [], catalog_by_id={})
        self.assertFalse(report["has_general_quote"])
        self.assertFalse(report["active_quote_is_general"])
        self.assertEqual(report["active_quote"]["id"], "Q1")

    def test_filters_by_project_id(self):
        # Cotización de OTRO proyecto no debe contar.
        other = _quote("OTHER", "General", "2026-04-01", [_q_item("CAT-1", 100, 100)], project_id="P2")
        own = _quote("Q1", "General", "2026-04-01", [_q_item("CAT-1", 1, 10)])
        report = cn.compute_consistency(PROJECT, [other, own], [], catalog_by_id={})
        self.assertEqual(report["quote_subtotal"], 10)


class LowMarginAndActionsTest(unittest.TestCase):
    def test_detects_low_margin_without_below_cost(self):
        quote = _quote("A", "General", "2026-04-01", [
            _q_item("CAT-LOW", 10, 100),
        ])
        ldm = _ldm("L1", [
            _l_item("CAT-LOW", 10, 75),  # margen unitario 25 %
        ])
        q_linked, _ = cn.aggregate_quote_items(quote)
        l_linked, _ = cn.aggregate_ldm_items([ldm])

        rows = cn.compare_items(q_linked, l_linked, catalog_by_id={})
        row = rows[0]
        self.assertIn("low_margin", row["issues"])
        self.assertNotIn("below_cost", row["issues"])
        self.assertEqual(row["status"], "warning")
        self.assertEqual(row["margin_unit"], 25)
        self.assertEqual(row["margin_unit_pct"], 25.0)
        self.assertEqual(row["primary_action"]["issue"], "low_margin")

    def test_report_includes_suggested_actions_and_linked_totals(self):
        quote = _quote("Q1", "General", "2026-04-01", [
            _q_item("CAT-1", 1, 100),
            _q_item("", 1, 50, description="Manual COT"),
        ])
        ldm = _ldm("L1", [
            _l_item("CAT-1", 1, 95),  # low_margin
            _l_item("", 1, 30, description="Manual LDM"),
        ])
        report = cn.compute_consistency(PROJECT, [quote], [ldm], catalog_by_id={})
        self.assertEqual(report["quote_linked_total"], 100)
        self.assertEqual(report["ldm_linked_total"], 95)
        self.assertEqual(report["quote_unlinked_total"], 50)
        self.assertEqual(report["ldm_unlinked_total"], 30)
        self.assertEqual(report["summary"]["low_margin"], 1)
        issues = [item["issue"] for item in report["suggested_actions"]]
        self.assertIn("low_margin", issues)
        self.assertIn("quote_unlinked", issues)
        self.assertIn("ldm_unlinked", issues)


if __name__ == "__main__":
    unittest.main()
