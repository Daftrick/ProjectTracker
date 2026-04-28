import unittest

from app import app


class AdminFormsTest(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def assert_invalid_form_preserved(self, path, data, expected_text):
        response = self.client.post(path, data=data)
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("is-invalid", body)
        self.assertIn(expected_text, body)

    def test_catalogo_invalid_form_preserves_capture(self):
        self.assert_invalid_form_preserved(
            "/catalogo",
            {"nombre": "", "descripcion": "Desc capturada", "unidad": "pza", "precio": "abc"},
            "Desc capturada",
        )

    def test_proveedores_invalid_form_preserves_capture(self):
        self.assert_invalid_form_preserved(
            "/proveedores",
            {"nombre": "", "categoria": "Iluminación", "contacto": "Ana"},
            "Iluminación",
        )

    def test_fichas_invalid_form_preserves_capture(self):
        self.assert_invalid_form_preserved(
            "/fichas",
            {"tipo": "LUM", "marca": "", "modelo": "", "descripcion": "Ficha capturada"},
            "Ficha capturada",
        )

    def test_team_invalid_form_preserves_capture(self):
        self.assert_invalid_form_preserved(
            "/team",
            {"name": "", "role": "Ing. Eléctrico"},
            "Ing. Eléctrico",
        )

    def test_settings_invalid_path_preserves_capture(self):
        self.assert_invalid_form_preserved(
            "/settings",
            {"drive_projects_path": "/ruta/que/no/existe", "drive_fichas_path": ""},
            "/ruta/que/no/existe",
        )


if __name__ == "__main__":
    unittest.main()
