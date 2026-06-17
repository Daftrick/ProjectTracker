import io
import os
import tempfile
import unittest
from unittest.mock import patch


PROJECT = {
    "id": "P1",
    "clave": "OM001",
    "name": "Proyecto CSV",
    "client": "Cliente Uno",
    "version": "V1",
}


class QuoteCsvImportRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        app.config["TESTING"] = True
        app.config["LOGIN_DISABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()

    def _fake_load(self, key):
        data = {
            "projects": [PROJECT],
            "quotes": [],
            "catalogo": [
                {
                    "id": "CAT1",
                    "nombre": "Metro Lineal de Tuberia Conduit 1",
                    "descripcion": "Omniious | Incluye instalacion",
                    "unidad": "ml",
                }
            ],
        }
        return data.get(key, [])

    def test_import_quote_csv_renders_editable_preview(self):
        csv_body = (
            "description,unit,qty,price\n"
            "#proyecto_clave,OM001,,\n"
            "#quote_type,General,,\n"
            "#fecha,2026-05-08,,\n"
            "Metro Lineal de Tuberia Conduit 1,ml,12.5,150\n"
        )
        data = {
            "quote_csv": (io.BytesIO(csv_body.encode("utf-8")), "OM001-V1-I1-COT-20260508.csv")
        }

        with patch("tracker.routes.quotes.load", side_effect=self._fake_load):
            response = self.client.post(
                "/projects/P1/quote/import",
                data=data,
                content_type="multipart/form-data",
            )

        body = response.data.decode("utf-8")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Vista previa de importación CSV", body)
        self.assertIn("COT-OM001-G01-20260508", body)
        self.assertIn("Metro Lineal de Tuberia Conduit 1", body)
        self.assertIn('action="/projects/P1/quote/new"', body)

    def test_import_quote_csv_blocks_unit_mismatch(self):
        csv_body = (
            "description,unit,qty,price\n"
            "Metro Lineal de Tuberia Conduit 1,m,12.5,150\n"
        )
        data = {
            "quote_csv": (io.BytesIO(csv_body.encode("utf-8")), "OM001-V1-I1-COT-20260508.csv")
        }

        with patch("tracker.routes.quotes.load", side_effect=self._fake_load):
            response = self.client.post(
                "/projects/P1/quote/import",
                data=data,
                content_type="multipart/form-data",
            )

        self.assertEqual(response.status_code, 302)
        self.assertIn("#tab-quote", response.headers["Location"])
        with self.client.session_transaction() as session:
            flashes = session.get("_flashes", [])
        messages = [message for _, message in flashes]
        self.assertTrue(any("CSV COT no se puede importar" in message for message in messages))
        self.assertTrue(any("unidad incompatible" in message for message in messages))

    def test_import_quote_csv_drive_blocks_catalog_validation(self):
        with tempfile.TemporaryDirectory() as root:
            project_folder = os.path.join(root, "P1")
            os.makedirs(project_folder)
            filename = "OM001-V1-I1-COT-20260508.csv"
            with open(os.path.join(project_folder, filename), "w", encoding="utf-8") as handle:
                handle.write("description,unit,qty,price\nConcepto Inexistente,pza,1,0\n")

            with patch("tracker.routes.quotes.load", side_effect=self._fake_load), \
                 patch("tracker.routes.quotes.active_drive_paths", return_value={"projects": root}), \
                 patch("tracker.routes.quotes.folder_name", return_value="P1"), \
                 patch("tracker.routes.quotes.load_config", return_value={}):
                response = self.client.get(f"/projects/P1/quote/import-drive/{filename}")

        self.assertEqual(response.status_code, 302)
        self.assertIn("#tab-quote", response.headers["Location"])
        with self.client.session_transaction() as session:
            flashes = session.get("_flashes", [])
        messages = [message for _, message in flashes]
        self.assertTrue(any("CSV COT no se puede importar" in message for message in messages))
        self.assertTrue(any("no tiene coincidencia exacta" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
