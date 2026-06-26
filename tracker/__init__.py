import os

from flask import Flask, current_app, redirect, request, url_for
from flask_login import current_user
from .auth import init_auth
from .catalog import migrate_catalog_disciplina, migrate_catalog_fields, migrate_quote_approval
from .company_config import get_company
from .domain import APP_VERSION, ALCANCES, ALCANCES_BY_ID, INFO_EXT_EXCLUDED, STAGES, TASK_STATUSES, TIPOS_FICHA, currency, fdate
from .routes.admin import bp as admin_bp
from .routes.auth_routes import bp as auth_bp
from .routes.materials import bp as materials_bp
from .routes.projects import bp as projects_bp
from .routes.quotes import bp as quotes_bp
from .routes.quotes_mobile import bp as quotes_mobile_bp
from .extensions import csrf
from .storage import BASE_DIR, DATA_DIR, load, save

_LOGIN_EXEMPT = {"auth_bp.login", "auth_bp.logout", "static"}
_DEFAULT_SECRET_KEY = "project-tracker-v2-2026"
_PRODUCTION_ENV_VARS = (
    "PROJECT_TRACKER_ENV",
    "FLASK_ENV",
    "APP_ENV",
    "ENV",
    "RAILWAY_ENVIRONMENT_NAME",
)


def _is_truthy(value):
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _is_production_environment():
    if _is_truthy(os.environ.get("PROJECT_TRACKER_PRODUCTION")):
        return True
    for name in _PRODUCTION_ENV_VARS:
        value = str(os.environ.get(name, "")).strip().lower()
        if value in {"production", "prod"}:
            return True
    return False


def _requires_configured_secret_key(secret_key):
    return secret_key == _DEFAULT_SECRET_KEY and _is_production_environment()


def create_app():
    app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))

    import sys
    secret_key = os.environ.get("FLASK_SECRET_KEY") or os.environ.get("SECRET_KEY", _DEFAULT_SECRET_KEY)
    app.secret_key = secret_key
    _in_tests = "unittest" in sys.modules or "pytest" in sys.modules
    if not _in_tests and _requires_configured_secret_key(secret_key):
        raise RuntimeError(
            "Set FLASK_SECRET_KEY env var before deploying to production"
        )

    csrf.init_app(app)
    init_auth(app)

    os.makedirs(DATA_DIR, exist_ok=True)
    migrate_catalog_fields()
    migrate_catalog_disciplina()
    _migrate_quote_approval()

    app.add_template_filter(fdate, "fdate")
    app.add_template_filter(currency, "currency")

    @app.context_processor
    def inject_globals():
        return {
            "app_version": APP_VERSION,
            "alcances_catalog": ALCANCES,
            "alcances_by_id": ALCANCES_BY_ID,
            "task_statuses": TASK_STATUSES,
            "tipos_ficha": TIPOS_FICHA,
            "info_ext_excluded": INFO_EXT_EXCLUDED,
            "stages": STAGES,
            "company": get_company(),
        }

    @app.before_request
    def _require_login():
        if current_app.config.get("LOGIN_DISABLED"):
            return
        endpoint = request.endpoint or ""
        if endpoint in _LOGIN_EXEMPT or endpoint.startswith("static"):
            return
        if not current_user.is_authenticated:
            return redirect(url_for("auth_bp.login", next=request.url))

    app.register_blueprint(projects_bp)
    app.register_blueprint(quotes_bp)
    app.register_blueprint(quotes_mobile_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(auth_bp)
    _register_legacy_endpoint_aliases(app)
    return app


def _migrate_quote_approval():
    """Migración idempotente: asigna approval_status a cotizaciones existentes."""
    quotes = load("quotes")
    if migrate_quote_approval(quotes):
        save("quotes", quotes)


def _register_legacy_endpoint_aliases(app):
    rules = list(app.url_map.iter_rules())
    for rule in rules:
        if "." not in rule.endpoint:
            continue
        _, legacy_endpoint = rule.endpoint.split(".", 1)
        if legacy_endpoint in app.view_functions:
            continue
        methods = sorted(method for method in rule.methods if method not in {"HEAD", "OPTIONS"})
        app.add_url_rule(rule.rule, endpoint=legacy_endpoint, view_func=app.view_functions[rule.endpoint], methods=methods)
