#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT=${PROJECT_ROOT:-/var/www/fundraising-PythonBased}
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"
VENV_DIR="$BACKEND_DIR/.venv"
PYTHON_BIN=${PYTHON_BIN:-python3}
BACKEND_SERVICE=${BACKEND_SERVICE:-fundraising-backend}
FRONTEND_SERVICE=${FRONTEND_SERVICE:-fundraising-frontend}

log() {
  printf '\n[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*"
}

run() {
  log "Running: $*"
  "$@"
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Error: required command '$1' is not available." >&2
    exit 1
  fi
}

ensure_directory() {
  if [ ! -d "$1" ]; then
    echo "Error: expected directory '$1' does not exist." >&2
    exit 1
  fi
}

require_cmd git
require_cmd "$PYTHON_BIN"
require_cmd npm

ensure_directory "$PROJECT_ROOT"

log "Deploying project under $PROJECT_ROOT"

cd "$PROJECT_ROOT"
if [ -d .git ]; then
  run git fetch --all --prune
  CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
  run git pull --ff-only origin "$CURRENT_BRANCH"
else
  log "Warning: $PROJECT_ROOT is not a git repository. Skipping git pull."
fi

if [ -d "$BACKEND_DIR" ]; then
  cd "$BACKEND_DIR"
  if [ ! -x "$VENV_DIR/bin/python" ]; then
    log "Creating Python virtual environment in $VENV_DIR"
    run "$PYTHON_BIN" -m venv "$VENV_DIR"
  fi
  # shellcheck disable=SC1090
  source "$VENV_DIR/bin/activate"
  run pip install --upgrade pip wheel
  if [ -f requirements.txt ]; then
    run pip install -r requirements.txt
  fi
  deactivate
else
  log "Warning: backend directory $BACKEND_DIR not found. Skipping backend deployment."
fi

if [ -d "$FRONTEND_DIR" ]; then
  cd "$FRONTEND_DIR"
  export NEXT_TELEMETRY_DISABLED=1
  if [ -f package-lock.json ]; then
    run npm ci
  else
    run npm install
  fi
  run npm run build
else
  log "Warning: frontend directory $FRONTEND_DIR not found. Skipping frontend deployment."
fi

restart_service_if_exists() {
  local service_name=$1
  if command -v systemctl >/dev/null 2>&1 && systemctl list-unit-files | grep -q "^${service_name}\.service"; then
    run sudo systemctl restart "$service_name"
  else
    log "Systemd service ${service_name}.service not found. Skipping restart."
  fi
}

restart_service_if_exists "$BACKEND_SERVICE"
restart_service_if_exists "$FRONTEND_SERVICE"

log "Deployment complete."
