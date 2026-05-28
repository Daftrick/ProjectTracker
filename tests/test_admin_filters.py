"""Pruebas de filtros administrativos para proveedores y fichas."""

import unittest
from unittest.mock import patch

from tracker.admin_filters import filter_fichas, filter_proveedores, list_field_values


class AdminFilterHelpersTest(unittest.TestCase):
    def test_filters_proveedores_by_tokens_and_category(self):
        proveedores = [
            {
                "nombre": "Electrica del Norte",
                "categoria": "Iluminacion",
                "contacto": "Ana Lopez",
                "email": "ana@example.com",
                "telefono": "55",
                "notas": "Entrega rapida",
            },
            {
                "nombre": "Cable Pro",
                "categoria": "Conductores",
                "contacto": "Luis",
                "email": "",
                "telefono": "",
                "notas": "",
            },
        ]

        result = filter_proveedores(proveedores, q="ana entrega", categoria="iluminación")

        self.assertEqual([item["nombre"] for item in result], ["Electrica del Norte"])

    def test_filters_fichas_by_text_type_and_link_status(self):
        fichas = [
            {
                "code": "LUM-ACME-L100",
                "tipo": "LUM",
                "marca": "ACME",
                "modelo": "L100",
                "descripcion": "Luminaria lineal",
                "filename": "FT-LUM-ACME-L100.pdf",
                "projects": ["P1"],
            },
            {
                "code": "PANEL-SQD-QO",
                "tipo": "PANEL",
                "marca": "SQD",
                "modelo": "QO",
                "descripcion": "Tablero",
                "filename": "",
                "projects": [],
            },
        ]

        result = filter_fichas(fichas, q="lineal acme", tipo="lum", vinculo="con-proyecto")

        self.assertEqual([item["code"] for item in result], ["LUM-ACME-L100"])

    def test_list_field_values_returns_unique_sorted_values(self):
        result = list_field_values(
            [
                {"categoria": "Tableros"},
                {"categoria": "tableros"},
                {"categoria": "Iluminacion"},
                {"categoria": ""},
            ],
            "categoria",
        )

        self.assertEqual(result, ["Iluminacion", "Tableros"])


class AdminFilterRouteTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from app import app

        cls.client = app.test_client()

    def _fake_load(self, key):
        data = {
            "proveedores": [
                {
                    "id": "P1",
                    "nombre": "Electrica del Norte",
                    "categoria": "Iluminacion",
                    "contacto": "Ana Lopez",
                    "email": "ana@example.com",
                    "telefono": "55",
                    "notas": "Entrega rapida",
                },
                {
                    "id": "P2",
                    "nombre": "Cable Pro",
                    "categoria": "Conductores",
                    "contacto": "Luis",
                    "email": "",
                    "telefono": "",
                    "notas": "",
                },
            ],
            "fichas": [
                {
                    "id": "F1",
                    "code": "LUM-ACME-L100",
                    "tipo": "LUM",
                    "marca": "ACME",
                    "modelo": "L100",
                    "descripcion": "Luminaria lineal",
                    "filename": "FT-LUM-ACME-L100.pdf",
                    "projects": ["PR1"],
                    "notes": "",
                },
                {
                    "id": "F2",
                    "code": "PANEL-SQD-QO",
                    "tipo": "PANEL",
                    "marca": "SQD",
                    "modelo": "QO",
                    "descripcion": "Tablero",
                    "filename": "",
                    "projects": [],
                    "notes": "",
                },
            ],
            "projects": [{"id": "PR1", "clave": "OM001"}],
            "catalogo": [],
            "bundles": [],
            "team": [],
            "quotes": [],
            "materiales": [],
        }
        return data.get(key, [])

    def test_proveedores_route_filters_by_category(self):
        with patch("tracker.routes.admin.load", side_effect=self._fake_load):
            response = self.client.get("/proveedores?categoria=Conductores")

        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Cable Pro", body)
        self.assertNotIn("Electrica del Norte", body)

    def test_fichas_route_filters_by_text_and_unlinked_status(self):
        with patch("tracker.routes.admin.load", side_effect=self._fake_load):
            response = self.client.get("/fichas?q=panel&vinculo=sin-proyecto")

        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("PANEL-SQD-QO", body)
        self.assertNotIn("LUM-ACME-L100", body)


if __name__ == "__main__":
    unittest.main()
