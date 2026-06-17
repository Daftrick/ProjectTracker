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

    def test_cotizador_cannot_access_empresa(self):
        self._login_as("cotizador_user")
        response = self.client.get("/empresa", follow_redirects=False)
        self.assertEqual(response.status_code, 302)

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
