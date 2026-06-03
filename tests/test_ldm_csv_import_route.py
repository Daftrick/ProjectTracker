import os
import tempfile
import unittest
from unittest.mock import patch


PROJECT = {
    "id": "P1",
    "clave": "OM001",
    "name": "Proyecto CSV",
}


class LdmCsvImportRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        app.config["TESTING"] = True
        cls.client = app.test_client()

    def _fake_load(self, key):
        data = {
            "projects": [PROJECT],
            "materiales": [],
            "catalogo": [
                {
                    "id": "CAT1",
                    "nombre": "Tubo Conduit Galvanizado Pared Delgada | 27 [mm] (1\")",
                    "descripcion": "Quality",
                    "unidad": "pza",
                }
            ],
        }
        return data.get(key, [])

    def test_import_ldm_csv_blocks_missing_catalog_before_preview(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "OM001-V1-I1-20260602.csv")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("description,unit,qty\nArticulo Sin Catalogo,pza,1\n")

            with patch("tracker.routes.materials.load", side_effect=self._fake_load), \
                 patch("tracker.routes.materials._csv_path_for_project", return_value=(os.path.basename(path), path)), \
                 patch("tracker.routes.materials._csv_already_imported", return_value=None):
                response = self.client.get(f"/projects/P1/ldm/import/{os.path.basename(path)}")

        self.assertEqual(response.status_code, 302)
        self.assertIn("#tab-documentos", response.headers["Location"])
        with self.client.session_transaction() as session:
            flashes = session.get("_flashes", [])
        messages = [message for _, message in flashes]
        self.assertTrue(any("LDM CSV no se puede importar" in message for message in messages))
        self.assertTrue(any("no tiene coincidencia exacta" in message for message in messages))


if __name__ == "__main__":
    unittest.main()
