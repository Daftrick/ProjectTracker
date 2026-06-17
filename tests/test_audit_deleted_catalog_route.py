"""Tests for the deleted catalog audit route."""

import unittest
from unittest.mock import patch


class AuditDeletedCatalogRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        app.config["TESTING"] = True
        app.config["LOGIN_DISABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        cls.client = app.test_client()

    def test_audit_deleted_catalog_loads_materiales_for_ldms(self):
        deleted_item = {
            "id": "CAT1",
            "nombre": "Interruptor eliminado",
            "descripcion": "3P 100A",
            "deleted_at": "2026-05-06",
        }

        def fake_load(key):
            data = {
                "quotes": [],
                "materiales": [
                    {
                        "id": "L1",
                        "ldm_number": "LDM-OM001-01",
                        "items": [
                            {
                                "description": "Interruptor histórico",
                                "qty": 2,
                                "precio_cot": 7.5,
                                "total_cot": 15,
                                "deleted_catalog_item": deleted_item,
                            }
                        ],
                    }
                ],
            }
            return data.get(key, [])

        with patch("tracker.routes.quotes.load", side_effect=fake_load):
            response = self.client.get("/audit/deleted-catalog")

        self.assertEqual(response.status_code, 200)
        self.assertIn("LDM-OM001-01", response.text)
        self.assertIn("Interruptor eliminado", response.text)
        self.assertIn("$7.50", response.text)
        self.assertIn("$15.00", response.text)


if __name__ == "__main__":
    unittest.main()
