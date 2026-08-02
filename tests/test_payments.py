import unittest

from tracker import create_app
from tracker.payments import (
    add_payment,
    delete_payment,
    get_payment_by_id,
    get_payments_for_project,
    get_payments_for_quote,
    payment_summary,
    update_payment,
)
from tracker.storage import load, save

PROJECT = {
    "id": "PAY001TEST",
    "name": "Test Pagos Proyecto",
    "clave": "PAY",
    "client": "Cliente Test",
    "folder_num": "098",
    "version": "V1",
    "fecha": "260101",
    "alcances": ["cotizacion"],
    "notes": "",
    "closed_at": None,
    "in_obra": False,
    "template_id": "residencial",
    "drive_url": "",
    "created_at": "2026-01-01",
    "updated_at": "2026-01-01",
}

QUOTE = {
    "id": "PAYQ001TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "PAY-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "tax_enabled": True,
    "discount_pct": 0,
    "approval_status": "active",
    "items": [
        {"description": "Concepto de prueba", "qty": 1, "price": 1000, "total": 1000},
    ],
    "created_at": "2026-01-01",
}


class PaymentsModelTest(unittest.TestCase):
    """Pruebas unitarias del módulo tracker.payments, sin tocar storage real."""

    def setUp(self):
        self._saved_payments = load("payments")
        save("payments", [])

    def tearDown(self):
        save("payments", self._saved_payments)

    def test_add_and_get_payments_for_quote(self):
        add_payment("PROJ1", "QUOTE1", "2026-01-05", 500, "Anticipo")
        add_payment("PROJ1", "QUOTE2", "2026-01-06", 300, "Otro concepto")
        payments = get_payments_for_quote("QUOTE1")
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0]["amount"], 500)
        self.assertEqual(payments[0]["concept"], "Anticipo")

    def test_get_payments_for_project_includes_all_quotes(self):
        add_payment("PROJ1", "QUOTE1", "2026-01-05", 500, "Anticipo")
        add_payment("PROJ1", "QUOTE2", "2026-01-06", 300, "Otro concepto")
        payments = get_payments_for_project("PROJ1")
        self.assertEqual(len(payments), 2)

    def test_update_payment(self):
        payment = add_payment("PROJ1", "QUOTE1", "2026-01-05", 500, "Anticipo")
        ok = update_payment(payment["id"], "2026-01-07", 600, "Anticipo corregido")
        self.assertTrue(ok)
        updated = get_payment_by_id(payment["id"])
        self.assertEqual(updated["amount"], 600)
        self.assertEqual(updated["date"], "2026-01-07")
        self.assertEqual(updated["concept"], "Anticipo corregido")

    def test_update_payment_unknown_id_returns_false(self):
        self.assertFalse(update_payment("no-existe", "2026-01-01", 100, ""))

    def test_delete_payment(self):
        payment = add_payment("PROJ1", "QUOTE1", "2026-01-05", 500, "Anticipo")
        self.assertTrue(delete_payment(payment["id"]))
        self.assertIsNone(get_payment_by_id(payment["id"]))

    def test_delete_payment_unknown_id_returns_false(self):
        self.assertFalse(delete_payment("no-existe"))

    def test_payment_summary_computes_balance(self):
        payments = [{"amount": 400}, {"amount": 100}]
        summary = payment_summary(1000, payments)
        self.assertEqual(summary["total"], 1000)
        self.assertEqual(summary["paid"], 500)
        self.assertEqual(summary["balance"], 500)

    def test_payment_summary_no_payments(self):
        summary = payment_summary(1000, [])
        self.assertEqual(summary["paid"], 0)
        self.assertEqual(summary["balance"], 1000)


class PaymentsRoutesTest(unittest.TestCase):
    """Pruebas de extremo a extremo de las rutas de pagos en quotes.py."""

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()

        self._saved_projects = load("projects")
        self._saved_quotes = load("quotes")
        self._saved_payments = load("payments")
        save("projects", [p for p in self._saved_projects if p["id"] != PROJECT["id"]] + [dict(PROJECT)])
        save("quotes", [q for q in self._saved_quotes if q["id"] != QUOTE["id"]] + [dict(QUOTE)])
        save("payments", [])

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)
        save("payments", self._saved_payments)

    def _add_payment(self, **overrides):
        data = {
            "quote_id": QUOTE["id"],
            "date": "2026-02-01",
            "amount": "400",
            "concept": "Anticipo",
            "next": "",
        }
        data.update(overrides)
        return self.client.post(
            f"/projects/{PROJECT['id']}/payments/add",
            data=data,
            follow_redirects=True,
        )

    def test_add_payment_via_project_route(self):
        response = self._add_payment()
        self.assertEqual(response.status_code, 200)
        payments = get_payments_for_quote(QUOTE["id"])
        self.assertEqual(len(payments), 1)
        self.assertEqual(payments[0]["amount"], 400)
        self.assertEqual(payments[0]["concept"], "Anticipo")

    def test_add_payment_rejects_invalid_amount(self):
        response = self._add_payment(amount="abc")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_payments_for_quote(QUOTE["id"]), [])

    def test_add_payment_rejects_missing_date(self):
        response = self._add_payment(date="")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_payments_for_quote(QUOTE["id"]), [])

    def test_add_payment_rejects_unknown_quote(self):
        response = self._add_payment(quote_id="no-existe")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(get_payments_for_project(PROJECT["id"]), [])

    def test_edit_payment_via_route(self):
        self._add_payment()
        payment = get_payments_for_quote(QUOTE["id"])[0]
        response = self.client.post(
            f"/projects/{PROJECT['id']}/payments/{payment['id']}/edit",
            data={"date": "2026-02-10", "amount": "650", "concept": "Anticipo actualizado", "next": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        updated = get_payment_by_id(payment["id"])
        self.assertEqual(updated["amount"], 650)
        self.assertEqual(updated["concept"], "Anticipo actualizado")

    def test_delete_payment_via_route(self):
        self._add_payment()
        payment = get_payments_for_quote(QUOTE["id"])[0]
        response = self.client.post(
            f"/projects/{PROJECT['id']}/payments/{payment['id']}/delete",
            data={"next": ""},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIsNone(get_payment_by_id(payment["id"]))

    def test_quote_detail_page_shows_payment_summary(self):
        self._add_payment(amount="1000")
        response = self.client.get(
            f"/projects/{PROJECT['id']}/quote/{QUOTE['id']}/view",
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("Pagos", text)
        self.assertIn("Anticipo", text)

    def test_project_detail_page_shows_payments_tab(self):
        response = self.client.get(f"/projects/{PROJECT['id']}", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("tab-pagos", text)


if __name__ == "__main__":
    unittest.main()
