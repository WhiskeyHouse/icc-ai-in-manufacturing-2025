#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

./scripts/demo-preflight.sh

echo "[up] Starting containers..."
docker compose up -d

echo "[up] Containers running:"
docker ps | cat

echo "[up] Opening UIs (macOS)"
if command -v open >/dev/null 2>&1; then
  open https://localhost:9043 || true
  open http://localhost:3000 || true
  open http://localhost:15672 || true
  open http://localhost:19999 || true
fi

echo "[up] Done"



