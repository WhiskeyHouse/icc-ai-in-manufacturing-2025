#!/usr/bin/env bash
set -euo pipefail

echo "[open] Opening service UIs (macOS)"
if command -v open >/dev/null 2>&1; then
  open https://localhost:9043 || true
  open http://localhost:3000 || true
  open http://localhost:15672 || true
  open http://localhost:19999 || true
else
  echo "Use your browser to open:"
  echo "  https://localhost:9043  (Ignition)"
  echo "  http://localhost:3000   (Grafana)"
  echo "  http://localhost:15672  (RabbitMQ)"
  echo "  http://localhost:19999  (Netdata)"
fi



