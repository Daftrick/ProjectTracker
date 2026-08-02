import os
import sqlite3
import tempfile
import unittest


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        from app import app
        from tracker.auth import AUTH_DB, init_db

        self._orig_auth_db = os.environ.get("_TEST_AUTH_DB")

        # Use a temporary database for each test
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        import tracker.auth as _auth_mod
        self._orig_db_path = _auth_mod.AUTH_DB
        _auth_mod.AUTH_DB = self._db_path

        init_db()

        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["LOGIN_DISABLED"] = False  # We want real auth for these tests
        app.config["SECRET_KEY"] = "test-secret-key"
        self.client = app.test_client()
        self.app = app

    def tearDown(self):
        import tracker.auth as _auth_mod
        _auth_mod.AUTH_DB = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def _create_user(self, username, password, role="cotizador"):
        from tracker.auth import create_user
        create_user(username, password, role)

    def _login(self, username, password):
        return self.client.post(
            "/login",
            data={"username": username, "password": password},
            follow_redirects=False,
        )

    def test_login_page_returns_200(self):
        response = self.client.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Iniciar sesi", response.data)

    def test_unauthenticated_redirect_to_login(self):
        response = self.client.get("/", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_login_success_redirects_to_dashboard(self):
        self._create_user("testuser", "password123", "cotizador")
        response = self._login("testuser", "password123")
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("/login", response.headers.get("Location", ""))

    def test_login_wrong_password_shows_error(self):
        self._create_user("testuser", "password123", "cotizador")
        response = self.client.post(
            "/login",
            data={"username": "testuser", "password": "wrongpassword"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Credenciales incorrectas", response.data)

    def test_login_unknown_user_same_error(self):
        # Should show the same error message regardless of whether user exists
        response = self.client.post(
            "/login",
            data={"username": "nobody", "password": "whatever"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Credenciales incorrectas", response.data)

    def test_inactive_user_cannot_login(self):
        from tracker.auth import set_user_active, _db_query
        self._create_user("inactive_user", "password123", "cotizador")
        rows = _db_query("SELECT id FROM users WHERE username='inactive_user'")
        user_id = rows[0]["id"]
        set_user_active(user_id, False)
        response = self.client.post(
            "/login",
            data={"username": "inactive_user", "password": "password123"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Credenciales incorrectas", response.data)

    def test_logout_clears_session(self):
        self._create_user("testuser2", "password123", "cotizador")
        self._login("testuser2", "password123")
        response = self.client.post("/logout", follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        # After logout, dashboard should redirect to login
        response2 = self.client.get("/", follow_redirects=False)
        self.assertEqual(response2.status_code, 302)
        self.assertIn("/login", response2.headers["Location"])


class AdminRequiredTestCase(unittest.TestCase):
    def setUp(self):
        from app import app
        import tracker.auth as _auth_mod
        from tracker.auth import init_db, create_user

        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        self._orig_db_path = _auth_mod.AUTH_DB
        _auth_mod.AUTH_DB = self._db_path
        init_db()

        create_user("cotizador_user", "pass123", "cotizador")
        create_user("admin_user", "pass123", "admin")

        app.config["TESTING"] = True
        app.config["WTF_CSRF_ENABLED"] = False
        app.config["LOGIN_DISABLED"] = False
        app.config["SECRET_KEY"] = "test-secret-key"
        self.client = app.test_client()

    def tearDown(self):
        import tracker.auth as _auth_mod
        _auth_mod.AUTH_DB = self._orig_db_path
        os.close(self._db_fd)
        os.unlink(self._db_path)

    def _login_as(self, username):
        self.client.post(
            "/login",
            data={"username": username, "password": "pass123"},
        )

    def test_cotizador_cannot_access_users(self):
        self._login_as("cotizador_user")
        response = self.client.get("/usuarios", follow_redirects=False)
        self.assertEqual(response.status_code, 302)

    def test_admin_can_access_empresa(self):
        self._login_as("admin_user")
        response = self.client.get("/empresa", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_admin_can_access_users(self):
        self._login_as("admin_user")
        response = self.client.get("/usuarios", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_cotizador_can_add_catalog_item_via_form(self):
        # Dar de alta conceptos nuevos en el catálogo debe estar disponible
        # para todos los usuarios autenticados, no sólo administradores.
        self._login_as("cotizador_user")
        response = self.client.post(
            "/catalogo",
            data={"nombre": "Concepto de prueba", "descripcion": "", "unidad": "pza", "precio": "10"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("agregado al cat", response.get_data(as_text=True))

    def test_cotizador_can_add_catalog_item_via_api(self):
        self._login_as("cotizador_user")
        response = self.client.post(
            "/api/catalogo/add",
            json={"nombre": "Concepto API", "unidad": "pza", "precio": 5},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.get_json()["nombre"], "Concepto API")

    def _assert_no_admin_block(self, response):
        body = response.get_data(as_text=True)
        self.assertNotIn("Acceso restringido a administradores", body)

    def test_cotizador_can_edit_and_delete_catalog_items(self):
        # Sólo la edición de usuarios y de la empresa se quedan restringidas
        # a admin — el resto del catálogo (editar/eliminar/bulk) es de todos.
        self._login_as("cotizador_user")
        item_id = self.client.post(
            "/api/catalogo/add", json={"nombre": "Editable", "unidad": "pza", "precio": 1}
        ).get_json()["id"]
        response = self.client.post(
            f"/catalogo/{item_id}/edit",
            data={"nombre": "Editado", "descripcion": "", "unidad": "pza", "precio": "2"},
            follow_redirects=True,
        )
        self._assert_no_admin_block(response)
        response = self.client.post(f"/catalogo/{item_id}/delete", follow_redirects=True)
        self._assert_no_admin_block(response)
        response = self.client.post(
            "/api/catalogo/bulk-delete", json={"ids": ["nonexistent"]}
        )
        self._assert_no_admin_block(response)

    def test_cotizador_can_manage_proveedores_fichas_team(self):
        self._login_as("cotizador_user")
        response = self.client.post(
            "/proveedores",
            data={"nombre": "Proveedor de prueba", "categoria": "", "contacto": ""},
            follow_redirects=True,
        )
        self._assert_no_admin_block(response)
        response = self.client.post("/proveedores/nonexistent/edit", data={"nombre": "X"}, follow_redirects=True)
        self._assert_no_admin_block(response)
        response = self.client.post("/proveedores/nonexistent/delete", follow_redirects=True)
        self._assert_no_admin_block(response)

        response = self.client.post("/fichas/nonexistent/delete", follow_redirects=True)
        self._assert_no_admin_block(response)

        response = self.client.post(
            "/team", data={"name": "Miembro de prueba", "role": "Ing."}, follow_redirects=True
        )
        self._assert_no_admin_block(response)
        response = self.client.post("/team/nonexistent/delete", follow_redirects=True)
        self._assert_no_admin_block(response)

    def test_cotizador_can_delete_project_and_approve_quote(self):
        self._login_as("cotizador_user")
        response = self.client.post("/projects/nonexistent/delete", follow_redirects=True)
        self._assert_no_admin_block(response)
        response = self.client.post("/projects/nonexistent/quote/nonexistent/approve", follow_redirects=True)
        self._assert_no_admin_block(response)
        self.assertIn("Cotización no encontrada", response.get_data(as_text=True))

    def test_cotizador_can_access_system_pages_except_admin_only_ones(self):
        self._login_as("cotizador_user")
        for path in (
            "/project-templates",
            "/import-json",
            "/alcances",
            "/disciplinas",
            "/audit/deleted-catalog",
        ):
            response = self.client.get(path, follow_redirects=True)
            self.assertNotEqual(response.status_code, 404, path)
            self._assert_no_admin_block(response)
        # Exportar datos, reiniciar app y usuarios se mantienen exclusivos de admin.
        for path in ("/export", "/reset-data", "/usuarios"):
            response = self.client.get(path, follow_redirects=False)
            self.assertEqual(response.status_code, 302, path)

    def test_admin_can_access_export_and_reset_data(self):
        self._login_as("admin_user")
        response = self.client.get("/export", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "application/zip")
        response = self.client.get("/reset-data", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_cotizador_can_view_empresa_but_only_edit_address(self):
        self._login_as("cotizador_user")
        response = self.client.get("/empresa", follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self._assert_no_admin_block(response)

        response = self.client.post(
            "/empresa",
            data={
                "name": "Nombre hackeado",
                "address": "Dirección nueva 123",
                "email": "hack@example.com",
                "portada_color": "#123456",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        from tracker.company_config import get_company
        company = get_company()
        self.assertEqual(company.get("address"), "Dirección nueva 123")
        self.assertNotEqual(company.get("name"), "Nombre hackeado")
        self.assertNotEqual(company.get("email"), "hack@example.com")

    def test_admin_can_edit_all_empresa_fields(self):
        self._login_as("admin_user")
        response = self.client.post(
            "/empresa",
            data={
                "name": "Empresa Admin",
                "address": "Otra dirección",
                "email": "admin@example.com",
                "portada_color": "#123456",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        from tracker.company_config import get_company
        company = get_company()
        self.assertEqual(company.get("name"), "Empresa Admin")
        self.assertEqual(company.get("email"), "admin@example.com")
