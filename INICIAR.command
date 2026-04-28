#!/bin/zsh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

APP_PORT="${PROJECT_TRACKER_PORT:-8080}"
APP_URL="http://localhost:${APP_PORT}"
OPEN_BROWSER="1"

if [[ "${1:-}" == "noopen" ]]; then
  OPEN_BROWSER="0"
fi

if lsof -nP -iTCP:"${APP_PORT}" -sTCP:LISTEN >/dev/null 2>&1; then
  exit 0
fi

if command -v python3 >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python3)"
elif command -v python >/dev/null 2>&1; then
  PYTHON_BIN="$(command -v python)"
else
  osascript -e 'display alert "Python no encontrado" message "Instala Python 3 para abrir Project Tracker en macOS."' >/dev/null 2>&1 || true
  echo "ERROR: Python 3 no encontrado."
  exit 1
fi

"${PYTHON_BIN}" -m pip install --disable-pip-version-check -r requirements.txt --quiet

if [[ "${OPEN_BROWSER}" == "1" ]]; then
  (
    sleep 3
    open "${APP_URL}" >/dev/null 2>&1
  ) &
fi

exec "${PYTHON_BIN}" app.py
