import os

from flask import Flask

from .domain import APP_VERSION, ALCANCES, ALCANCES_BY_ID, INFO_EXT_EXCLUDED, TASK_STATUSES, TIPOS_FICHA, currency, fdate
from .drive import migrate_folder_numbers, migrate_task_names, migrate_task_statuses
from .routes.admin import bp as admin_bp
from .routes.materials import bp as materials_bp
from .routes.projects import bp as projects_bp
from .routes.quotes import bp as quotes_bp
from .storage import BASE_DIR, DATA_DIR


def create_app():
    app = Flask(__name__, template_folder=os.path.join(BASE_DIR, "templates"))
    app.secret_key = "project-tracker-v2-2026"

    os.makedirs(DATA_DIR, exist_ok=True)
    migrate_task_statuses()
    migrate_task_names()
    migrate_folder_numbers()

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
        }

    app.register_blueprint(projects_bp)
    app.register_blueprint(quotes_bp)
    app.register_blueprint(materials_bp)
    app.register_blueprint(admin_bp)
    _register_legacy_endpoint_aliases(app)
    return app


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
