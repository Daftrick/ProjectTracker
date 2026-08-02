"""Cliente editable por cotización + "Propuesta para" (VERSIONES.md #12).

- Cliente: campo de texto en el editor, precargado con el cliente del
  proyecto. Si no se toca, la cotización sigue sincronizada con el proyecto;
  si se edita, el texto queda fijo como override para esa cotización.
- Propuesta para: a quién va dirigida la portada del PDF, independiente del
  Cliente — "cliente" (default), "personalizado" (texto libre) o "" (vacío,
  oculta la línea).
"""

import tempfile
import unittest
from unittest.mock import patch

from tracker import create_app
from tracker.catalog import resolve_quote_client, resolve_quote_proposal_for
from tracker.pdfs import build_quote_pdf
from tracker.storage import load, save

PROJECT = {
    "id": "OVR001TEST",
    "name": "Test Override Proyecto",
    "clave": "OVR",
    "client": "Cliente Del Proyecto",
    "folder_num": "102",
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


class ResolveQuoteClientTest(unittest.TestCase):
    def test_override_wins_over_project(self):
        quote = {"client_override": "Cliente Override", "client": "Snapshot Viejo"}
        project = {"client": "Cliente Del Proyecto"}
        self.assertEqual(resolve_quote_client(quote, project), "Cliente Override")

    def test_project_wins_when_no_override(self):
        quote = {"client_override": "", "client": "Snapshot Viejo"}
        project = {"client": "Cliente Del Proyecto"}
        self.assertEqual(resolve_quote_client(quote, project), "Cliente Del Proyecto")

    def test_falls_back_to_snapshot_when_no_override_and_no_project_client(self):
        quote = {"client_override": "", "client": "Snapshot Viejo"}
        project = {"client": ""}
        self.assertEqual(resolve_quote_client(quote, project), "Snapshot Viejo")

    def test_handles_missing_quote_and_project(self):
        self.assertEqual(resolve_quote_client(None, None), "")
        self.assertEqual(resolve_quote_client({}, {}), "")


class ResolveQuoteProposalForTest(unittest.TestCase):
    def test_default_mode_missing_field_uses_client(self):
        quote = {"client_override": "", "client": ""}
        project = {"client": "Cliente Del Proyecto"}
        result = resolve_quote_proposal_for(quote, project)
        self.assertEqual(result, ("Propuesta para", "Cliente Del Proyecto"))

    def test_mode_cliente_explicit_uses_resolved_client(self):
        quote = {"proposal_for_mode": "cliente", "client_override": "Override X"}
        project = {"client": "Cliente Del Proyecto"}
        result = resolve_quote_proposal_for(quote, project)
        self.assertEqual(result, ("Propuesta para", "Override X"))

    def test_mode_personalizado_uses_custom_text(self):
        quote = {"proposal_for_mode": "personalizado", "proposal_for_custom": "Arq. Juan Pérez"}
        project = {"client": "Cliente Del Proyecto"}
        result = resolve_quote_proposal_for(quote, project)
        self.assertEqual(result, ("Propuesta para", "Arq. Juan Pérez"))

    def test_mode_personalizado_without_text_hides_line(self):
        quote = {"proposal_for_mode": "personalizado", "proposal_for_custom": ""}
        project = {"client": "Cliente Del Proyecto"}
        self.assertIsNone(resolve_quote_proposal_for(quote, project))

    def test_mode_vacio_hides_line_even_with_client(self):
        quote = {"proposal_for_mode": "", "client_override": "Alguien"}
        project = {"client": "Cliente Del Proyecto"}
        self.assertIsNone(resolve_quote_proposal_for(quote, project))

    def test_mode_cliente_without_any_client_hides_line(self):
        quote = {"proposal_for_mode": "cliente"}
        project = {"client": ""}
        self.assertIsNone(resolve_quote_proposal_for(quote, project))


class QuoteClientOverrideRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.app.config["LOGIN_DISABLED"] = True
        self.app.config["WTF_CSRF_ENABLED"] = False
        self.client = self.app.test_client()
        self._saved_projects = load("projects")
        self._saved_quotes = load("quotes")
        save("projects", [p for p in self._saved_projects if p["id"] != PROJECT["id"]] + [dict(PROJECT)])

    def tearDown(self):
        save("projects", self._saved_projects)
        save("quotes", self._saved_quotes)

    def _base_quote_form(self, **overrides):
        data = {
            "quote_type": "Proyecto",
            "date": "2026-02-01",
            "currency": "MXN",
            "tax_enabled": "on",
            "discount_pct": "0",
            "item_desc[]": "Concepto de prueba",
            "item_unit[]": "pza",
            "item_qty[]": "1",
            "item_precio_costo[]": "500",
            "item_catalog_id[]": "",
            "item_desc2[]": "",
        }
        data.update(overrides)
        return data

    def test_new_quote_with_client_unchanged_has_no_override(self):
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/new",
            data=self._base_quote_form(client="Cliente Del Proyecto"),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        quotes = [q for q in load("quotes") if q["project_id"] == PROJECT["id"]]
        self.assertEqual(len(quotes), 1)
        self.assertEqual(quotes[0]["client_override"], "")
        self._saved_quotes = [q for q in load("quotes") if q["id"] != quotes[0]["id"]]

    def test_new_quote_with_edited_client_saves_override(self):
        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/new",
            data=self._base_quote_form(client="Cliente Distinto S.A."),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        quotes = [q for q in load("quotes") if q["project_id"] == PROJECT["id"]]
        self.assertEqual(len(quotes), 1)
        self.assertEqual(quotes[0]["client_override"], "Cliente Distinto S.A.")
        self._saved_quotes = [q for q in load("quotes") if q["id"] != quotes[0]["id"]]

    def test_override_survives_later_project_client_change(self):
        self.client.post(
            f"/projects/{PROJECT['id']}/quote/new",
            data=self._base_quote_form(client="Cliente Fijo Override"),
            follow_redirects=True,
        )
        quotes = [q for q in load("quotes") if q["project_id"] == PROJECT["id"]]
        quote_id = quotes[0]["id"]

        # El proyecto cambia de cliente después.
        projects = load("projects")
        for p in projects:
            if p["id"] == PROJECT["id"]:
                p["client"] = "Cliente Nuevo Del Proyecto"
        save("projects", projects)

        response = self.client.get(
            f"/projects/{PROJECT['id']}/quote/{quote_id}/view", follow_redirects=True
        )
        text = response.get_data(as_text=True)
        self.assertIn("Cliente Fijo Override", text)
        self.assertNotIn("Cliente Nuevo Del Proyecto", text)
        self._saved_quotes = [q for q in load("quotes") if q["id"] != quote_id]

    def test_edit_quote_updates_proposal_for(self):
        self.client.post(
            f"/projects/{PROJECT['id']}/quote/new",
            data=self._base_quote_form(),
            follow_redirects=True,
        )
        quotes = [q for q in load("quotes") if q["project_id"] == PROJECT["id"]]
        quote_id = quotes[0]["id"]

        response = self.client.post(
            f"/projects/{PROJECT['id']}/quote/{quote_id}/edit",
            data=self._base_quote_form(
                proposal_for_mode="personalizado",
                proposal_for_custom="Arq. Prueba Edit",
            ),
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        updated = next(q for q in load("quotes") if q["id"] == quote_id)
        self.assertEqual(updated["proposal_for_mode"], "personalizado")
        self.assertEqual(updated["proposal_for_custom"], "Arq. Prueba Edit")
        self._saved_quotes = [q for q in load("quotes") if q["id"] != quote_id]

    def test_new_quote_form_prefills_client_with_project_client(self):
        response = self.client.get(f"/projects/{PROJECT['id']}/quote/new")
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        self.assertIn('value="Cliente Del Proyecto"', text)


class QuoteProposalForPdfTest(unittest.TestCase):
    def _company(self):
        return {
            "name": "Empresa PDF", "address": "", "email": "", "phone": "",
            "rut": "", "logo": "", "portada_color": "#000000",
        }

    def _base_quote(self, **overrides):
        quote = {
            "quote_type": "Proyecto",
            "quote_number": "COT-PROP-P01-20260801",
            "date": "2026-08-01",
            "currency": "MXN",
            "tax_rate": 16,
            "discount_pct": 0,
            "items": [{
                "description": "Item de prueba", "unit": "pza", "qty": 1,
                "price": 100, "precio_costo": 100, "total": 100,
            }],
            "subtotal": 100, "tax": 16, "total": 116,
        }
        quote.update(overrides)
        return quote

    def _render_text(self, project, quote):
        import pdfplumber
        with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
            with patch("tracker.pdfs._load_company", return_value=self._company()), \
                    patch("tracker.pdfs.quote_logo_path", return_value=None):
                build_quote_pdf(project, quote, tmp.name)
            with pdfplumber.open(tmp.name) as pdf:
                return "\n".join(page.extract_text() or "" for page in pdf.pages)

    def test_personalizado_shows_custom_addressee_not_client(self):
        project = {"name": "Proyecto Prueba", "client": "Cliente Real"}
        quote = self._base_quote(proposal_for_mode="personalizado", proposal_for_custom="Arq. Juan Pérez")
        text = self._render_text(project, quote)
        self.assertIn("Propuesta para", text)
        self.assertIn("Arq. Juan Pérez", text)
        self.assertNotIn("Cliente Real", text)

    def test_vacio_hides_propuesta_para_block(self):
        project = {"name": "Proyecto Prueba", "client": "Cliente Real"}
        quote = self._base_quote(proposal_for_mode="")
        text = self._render_text(project, quote)
        self.assertNotIn("Propuesta para", text)
        self.assertNotIn("Cliente Real", text)

    def test_cliente_mode_with_override_shows_override(self):
        project = {"name": "Proyecto Prueba", "client": "Cliente Del Proyecto"}
        quote = self._base_quote(proposal_for_mode="cliente", client_override="Cliente Fijo")
        text = self._render_text(project, quote)
        self.assertIn("Propuesta para", text)
        self.assertIn("Cliente Fijo", text)
        self.assertNotIn("Cliente Del Proyecto", text)

    def test_legacy_quote_without_proposal_fields_behaves_like_before(self):
        project = {"name": "Proyecto Prueba", "client": "Cliente Legacy"}
        quote = self._base_quote()  # sin proposal_for_mode ni client_override
        text = self._render_text(project, quote)
        self.assertIn("Propuesta para", text)
        self.assertIn("Cliente Legacy", text)


if __name__ == "__main__":
    unittest.main()
