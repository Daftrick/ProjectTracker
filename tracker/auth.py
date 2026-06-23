import os
import secrets
import sqlite3
import threading
from contextlib import closing
from functools import wraps

from flask import flash, redirect, url_for
from flask_login import LoginManager, UserMixin, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from .storage import DATA_DIR

AUTH_DB = os.path.join(DATA_DIR, "auth.db")
_auth_lock = threading.Lock()
_DEFAULT_ADMIN_USERNAME = "admin"

login_manager = LoginManager()
login_manager.login_view = "auth_bp.login"
login_manager.login_message = "Inicia sesión para continuar."
login_manager.login_message_category = "warning"


def init_db():
    os.makedirs(DATA_DIR, exist_ok=True)
    with sqlite3.connect(AUTH_DB) as conn:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id           INTEGER PRIMARY KEY,
                username     TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role         TEXT NOT NULL DEFAULT 'cotizador',
                active       INTEGER NOT NULL DEFAULT 1,
                created_at   TEXT DEFAULT (date('now'))
            )
        """)
        _ensure_default_admin(conn)


def _is_truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _default_admin_config():
    username = os.environ.get("PROJECT_TRACKER_ADMIN_USERNAME", _DEFAULT_ADMIN_USERNAME).strip()
    password = os.environ.get("PROJECT_TRACKER_ADMIN_PASSWORD", "Resdosco1356!#")
    reset_password = _is_truthy(os.environ.get("PROJECT_TRACKER_ADMIN_RESET"))
    return username or _DEFAULT_ADMIN_USERNAME, password, reset_password


def _ensure_default_admin(conn):
    username, configured_password, should_reset = _default_admin_config()
    row = conn.execute("SELECT id FROM users WHERE username=?", (username,)).fetchone()
    if not row:
        password = configured_password or secrets.token_urlsafe(12)
        conn.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, 'admin')",
            (username, generate_password_hash(password)),
        )
        conn.commit()
        print(
            f"\n[AUTH] Admin creado. Contraseña inicial: {password}\n"
            f"       Cámbiala desde /usuarios después del primer login.\n",
            flush=True,
        )
    elif configured_password and should_reset:
        conn.execute(
            "UPDATE users SET password_hash=?, role='admin', active=1 WHERE id=?",
            (generate_password_hash(configured_password), row[0]),
        )
        conn.commit()
        print(
            f"\n[AUTH] Admin actualizado. Usuario: {username}\n"
            "       Contrasena restablecida desde PROJECT_TRACKER_ADMIN_PASSWORD.\n",
            flush=True,
        )


class User(UserMixin):
    def __init__(self, id, username, role, active):
        self.id = id
        self.username = username
        self.role = role
        self._active = active

    @property
    def is_active(self):
        return bool(self._active)


@login_manager.user_loader
def load_user(user_id):
    with closing(sqlite3.connect(AUTH_DB)) as conn:
        row = conn.execute(
            "SELECT id, username, role, active FROM users WHERE id=?", (user_id,)
        ).fetchone()
    return User(*row) if row else None


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        from flask import current_app
        if current_app.config.get("LOGIN_DISABLED"):
            return f(*args, **kwargs)
        if not current_user.is_authenticated or current_user.role != "admin":
            flash("Acceso restringido a administradores.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated


def _db_query(sql, params=()):
    with closing(sqlite3.connect(AUTH_DB)) as conn:
        conn.row_factory = sqlite3.Row
        return conn.execute(sql, params).fetchall()


def _db_execute(sql, params=()):
    with _auth_lock:
        with closing(sqlite3.connect(AUTH_DB)) as conn:
            conn.execute(sql, params)
            conn.commit()


def get_all_users():
    return [dict(row) for row in _db_query(
        "SELECT id, username, role, active, created_at FROM users ORDER BY id"
    )]


def get_user_by_username(username):
    rows = _db_query(
        "SELECT id, username, password_hash, role, active FROM users WHERE username=?",
        (username,),
    )
    return dict(rows[0]) if rows else None


def verify_credentials(username, password):
    """Returns a User if credentials are valid and account is active, else None."""
    user_data = get_user_by_username(username)
    if (
        user_data
        and check_password_hash(user_data["password_hash"], password)
        and user_data["active"]
    ):
        return User(user_data["id"], user_data["username"], user_data["role"], user_data["active"])
    return None


def create_user(username, password, role="cotizador"):
    _db_execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), role),
    )


def set_user_active(user_id, active):
    _db_execute("UPDATE users SET active=? WHERE id=?", (int(bool(active)), user_id))


def reset_user_password(user_id, new_password):
    _db_execute(
        "UPDATE users SET password_hash=? WHERE id=?",
        (generate_password_hash(new_password), user_id),
    )


def init_auth(app):
    init_db()
    login_manager.init_app(app)
