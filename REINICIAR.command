#!/bin/zsh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

APP_PORT="${PROJECT_TRACKER_PORT:-8080}"

PIDS="$(lsof -tiTCP:"${APP_PORT}" -sTCP:LISTEN 2>/dev/null || true)"
if [[ -n "${PIDS}" ]]; then
  echo "${PIDS}" | while IFS= read -r pid; do
    if [[ -n "${pid}" ]]; then
      kill "${pid}" >/dev/null 2>&1 || true
    fi
  done
  sleep 2
fi

exec "${SCRIPT_DIR}/INICIAR.command" noopen
