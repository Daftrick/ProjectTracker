"""Tests for exporting an existing LDM as CSV."""

import unittest
from unittest.mock import patch


PROJECT = {"id": "P1", "clave": "OM001", "name": "Proyecto demo"}
LDM = {
    "id": "L1",
    "project_id": "P1",
    "ldm_number": "LDM-OM001-01",
    "proveedor": "Proveedor Uno",
    "fecha": "2026-05-06",
    "items": [
        {
            "description": "Tubo 1/2",
            "unit": "ml",
            "qty": "2.5",
            "catalog_item_id": "CAT1",
        }
    ],
}


class MaterialsCsvExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        cls.client = app.test_client()

    def _fake_load(self, key):
        data = {
            "projects": [PROJECT],
            "materiales": [LDM],
        }
        return data.get(key, [])

    def test_exports_existing_ldm_without_creating_a_new_list(self):
        with patch("tracker.routes.materials.load", side_effect=self._fake_load), \
             patch("tracker.routes.materials.catalog_maps", return_value=({}, {})):
            response = self.client.get("/projects/P1/ldm/L1/csv")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "text/csv")
        self.assertIn('attachment; filename="LDM-OM001-01.csv"', response.headers["Content-Disposition"])

        body = response.data.decode("utf-8-sig")
        self.assertIn("description,unit,qty,catalog_item_id,proveedor,fecha,ldm_number", body)
        self.assertIn("Tubo 1/2,ml,2.5,CAT1,Proveedor Uno,2026-05-06,LDM-OM001-01", body)


if __name__ == "__main__":
    unittest.main()
