import copy
import io
import unittest
from unittest.mock import patch

import pdfplumber
from werkzeug.datastructures import MultiDict

from tracker.form_models import quote_from_form
from tracker.pdfs import build_quote_pdf
from tracker.terms_templates_config import resolve_quote_terms
from tracker.validators import validate_quote_form


TEMPLATES = [{"id": "base", "name": "Base", "terms": [
    {"id": "pago", "title": "Pago", "body": "Texto general", "enabled": True},
]}]


class QuoteTermsEditingTest(unittest.TestCase):
    def setUp(self):
        self.templates = copy.deepcopy(TEMPLATES)
        self.template_patch = patch("tracker.terms_templates_config.get_terms_templates", side_effect=lambda: self.templates)
        self.template_patch.start()
        self.addCleanup(self.template_patch.stop)

    def form(self):
        return MultiDict([
            ("quote_type", "Proyecto"), ("date", "2026-10-10"), ("currency", "MXN"),
            ("item_desc[]", "Proyecto general"), ("item_qty[]", "1"),
            ("item_unit[]", "lote"), ("item_precio_costo[]", "100"),
            ("terms_template_id", "base"), ("terms_present", "1"),
            ("term_id[]", "pago"), ("term_title[]", "Anticipo"),
            ("term_body[]", "50% al iniciar"), ("term_enabled[]", "1"),
            ("term_id[]", "oculto"), ("term_title[]", "Oculto"),
            ("term_body[]", "No imprimir"), ("term_enabled[]", "0"),
        ])

    def test_validation_and_error_rerender_keep_custom_terms(self):
        validation = validate_quote_form(self.form())
        self.assertTrue(validation["ok"], validation["errors"])
        quote = quote_from_form(self.form(), {"specs": {"portada_spacing": "24"}})
        self.assertEqual(quote["specs"]["terms"], validation["specs"]["terms"])
        self.assertEqual(quote["specs"]["portada_spacing"], "24")
        self.assertEqual(quote["specs"]["terms"][0]["title"], "Anticipo")
        self.assertFalse(quote["specs"]["terms"][1]["enabled"])

    def test_saved_terms_survive_template_changes_and_deletion(self):
        quote = quote_from_form(self.form())
        self.templates[0]["terms"][0]["body"] = "Plantilla modificada"
        terms, template = resolve_quote_terms(quote)
        self.assertEqual(terms[0]["body"], "50% al iniciar")
        self.assertEqual(template["id"], "base")
        self.templates.clear()
        terms, _ = resolve_quote_terms(quote)
        self.assertEqual(terms[0]["body"], "50% al iniciar")

    def test_existing_overrides_and_legacy_keys_are_preserved(self):
        terms, _ = resolve_quote_terms({"specs": {
            "terms_template_id": "base", "term_body_overrides": {"pago": "Override anterior"},
        }})
        self.assertEqual(terms[0]["body"], "Override anterior")
        terms, _ = resolve_quote_terms({"specs": {"terms_template_id": "base", "terms": [
            {"key": "vigencia", "body": "30 días", "enabled": True},
        ]}})
        self.assertEqual(terms[0]["id"], "vigencia")
        self.assertEqual(terms[0]["title"], "Vigencia")
        self.assertEqual(terms[0]["body"], "30 días")

    def test_empty_terms_are_intentional_and_old_forms_keep_terms(self):
        quote = quote_from_form(MultiDict({"terms_present": "1"}))
        self.assertEqual(resolve_quote_terms(quote)[0], [])
        existing = {"specs": {"terms": [{"id": "pago", "body": "Guardado"}]}}
        self.assertEqual(quote_from_form(MultiDict(), existing)["specs"]["terms"], existing["specs"]["terms"])

    def test_pdf_uses_local_terms_and_embeds_lato_in_both_cover_modes(self):
        quote = quote_from_form(self.form())
        quote.update(quote_number="COT-TEST-P01", subtotal=100, total=100)
        quote["specs"]["condiciones_pago"] = "Condición específica"
        quote["cover_discipline"] = "Diseño integral de instalaciones eléctricas y coordinación del proyecto ejecutivo para vivienda residencial"
        for spacing in ("40", "24"):
            with self.subTest(spacing=spacing), patch("tracker.pdfs._load_company", return_value={"name": "Empresa"}), patch("tracker.pdfs.quote_logo_path", return_value=None):
                quote["specs"]["portada_spacing"] = spacing
                with pdfplumber.open(io.BytesIO(build_quote_pdf({"name": "Proyecto", "client": "Cliente"}, quote))) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    self.assertIn("50% al iniciar", text)
                    self.assertIn("Condición específica", text)
                    self.assertNotIn("Texto general", text)
                    self.assertNotIn("No imprimir", text)
                    fonts = {char["fontname"] for page in pdf.pages for char in page.chars}
                    self.assertTrue(all("Lato" in font for font in fonts), fonts)
                    expected_size = 26.0 if spacing == "40" else 18.0
                    description_words = pdf.pages[0].extract_words(extra_attrs=["size"])
                    description_word = next(w for w in description_words if w["text"] == "Diseño")
                    self.assertAlmostEqual(description_word["size"], expected_size, places=2)
                    heading_word = next(w for w in description_words if w["text"] == "Cotización")
                    self.assertGreater(description_word["size"], heading_word["size"])
                quote["specs"]["terms"] = []
                with pdfplumber.open(io.BytesIO(build_quote_pdf({"name": "Proyecto"}, quote))) as pdf:
                    text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                    self.assertNotIn("Términos y Condiciones", text)
                    self.assertNotIn("Texto general", text)
                quote["specs"]["terms"] = quote_from_form(self.form())["specs"]["terms"]

    def test_save_in_both_editors_preserves_quote_terms_and_template(self):
        from tracker import create_app
        project = {"id": "PTERMS", "name": "Proyecto", "clave": "TERMS", "client": "Cliente"}
        quote = {"id": "QTERMS", "project_id": project["id"], "quote_type": "Proyecto", "quote_number": "COT-TEST-P01", "date": "2026-10-10", "items": [], "specs": {"nota_precio": "Nota guardada"}}
        records = {"projects": [project], "quotes": [quote], "catalogo": []}
        app = create_app()
        app.config.update(TESTING=True, LOGIN_DISABLED=True, WTF_CSRF_ENABLED=False)
        client = app.test_client()
        with patch("tracker.routes.quotes.load", side_effect=lambda key: records.get(key, [])), patch("tracker.routes.quotes.save") as save:
            url = "/projects/PTERMS/quote/QTERMS"
            for editor in ("/edit", "/pdf-editor", "/edit"):
                response = client.post(url + editor, data=self.form())
                self.assertEqual(response.status_code, 302)
                saved_quote = save.call_args.args[1][0]
                self.assertEqual(saved_quote["specs"]["terms"][0]["body"], "50% al iniciar")
                self.assertEqual(saved_quote["specs"]["nota_precio"], "Nota guardada" if editor == "/edit" and save.call_count == 1 else "")
                for view in ("/edit", "/pdf-editor"):
                    response = client.get(url + view)
                    self.assertEqual(response.status_code, 200)
                    self.assertIn("50% al iniciar", response.get_data(as_text=True))
                    self.assertIn('name="term_title[]"', response.get_data(as_text=True))
        self.assertEqual(self.templates, TEMPLATES)

    def test_large_table_amounts_stay_inside_their_columns(self):
        quote = quote_from_form(self.form())
        quote.update(quote_number="COT-TEST-P01", subtotal=123456789, total=123456789)
        quote["items"] = [{"description": "Descripción general del proyecto", "qty": 1, "unit": "lote", "price": 123456789, "total": 123456789}]
        with patch("tracker.pdfs._load_company", return_value={"name": "Empresa"}), patch("tracker.pdfs.quote_logo_path", return_value=None):
            with pdfplumber.open(io.BytesIO(build_quote_pdf({"name": "Proyecto"}, quote))) as pdf:
                words = pdf.pages[1].extract_words()
                unit = next(word for word in words if word["text"] == "lote")
                amounts = [word for word in words if word["text"] == "$123,456,789.00" and abs(word["top"] - unit["top"]) < 8]
                self.assertEqual(len(amounts), 2)
                scale = 72 / 25.4
                for word, left, right in zip(amounts, (144, 172), (172, 200)):
                    self.assertGreaterEqual(word["x0"], left * scale)
                    self.assertLessEqual(word["x1"], right * scale)
