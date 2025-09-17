#!/bin/bash

# Test script to verify container connectivity
echo "Testing container connectivity..."

# Function to test if a service is reachable
test_service() {
    local service_name=$1
    local port=$2
    echo -n "Testing $service_name connectivity... "
    
    if docker exec -it $(docker ps -q -f name=portainer) nc -z $service_name $port 2>/dev/null; then
        echo "✅ SUCCESS"
    else
        echo "❌ FAILED"
    fi
}

# Wait for containers to be up
echo "Waiting for containers to start..."
sleep 10

# Test connectivity from Portainer to other services
echo "Testing connectivity from Portainer to other services:"
test_service "mqtt-broker" 1883
test_service "redis" 6379
test_service "db" 5432
test_service "vector-db" 5432
test_service "rabbitmq" 5672
test_service "mongo" 27017
test_service "prometheus" 9090
test_service "grafana" 3000
test_service "kong" 8000

echo ""
echo "Network connectivity test completed!"
echo "You can now access:"
echo "- MQTT Broker Web UI: http://localhost:${MQTT_WEB_UI_PORT:-18083}"
echo "- Portainer: http://localhost:9000"
echo "- Grafana: http://localhost:3000"
echo "- Prometheus: http://localhost:9090"
echo "- RabbitMQ Management: http://localhost:15672"


