#!/bin/zsh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

APP_PORT="${PROJECT_TRACKER_PORT:-8080}"
APP_URL="http://localhost:${APP_PORT}"

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  osascript -e 'display alert "Python no encontrado" message "Instala Python 3 para abrir Project Tracker en macOS."' >/dev/null 2>&1 || true
  echo "ERROR: Python 3 no encontrado."
  exit 1
fi

export FLASK_DEBUG=1

echo "============================================="
echo "   Project Tracker - MODO DEBUG"
echo "   Auto-reload activo: edita .py y se recarga"
echo "   Los errores se muestran aqui"
echo "============================================="
echo

"${PYTHON_BIN}" -m pip install --disable-pip-version-check -r requirements.txt --quiet

echo "Servidor en ${APP_URL}"
echo "Para detener: Ctrl+C"
echo

(
  sleep 3
  open "${APP_URL}" >/dev/null 2>&1
) &

exec "${PYTHON_BIN}" app.py
