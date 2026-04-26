import os

from tracker import create_app

app = create_app()


def _is_truthy(value):
    """Reconoce '1', 'true', 'yes', 'on' (case-insensitive) como verdadero."""
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    # Configuracion via variables de entorno (sin tocar el codigo):
    #   FLASK_DEBUG=1            -> auto-reload al editar archivos .py
    #   PROJECT_TRACKER_PORT=N   -> puerto alternativo (default 8080)
    debug_mode = _is_truthy(os.environ.get("FLASK_DEBUG"))
    port = int(os.environ.get("PROJECT_TRACKER_PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=debug_mode)
