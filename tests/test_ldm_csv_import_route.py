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
        app.config["LOGIN_DISABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = False
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


if __name__ == "__main__":
    unittest.main()
