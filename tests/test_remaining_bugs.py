"""BUG-08 through BUG-13: isolated persistence and rendered PDF regressions."""
import copy
import io
import re
from urllib.parse import parse_qs, urlsplit
from unittest.mock import patch

import pdfplumber
from flask import template_rendered

from test_priority_bugs import IsolatedAppFixture, PROJECT, QUOTE
from tracker import storage
from tracker.pdfs import build_quote_pdf


class RemainingBugTests(IsolatedAppFixture):
    def payment(self, **overrides):
        return {"id": "PAY1", "project_id": "P1", "quote_id": "Q1", "date": "2026-10-11",
                "amount": 50, "concept": "Anticipo", **overrides}

    def test_paid_quote_and_project_cannot_be_deleted(self):
        self.grant()
        storage.save("payments", [self.payment()])
        before = self.snapshot()
        response = self.client.post("/projects/P1/quote/Q1/delete", follow_redirects=True)
        self.assertIn("tiene pagos registrados", response.get_data(as_text=True))
        self.assertEqual(self.snapshot(), before)
        self.login(admin=True)
        response = self.client.post("/projects/P1/delete", follow_redirects=True)
        self.assertIn("tiene pagos registrados", response.get_data(as_text=True))
        self.assertEqual(self.snapshot(), before)
        # A damaged project_id does not allow deleting the quote's financial history.
        storage.save("payments", [self.payment(project_id="P2")])
        before = self.snapshot()
        self.client.post("/projects/P1/delete")
        self.assertEqual(self.snapshot(), before)

    def test_unpaid_deletion_preserves_other_projects_payments(self):
        self.grant()
        other = self.payment(id="PAY2", project_id="P2", quote_id="Q2")
        storage.save("payments", [other])
        self.client.post("/projects/P1/quote/Q1/delete")
        self.assertEqual(storage.load("quotes"), [])
        self.assertEqual(storage.load("payments"), [other])
        self.login(admin=True)
        self.client.post("/projects/P1/delete")
        self.assertFalse(any(p["id"] == "P1" for p in storage.load("projects")))
        self.assertEqual(storage.load("payments"), [other])

    def close(self):
        projects = storage.load("projects")
        projects[0]["closed_at"] = "2026-10-11"
        storage.save("projects", projects)

    def test_closed_projects_reject_all_project_document_mutations(self):
        self.login(admin=True)
        self.close()
        excluded = {"reopen_project", "add_payment", "edit_payment", "delete_payment"}
        checked = set()
        for rule in self.app.url_map.iter_rules():
            if not rule.endpoint.startswith(("projects_bp.", "quotes_bp.", "materials_bp.", "quotes_mobile_bp.", "admin_bp.")):
                continue
            if "project_id" not in rule.arguments or "POST" not in rule.methods or rule.endpoint.rsplit(".", 1)[-1] in excluded:
                continue
            ids = {"project_id": "P1", "quote_id": "Q1", "ldm_id": "L1", "item_index": "0", "item_id": "X", "delivery_id": "D1"}
            url = re.sub(r"<(?:[^:<>]+:)?(\w+)>", lambda m: ids.get(m[1], "X"), rule.rule)
            with self.subTest(endpoint=rule.endpoint):
                before = self.snapshot()
                response = self.client.post(url, data={"cover_discipline": "Intruso", "project_name_override": "Intruso", "item_id": "CAT1", "qty": "2", "name": "Intruso"})
                self.assertEqual(response.status_code, 302)
                self.assertEqual(self.snapshot(), before)
                checked.add(rule.endpoint)
        self.assertGreaterEqual(len(checked), 30)

    def test_closed_mobile_draft_reset_and_ldm_cost_api_are_guarded(self):
        self.grant()
        self.close()
        storage.save("quotes", [copy.deepcopy(QUOTE), {**copy.deepcopy(QUOTE), "id": "QD", "status": "draft", "approval_status": "draft"}])
        before = self.snapshot()
        self.assertEqual(self.client.get("/cotizar/mobile/P1/items?nueva=1").status_code, 302)
        self.assertEqual(self.client.post("/api/ldm/L1/costo", json={"subtotal_cot": 99}).status_code, 302)
        self.assertEqual(self.snapshot(), before)

    def test_closed_project_can_be_read_and_paid_then_reopened_to_edit(self):
        self.grant()
        self.close()
        self.assertEqual(self.client.get("/projects/P1/quote/Q1/view").status_code, 200)
        pdf = self.client.get("/projects/P1/quote/Q1/pdf?inline=1")
        self.assertEqual(pdf.status_code, 200)
        pdf.close()
        self.client.post("/projects/P1/payments/add", data={"quote_id": "Q1", "date": "2026-10-11", "amount": "25"})
        self.assertEqual(storage.load("payments")[0]["amount"], 25)
        self.client.post("/projects/P1/reopen")
        self.client.post("/projects/P1/quote/Q1/pdf-editor", data={"cover_discipline": "Reabierto"})
        self.assertEqual(storage.load("quotes")[0]["cover_discipline"], "Reabierto")
        self.client.post("/cotizar/mobile/P1/items", data={"item_id": "CAT1", "qty": "2"})
        self.assertTrue(any(q.get("status") == "draft" for q in storage.load("quotes")))

    def test_dashboard_and_detail_share_active_totals_and_ignore_mobile_drafts(self):
        self.grant()
        def q(id, total, **extra):
            return {**copy.deepcopy(QUOTE), "id": id, "total": total,
                    "items": [{"description": id, "unit": "pza", "qty": 1, "price": total, "total": total}], **extra}
        legacy = q("QL", 30)
        legacy.pop("approval_status")
        storage.save("quotes", [{**copy.deepcopy(QUOTE), "total": 9999}, q("QE", 25, quote_type="Extraordinaria"),
                                q("QD", 200, approval_status="draft"), q("QO", 300, approval_status="obsolete"),
                                q("QM", 999, status="draft"), legacy])
        contexts = {}
        def capture(sender, template, context, **kwargs):
            contexts[template.name] = context
        with template_rendered.connected_to(capture, self.app):
            self.client.get("/")
            self.client.get("/projects/P1")
        dashboard = next(p for p in contexts["dashboard.html"]["active"] if p["id"] == "P1")
        self.assertEqual(dashboard["total_cotizado"], 155)
        self.assertEqual(contexts["project_detail.html"]["total_cotizado"], 155)
        self.assertEqual(contexts["project_detail.html"]["active_bases_count"], 2)

    def test_catalog_decimal_comma_works_for_create_and_edit(self):
        self.grant()
        data = {"nombre": "Rollo", "precio": "10", "buy_unit_size": "2,5", "is_fractional": "1"}
        self.assertEqual(self.client.post("/catalogo", data=data).status_code, 302)
        item = storage.load("catalogo")[-1]
        self.assertEqual(item["buy_unit_size"], 2.5)
        self.assertEqual(self.client.post(f'/catalogo/{item["id"]}/edit', data={**data, "buy_unit_size": "3,75"}).status_code, 302)
        self.assertEqual(storage.load("catalogo")[-1]["buy_unit_size"], 3.75)

    def test_catalog_invalid_buy_size_is_rejected_without_mutation(self):
        self.grant()
        for raw in ("bad", "NaN", "inf", "1e309", "0", "-2"):
            with self.subTest(raw=raw):
                before = self.snapshot()
                data = {"nombre": "Rollo", "precio": "10", "buy_unit_size": raw}
                page = self.client.post("/catalogo", data=data)
                self.assertEqual(page.status_code, 200)
                self.assertIn("unidad de compra", page.get_data(as_text=True))
                self.assertIn('id="newFractionalFields" class="mt-2"', page.get_data(as_text=True))
                response = self.client.post("/catalogo/CAT1/edit", data=data, headers={"X-Requested-With": "XMLHttpRequest"})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.client.post("/catalogo/CAT1/edit", data={"nombre": "Artículo", "precio": "10", "buy_unit_size": ""}).status_code, 302)
        self.assertIsNone(storage.load("catalogo")[0]["buy_unit_size"])

    def test_login_rejects_external_and_ambiguous_redirects(self):
        for target in ("https://example.invalid/audit", "//example.invalid", "///example.invalid", "/\\example.invalid", "/\t/example.invalid", "javascript:alert(1)"):
            with self.subTest(target=target):
                fresh = self.app.test_client()
                response = fresh.post("/login", query_string={"next": target}, data={"username": "cotizador", "password": "Synthetic-user-only"})
                self.assertEqual(response.headers["Location"], "/")

    def test_login_preserves_local_destination_and_anonymous_request_query(self):
        fresh = self.app.test_client()
        target = "/projects/P1?tab=pagos"
        login = fresh.get(target)
        self.assertEqual(login.status_code, 302)
        next_path = parse_qs(urlsplit(login.headers["Location"]).query)["next"][0]
        self.assertEqual(next_path, target)
        response = fresh.post(login.headers["Location"], data={"username": "cotizador", "password": "Synthetic-user-only"})
        self.assertEqual(response.headers["Location"], target)

    def test_payment_return_destination_rejects_external_urls_and_preserves_local_paths(self):
        self.grant()
        for target, expected in (("https://example.invalid", "/projects/P1#tab-pagos"), ("/pagos", "/pagos")):
            response = self.client.post("/projects/P1/payments/add", data={"quote_id": "Q1", "date": "2026-10-11", "amount": "25", "next": target})
            self.assertEqual(response.headers["Location"], expected)

    def test_cover_long_name_remains_complete_at_requested_size_without_overlap(self):
        long_name = ("Diseño integral de instalaciones eléctricas, iluminación y coordinación del proyecto ejecutivo para vivienda residencial. " * 6).strip()
        for spacing, name_size in (("40", 24), ("24", 18)):
            for name in ("Diseño eléctrico", long_name, long_name * 4):
                with self.subTest(spacing=spacing, characters=len(name)):
                    quote = copy.deepcopy(QUOTE)
                    quote["cover_discipline"] = name
                    quote["specs"].update(portada_spacing=spacing, project_basis_note="")
                    with patch("tracker.pdfs._load_company", return_value={"name": "Empresa de prueba"}), patch("tracker.pdfs.quote_logo_path", return_value=None):
                        data = build_quote_pdf(PROJECT, quote)
                    with pdfplumber.open(io.BytesIO(data)) as pdf:
                        title_words = []
                        summary_page = None
                        for page_index, page in enumerate(pdf.pages):
                            words = page.extract_words(extra_attrs=["size"])
                            title_words += [w["text"] for w in words if abs(w["size"] - name_size) < .01]
                            for word in words:
                                if abs(word["size"] - name_size) < .01:
                                    self.assertLess(word["bottom"], 210 * 72 / 25.4)
                            if any(w["text"] == "TOTAL" and abs(w["size"] - 20) < .01 for w in words) and summary_page is None:
                                summary_page = page_index
                                summary_top = min(w["top"] for w in words if w["text"] == "PROYECTO")
                                for word in words:
                                    if abs(word["size"] - name_size) < .01:
                                        self.assertLess(word["bottom"], summary_top)
                        self.assertEqual(" ".join(title_words).split(), name.split())
                        self.assertIsNotNone(summary_page)
                        self.assertIn("Cliente", pdf.pages[summary_page].extract_text())
