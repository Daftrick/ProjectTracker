"""La caja financiera del header de project_detail.html ("Cotizado cliente" /
"Costo proveedor" / "Margen") ahora también muestra los pagos totales
realizados al proyecto ("Pagado" y "Saldo pendiente"), calculados en
build_project_detail_context (tracker/project_view.py) contra total_cotizado.
Ver [[quote-payments-link]] para el botón por-cotización; esto es el resumen
a nivel proyecto."""

from pathlib import Path
import unittest

from tracker import create_app
from tracker.payments import add_payment
from tracker.storage import load, save

PROJECT = {
    "id": "FINCARD01TEST",
    "name": "Test Tarjeta Financiera Proyecto",
    "clave": "FIN",
    "client": "Cliente Test",
    "folder_num": "109",
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
    "id": "FINCARDQ01TEST",
    "project_id": PROJECT["id"],
    "quote_type": "General",
    "quote_number": "FIN-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 0,
    "approval_status": "active",
    "items": [{"description": "Concepto de prueba", "qty": 1, "price": 5000, "total": 5000}],
    "created_at": "2026-01-01",
}


class FinancialCardTemplateSourceTest(unittest.TestCase):
    def test_project_detail_shows_pagado_and_saldo_rows(self):
        template = Path("templates/project_detail.html").read_text(encoding="utf-8")
        self.assertIn("total_pagado_proyecto", template)
        self.assertIn("saldo_pendiente_proyecto", template)
        self.assertIn("Saldo pendiente", template)
        self.assertIn("tab-pagos-link", template)


class FinancialCardRouteTest(unittest.TestCase):
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
        save("payments", [p for p in self._saved_payments if p.get("project_id") != PROJECT["id"]])

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)
        save("payments", self._saved_payments)

    def test_project_detail_page_shows_paid_amount_and_balance(self):
        add_payment(PROJECT["id"], QUOTE["id"], "2026-02-01", 2000, "Anticipo")
        response = self.client.get(f"/projects/{PROJECT['id']}")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        # Subtotal 5000 + IVA 16% = total_cotizado 5800; pagado 2000, saldo 3800.
        self.assertIn("$2,000.00", text)
        self.assertIn("$3,800.00", text)
        self.assertIn("Pagado", text)
        self.assertIn("Saldo pendiente", text)

    def test_project_detail_page_shows_zero_paid_without_payments(self):
        response = self.client.get(f"/projects/{PROJECT['id']}")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("$0.00", text)


DISCOUNT_PROJECT = {
    "id": "FINCARDDISC01TEST",
    "name": "Test Tarjeta Financiera Descuento",
    "clave": "FCD",
    "client": "Cliente Test",
    "folder_num": "110",
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

# Subtotal 5000, descuento 10% = -500 → subtotal_after_discount 4500,
# IVA 16% sobre 4500 = 720 → total_cotizado real (hidratado) = 5220.
# hydrate_quote recalcula "total" a partir de items/discount_pct/tax_rate,
# así que la tarjeta debe reflejar 5220, no el subtotal bruto (5000) ni un
# 5800 calculado sin descuento.
DISCOUNT_QUOTE = {
    "id": "FINCARDDISCQ01TEST",
    "project_id": DISCOUNT_PROJECT["id"],
    "quote_type": "General",
    "quote_number": "FCD-COT-01",
    "version": "V1",
    "date": "2026-01-01",
    "currency": "MXN",
    "tax_rate": 16,
    "discount_pct": 10,
    "approval_status": "active",
    "items": [{"description": "Concepto de prueba", "qty": 1, "price": 5000, "total": 5000}],
    "created_at": "2026-01-01",
}


class DiscountFinancialCardRouteTest(unittest.TestCase):
    """La cotización de este proyecto tiene descuento_pct=10 — la tarjeta debe
    usar el total YA con descuento e IVA aplicados (5220), no el subtotal
    bruto (5000) ni el total sin descuento (5800)."""

    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self._saved_projects = load("projects")
        self._saved_quotes = load("quotes")
        self._saved_payments = load("payments")
        save("projects", [p for p in self._saved_projects if p["id"] != DISCOUNT_PROJECT["id"]] + [dict(DISCOUNT_PROJECT)])
        save("quotes", [q for q in self._saved_quotes if q["id"] != DISCOUNT_QUOTE["id"]] + [dict(DISCOUNT_QUOTE)])
        save("payments", [p for p in self._saved_payments if p.get("project_id") != DISCOUNT_PROJECT["id"]])

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)
        save("payments", self._saved_payments)

    def test_cotizado_cliente_reflects_discounted_total(self):
        response = self.client.get(f"/projects/{DISCOUNT_PROJECT['id']}")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn("$5,220.00", text)
        # No debe aparecer el total sin descontar como si fuera lo cotizado.
        self.assertNotIn("$5,800.00", text)

    def test_pagado_y_saldo_se_calculan_contra_el_total_con_descuento(self):
        add_payment(DISCOUNT_PROJECT["id"], DISCOUNT_QUOTE["id"], "2026-02-01", 1000, "Anticipo")
        response = self.client.get(f"/projects/{DISCOUNT_PROJECT['id']}")
        text = response.get_data(as_text=True)
        self.assertIn("$1,000.00", text)
        # Saldo = 5220 - 1000 = 4220 (no 4000, que sería contra el subtotal bruto).
        self.assertIn("$4,220.00", text)
        self.assertNotIn("$4,000.00", text)

    def test_context_totals_match_discounted_quote(self):
        """Verifica los mismos números a nivel de contexto (sin depender del
        render HTML), usando el pipeline real de hidratación de la app."""
        from tracker.project_view import build_project_detail_context

        with self.app.test_request_context():
            context = build_project_detail_context(dict(DISCOUNT_PROJECT))

        self.assertEqual(context["total_cotizado"], 5220.0)
        self.assertEqual(context["total_pagado_proyecto"], 0)
        self.assertEqual(context["saldo_pendiente_proyecto"], 5220.0)


if __name__ == "__main__":
    unittest.main()
