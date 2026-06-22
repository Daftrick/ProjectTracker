import os
import sqlite3
import tempfile
from unittest import TestCase
from unittest.mock import patch

from werkzeug.security import check_password_hash

import tracker.auth as auth


class DefaultAdminTests(TestCase):
    def setUp(self):
        self._db_fd, self._db_path = tempfile.mkstemp(suffix=".db")
        os.close(self._db_fd)
        self._orig_db_path = auth.AUTH_DB
        auth.AUTH_DB = self._db_path

    def tearDown(self):
        auth.AUTH_DB = self._orig_db_path
        for path in (self._db_path, f"{self._db_path}-wal", f"{self._db_path}-shm"):
            try:
                os.unlink(path)
            except FileNotFoundError:
                pass
            except PermissionError:
                pass

    def _admin_row(self, username):
        with sqlite3.connect(self._db_path) as conn:
            return conn.execute(
                "SELECT username, password_hash, role, active FROM users WHERE username=?",
                (username,),
            ).fetchone()

    def test_configured_default_admin_credentials_are_used_on_first_init(self):
        env = {
            "PROJECT_TRACKER_ADMIN_USERNAME": "owner",
            "PROJECT_TRACKER_ADMIN_PASSWORD": "owner-pass-123",
        }
        with patch.dict(os.environ, env, clear=True):
            auth.init_db()

        username, password_hash, role, active = self._admin_row("owner")
        self.assertEqual(username, "owner")
        self.assertEqual(role, "admin")
        self.assertEqual(active, 1)
        self.assertTrue(check_password_hash(password_hash, "owner-pass-123"))

    def test_configured_password_does_not_reset_existing_admin_by_default(self):
        with patch.dict(os.environ, {"PROJECT_TRACKER_ADMIN_PASSWORD": "first-pass"}, clear=True):
            auth.init_db()
        with patch.dict(os.environ, {"PROJECT_TRACKER_ADMIN_PASSWORD": "second-pass"}, clear=True):
            auth.init_db()

        _, password_hash, _, _ = self._admin_row("admin")
        self.assertTrue(check_password_hash(password_hash, "first-pass"))
        self.assertFalse(check_password_hash(password_hash, "second-pass"))

    def test_configured_password_can_reset_existing_admin_when_enabled(self):
        with patch.dict(os.environ, {"PROJECT_TRACKER_ADMIN_PASSWORD": "first-pass"}, clear=True):
            auth.init_db()
        env = {
            "PROJECT_TRACKER_ADMIN_PASSWORD": "second-pass",
            "PROJECT_TRACKER_ADMIN_RESET": "1",
        }
        with patch.dict(os.environ, env, clear=True):
            auth.init_db()

        _, password_hash, role, active = self._admin_row("admin")
        self.assertTrue(check_password_hash(password_hash, "second-pass"))
        self.assertEqual(role, "admin")
        self.assertEqual(active, 1)
