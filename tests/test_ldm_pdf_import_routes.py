import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch


PROJECT = {"id": "P1", "clave": "OM001", "name": "Proyecto demo"}
CLOSED_PROJECT = {**PROJECT, "closed_at": "2026-05-28"}
CATALOG = [{"id": "MAT-1", "nombre": "Cable THHW", "unidad": "m", "descripcion": ""}]


class LdmPdfImportRoutesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        app.config["TESTING"] = True
        app.config["LOGIN_DISABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()

    def test_upload_stores_pdf_import_payload_outside_cookie_session(self):
        from tracker.routes import materials

        result = {
            "items": [{
                "description": "Cable THHW",
                "qty": 10,
                "unit": "m",
                "precio_unit": 2.5,
                "total": 25,
                "raw_line": "10 Cable THHW m 2.50 25.00",
            }],
            "method": "procables",
            "page_count": 1,
            "meta": {"cot_number": "1608846", "fecha": "2026-05-26", "proveedor": "Procables de México"},
            "error": None,
        }

        def fake_load(key):
            return {"projects": [PROJECT]}.get(key, [])

        with tempfile.TemporaryDirectory() as root, \
             patch("tracker.routes.materials.load", side_effect=fake_load), \
             patch("tracker.routes.materials.extract_items_from_pdf", return_value=result), \
             patch("tracker.routes.materials._pdf_import_dir", return_value=root):
            response = self.client.post(
                "/projects/P1/ldm/import-pdf",
                data={"pdf_file": (io.BytesIO(b"%PDF-1.4"), "procables.pdf")},
                content_type="multipart/form-data",
            )

            self.assertEqual(response.status_code, 302)
            with self.client.session_transaction() as session:
                entry = session["pdf_import_P1"]
                self.assertIn("token", entry)
                self.assertNotIn("items", entry)
                payload_path = materials._pdf_import_path(entry["token"])

            self.assertTrue(os.path.isfile(payload_path))
            with open(payload_path, "r", encoding="utf-8") as handle:
                loaded = json.load(handle)
            self.assertEqual(loaded["items"][0]["description"], "Cable THHW")
            os.unlink(payload_path)

    def test_upload_pdf_is_blocked_when_project_is_closed(self):
        def fake_load(key):
            return {"projects": [CLOSED_PROJECT]}.get(key, [])

        with patch("tracker.routes.materials.load", side_effect=fake_load), \
             patch("tracker.routes.materials.extract_items_from_pdf") as extract:
            response = self.client.post(
                "/projects/P1/ldm/import-pdf",
                data={"pdf_file": (io.BytesIO(b"%PDF-1.4"), "procables.pdf")},
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 302)
        extract.assert_not_called()

    def test_create_pdf_import_is_blocked_when_project_is_closed(self):
        def fake_load(key):
            return {
                "projects": [CLOSED_PROJECT],
                "materiales": [],
                "catalogo": CATALOG,
            }.get(key, [])

        with self.client.session_transaction() as session:
            session["pdf_import_P1"] = {"items": [{"description": "Cable", "qty": 1}]}

        with patch("tracker.routes.materials.load", side_effect=fake_load), \
             patch("tracker.routes.materials.save") as save:
            response = self.client.post(
                "/projects/P1/ldm/import-pdf/create",
                data={"proveedor": "Procables", "catalog_id_0": "MAT-1"},
            )

        self.assertEqual(response.status_code, 302)
        save.assert_not_called()


if __name__ == "__main__":
    unittest.main()
