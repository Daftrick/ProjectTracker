import unittest
import tempfile

from tracker.pdfs import (
    build_quote_pdf,
    quote_cover_copy,
    quote_project_basis_note,
    quote_sequence_from_number,
)


class QuoteCoverCopyTest(unittest.TestCase):
    def test_proyecto(self):
        title, subtitle = quote_cover_copy({"quote_type": "Proyecto"})
        self.assertIn("Proyecto", title)
        self.assertIsNone(subtitle)

    def test_obra(self):
        title, subtitle = quote_cover_copy({"quote_type": "Obra"})
        self.assertIn("Obra", title)
        self.assertIsNone(subtitle)

    def test_servicio(self):
        title, subtitle = quote_cover_copy({"quote_type": "Servicio"})
        self.assertIn("Servicio", title)
        self.assertIsNone(subtitle)

    def test_extraordinaria_with_sequence(self):
        title, subtitle = quote_cover_copy({
            "quote_type": "Extraordinaria",
            "quote_number": "COT-OM001-E03-20260618",
        })
        self.assertIn("Extraordinaria", title)
        self.assertIn("03", subtitle)

    def test_extraordinaria_no_sequence(self):
        title, subtitle = quote_cover_copy({"quote_type": "Extraordinaria", "quote_number": ""})
        self.assertIn("Extraordinaria", title)
        self.assertIsNotNone(subtitle)

    def test_preliminar(self):
        title, subtitle = quote_cover_copy({"quote_type": "Preliminar"})
        self.assertIn("Preliminar", title)
        self.assertIsNone(subtitle)

    def test_general_fallback(self):
        title, subtitle = quote_cover_copy({"quote_type": "General"})
        self.assertIn("Cotización", title)


class QuoteProjectBasisNoteTest(unittest.TestCase):
    def test_proyecto_with_source(self):
        note = quote_project_basis_note({"quote_type": "Proyecto", "project_basis_source": "Plano A-01"})
        self.assertIn("Plano A-01", note)

    def test_proyecto_without_source(self):
        note = quote_project_basis_note({"quote_type": "Proyecto"})
        self.assertEqual(note, "")

    def test_obra_returns_empty(self):
        note = quote_project_basis_note({"quote_type": "Obra", "project_basis_source": "Plano B"})
        self.assertEqual(note, "")

    def test_servicio_returns_empty(self):
        note = quote_project_basis_note({"quote_type": "Servicio", "project_basis_source": "X"})
        self.assertEqual(note, "")

    def test_extraordinaria_uses_note_field(self):
        note = quote_project_basis_note({
            "quote_type": "Extraordinaria",
            "project_basis_note": "Proyecto estructural Rev3",
        })
        self.assertIn("Proyecto estructural Rev3", note)


class QuoteSequenceFromNumberTest(unittest.TestCase):
    def test_proyecto_code(self):
        self.assertEqual(quote_sequence_from_number("COT-OM001-P02-20260618"), "02")

    def test_obra_code(self):
        self.assertEqual(quote_sequence_from_number("COT-OM001-O01-20260618"), "01")

    def test_servicio_code(self):
        self.assertEqual(quote_sequence_from_number("COT-OM001-S03-20260618"), "03")

    def test_extraordinaria_code(self):
        self.assertEqual(quote_sequence_from_number("COT-OM001-E05-20260618"), "05")

    def test_general_code(self):
        self.assertEqual(quote_sequence_from_number("COT-OM001-G01-20260618"), "01")

    def test_no_match(self):
        self.assertEqual(quote_sequence_from_number("COT-OM001"), "")

    def test_empty(self):
        self.assertEqual(quote_sequence_from_number(""), "")


class QuotePdfSectionsTest(unittest.TestCase):
    def test_specs_terms_and_notes_render_as_independent_sections(self):
        import pdfplumber

        project = {
            "name": "Proyecto PDF",
            "client": "Cliente PDF",
        }
        quote = {
            "quote_type": "Proyecto",
            "quote_number": "COT-PDF-P01-20260627",
            "date": "2026-06-27",
            "currency": "MXN",
            "tax_rate": 16,
            "items": [
                {
                    "description": "Salida de prueba",
                    "unit": "pza",
                    "qty": 1,
                    "price": 100,
                    "precio_costo": 100,
                    "total": 100,
                }
            ],
            "subtotal": 100,
            "tax": 16,
            "total": 116,
            "notes": "Nota visible",
            "specs": {
                "condiciones_pago": "Pago visible",
                "terms": [
                    {
                        "key": "vigencia",
                        "title": "Vigencia.",
                        "body": "Termino visible",
                        "enabled": True,
                    },
                    {
                        "key": "precios",
                        "title": "Precios.",
                        "body": "Termino oculto",
                        "enabled": False,
                    },
                ],
            },
        }

        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            build_quote_pdf(project, quote, tmp.name)
            with pdfplumber.open(tmp.name) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)

        self.assertIn("Especificaciones técnicas", text)
        self.assertIn("Pago visible", text)
        self.assertIn("Términos y Condiciones", text)
        self.assertIn("Termino visible", text)
        self.assertNotIn("Termino oculto", text)
        self.assertIn("Notas", text)
        self.assertIn("Nota visible", text)


if __name__ == "__main__":
    unittest.main()
