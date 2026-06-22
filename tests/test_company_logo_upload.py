import io
import os
import tempfile
from unittest import TestCase
from unittest.mock import patch


class CompanyLogoUploadTests(TestCase):
    def setUp(self):
        from app import app

        app.config["TESTING"] = True
        app.config["LOGIN_DISABLED"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        self.client = app.test_client()

    def test_upload_accepts_real_png_and_saves_company_logo(self):
        png_content = b"\x89PNG\r\n\x1a\n" + b"0" * 12
        with tempfile.TemporaryDirectory() as uploads_dir, \
             patch("tracker.routes.admin._logo_upload_dir", return_value=uploads_dir), \
             patch("tracker.company_config.get_company", return_value={"name": "ACME", "logo": ""}), \
             patch("tracker.company_config.save_company") as mock_save:
            response = self.client.post(
                "/empresa/logo",
                data={"logo": (io.BytesIO(png_content), "brand.png")},
                content_type="multipart/form-data",
            )

            self.assertEqual(response.status_code, 302)
            self.assertTrue(os.path.isfile(os.path.join(uploads_dir, "logo.png")))
            mock_save.assert_called_once_with({"name": "ACME", "logo": "uploads/logo.png"})

    def test_empresa_preview_uses_static_url_with_logo_version(self):
        company = {"name": "ACME", "logo": "uploads/logo.jpg", "address": "", "rut": ""}
        with patch("tracker.company_config.get_company", return_value=company), \
             patch("tracker.routes.admin._company_logo_version", return_value="123"):
            response = self.client.get("/empresa")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"/static/uploads/logo.jpg?v=123", response.data)

    def test_upload_rejects_svg(self):
        with tempfile.TemporaryDirectory() as uploads_dir, \
             patch("tracker.routes.admin._logo_upload_dir", return_value=uploads_dir), \
             patch("tracker.company_config.save_company") as mock_save:
            response = self.client.post(
                "/empresa/logo",
                data={"logo": (io.BytesIO(b"<svg></svg>"), "brand.svg")},
                content_type="multipart/form-data",
                follow_redirects=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertFalse(os.path.exists(os.path.join(uploads_dir, "logo.svg")))
            mock_save.assert_not_called()

    def test_upload_rejects_extension_that_does_not_match_content(self):
        jpeg_content = b"\xff\xd8\xff" + b"0" * 12
        with tempfile.TemporaryDirectory() as uploads_dir, \
             patch("tracker.routes.admin._logo_upload_dir", return_value=uploads_dir), \
             patch("tracker.company_config.save_company") as mock_save:
            response = self.client.post(
                "/empresa/logo",
                data={"logo": (io.BytesIO(jpeg_content), "brand.png")},
                content_type="multipart/form-data",
                follow_redirects=True,
            )

            self.assertEqual(response.status_code, 200)
            self.assertFalse(os.listdir(uploads_dir))
            mock_save.assert_not_called()
