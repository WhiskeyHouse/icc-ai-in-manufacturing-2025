#!/usr/bin/env bash
set -euo pipefail

echo "🧹 Demo Cleanup - Removing all conflicting containers..."

# Stop and remove all compose services
echo "Stopping Docker Compose services..."
docker compose down --remove-orphans || true

# Force remove any containers that might conflict by name
echo "Removing conflicting containers by name..."
docker rm -f \
  mqtt-broker \
  ignition \
  grafana \
  prometheus \
  netdata \
  portainer \
  rabbitmq \
  redis \
  db \
  vector-db \
  kong \
  llama-index-service \
  cadvisor \
  node-exporter \
  2>/dev/null || true

# Clean up any dangling containers from this project
echo "Removing project containers..."
docker ps -a --filter "name=icc-ai-in-manufacturing-2025" --format "{{.ID}}" | xargs -r docker rm -f || true

# Kill any Docker containers using our required ports (but not system processes)
echo "Freeing up required ports..."
ports_to_free="5432 5433 6379 5672 15672 1883 8083 18083 8000 8443 9088 9043 3000 9090 19999 9000 9443"
for port in $ports_to_free; do
  # Find and kill any containers using these ports
  docker ps --filter "publish=$port" --format "{{.ID}}" | xargs -r docker rm -f 2>/dev/null || true
  # Note: We don't kill system processes to avoid breaking Docker/OrbStack
done

echo "✅ Cleanup complete! All ports freed and ready for fresh demo startup."
echo ""
echo "Now you can run:"
echo "  ./run-demo.sh auto startup"
echo "  or"
echo "  ./run-demo.sh up startup"
