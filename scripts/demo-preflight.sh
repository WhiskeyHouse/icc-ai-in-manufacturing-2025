#!/usr/bin/env bash
set -euo pipefail

echo "[preflight] Checking prerequisites..."

command -v docker >/dev/null 2>&1 || { echo >&2 "Docker not found"; exit 1; }

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p secrets

missing=0
for f in secrets/GATEWAY_ADMIN_PASSWORD secrets/GIT_USER_TOKEN; do
  if [[ ! -s "$f" ]]; then
    echo "[preflight] Missing or empty: $f"
    missing=1
  fi
done

if [[ ! -f .env ]]; then
  echo "[preflight] .env missing; attempt dotenv-vault pull (optional)"
  if command -v npx >/dev/null 2>&1; then
    npx dotenv-vault@latest pull || true
  fi
fi

echo "[preflight] Docker version: $(docker --version)"
echo "[preflight] OK"



