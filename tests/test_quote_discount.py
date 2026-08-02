import unittest

from tracker.catalog import compute_quote_totals, hydrate_quote


class ComputeQuoteTotalsTest(unittest.TestCase):
    def test_no_discount_no_tax(self):
        totals = compute_quote_totals(1000, 0, 0)
        self.assertEqual(totals["discount_amount"], 0)
        self.assertEqual(totals["subtotal_after_discount"], 1000)
        self.assertEqual(totals["tax"], 0)
        self.assertEqual(totals["total"], 1000)

    def test_tax_only_no_discount(self):
        totals = compute_quote_totals(1000, 16, 0)
        self.assertEqual(totals["discount_amount"], 0)
        self.assertEqual(totals["subtotal_after_discount"], 1000)
        self.assertEqual(totals["tax"], 160)
        self.assertEqual(totals["total"], 1160)

    def test_discount_applied_before_tax(self):
        # 1000 - 10% descuento = 900; IVA 16% sobre 900 = 144; total 1044.
        # (Si el IVA se calculara sobre el subtotal original daría 160/1140 — mal.)
        totals = compute_quote_totals(1000, 16, 10)
        self.assertEqual(totals["discount_pct"], 10)
        self.assertEqual(totals["discount_amount"], 100)
        self.assertEqual(totals["subtotal_after_discount"], 900)
        self.assertEqual(totals["tax"], 144)
        self.assertEqual(totals["total"], 1044)

    def test_discount_without_tax(self):
        totals = compute_quote_totals(1000, 0, 20)
        self.assertEqual(totals["discount_amount"], 200)
        self.assertEqual(totals["subtotal_after_discount"], 800)
        self.assertEqual(totals["tax"], 0)
        self.assertEqual(totals["total"], 800)

    def test_discount_pct_is_clamped_to_0_100(self):
        over = compute_quote_totals(1000, 0, 150)
        self.assertEqual(over["discount_pct"], 100)
        self.assertEqual(over["total"], 0)

        under = compute_quote_totals(1000, 0, -20)
        self.assertEqual(under["discount_pct"], 0)
        self.assertEqual(under["total"], 1000)

    def test_full_discount_zeroes_total_even_with_tax(self):
        totals = compute_quote_totals(1000, 16, 100)
        self.assertEqual(totals["subtotal_after_discount"], 0)
        self.assertEqual(totals["tax"], 0)
        self.assertEqual(totals["total"], 0)


class HydrateQuoteDiscountTest(unittest.TestCase):
    def test_hydrate_quote_applies_discount_before_tax(self):
        quote = hydrate_quote({
            "tax_rate": 16,
            "discount_pct": 10,
            "items": [
                {"description": "Item", "qty": 1, "price": 1000},
            ],
        })
        self.assertEqual(quote["subtotal"], 1000)
        self.assertEqual(quote["discount_amount"], 100)
        self.assertEqual(quote["subtotal_after_discount"], 900)
        self.assertEqual(quote["tax"], 144)
        self.assertEqual(quote["total"], 1044)

    def test_hydrate_quote_defaults_discount_to_zero(self):
        quote = hydrate_quote({
            "tax_rate": 16,
            "items": [{"description": "Item", "qty": 1, "price": 100}],
        })
        self.assertEqual(quote["discount_pct"], 0)
        self.assertEqual(quote["discount_amount"], 0)
        self.assertEqual(quote["total"], 116)


if __name__ == "__main__":
    unittest.main()
