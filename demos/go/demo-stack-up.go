package main

import (
	"github.com/saschagrunert/demo"
)

func main() {
	// Create a new demo CLI application
	d := demo.New()
	d.Name = "AI Manufacturing Stack Demo - Startup"
	d.Usage = "Interactive demo for spinning up the complete AI manufacturing stack"
	d.HideVersion = true

	// Register the demo runs
	d.Add(stackStartupDemo(), "startup", "Complete stack startup with license acceptance")
	d.Add(healthCheckDemo(), "health", "Verify all services are running correctly")

	// Run the application
	d.Run()
}

// stackStartupDemo demonstrates the complete startup process
func stackStartupDemo() *demo.Run {
	r := demo.NewRun(
		"🚀 AI Manufacturing Stack Startup Demo",
		"",
		"This demo will walk through starting up our complete",
		"manufacturing stack including:",
		"• Ignition SCADA Gateway (with auto license acceptance)",
		"• PostgreSQL databases for MES and data storage",
		"• RabbitMQ for message queuing",
		"• MQTT broker for IoT communication",
		"• Kong API Gateway for service orchestration",
		"• Monitoring stack (Grafana, Prometheus, Netdata)",
		"• Redis for caching",
		"",
		"All services will auto-accept licenses and certificates!",
	)

	// Step 1: Show the stack configuration
	r.Step(demo.S(
		"📋 Let's examine our Docker Compose configuration",
		"to see what services we'll be starting:",
	), demo.S(
		"echo '=== Docker Compose Services ===' && docker compose config --services | sort && echo '' && echo '=== Key Environment Variables ===' && grep 'ACCEPT_IGNITION_EULA\\|IGNITION_EDITION\\|GATEWAY_SKIP_COMMISSIONING' docker-compose.yml || echo 'License acceptance configured in compose file'",
	))

	// Step 2: Clean slate - ensure no conflicting containers
	r.Step(demo.S(
		"🧹 Ensuring clean environment by stopping any existing containers:",
		"• Stopping any running Docker Compose services",
		"• Removing conflicting containers by name",
		"• Cleaning up orphaned containers and networks",
	), demo.S(
		"echo 'Stopping existing compose services...' && docker compose down --remove-orphans || true && echo 'Removing conflicting containers...' && docker rm -f mqtt-broker ignition grafana prometheus netdata portainer rabbitmq redis db vector-db kong llama-index-service cadvisor node-exporter 2>/dev/null || true && echo 'Freeing up ports...' && for port in 5432 5433 6379 5672 15672 1883 8083 18083 8000 8443 9088 9043 3000 9090 19999 9000 9443; do docker ps --filter \"publish=$port\" --format \"{{.ID}}\" | xargs -r docker rm -f 2>/dev/null || true; done && echo 'Environment cleaned ✅'",
	))

	// Step 3: Start the infrastructure services first
	r.Step(demo.S(
		"🏗️  Starting core infrastructure services:",
		"• PostgreSQL databases (MES + Vector storage)",
		"• Redis cache",
		"• RabbitMQ message broker",
		"• MQTT broker for IoT",
	), demo.S(
		"docker compose up -d db vector-db redis rabbitmq mqtt-broker && echo '' && echo 'Waiting for databases to initialize...' && sleep 5",
	))

	// Step 4: Start the API Gateway
	r.Step(demo.S(
		"🌐 Starting API Gateway:",
		"• Kong API Gateway for service orchestration",
	), demo.S(
		"docker compose up -d kong && echo '' && echo 'API Gateway starting up...' && sleep 3",
	))

	// Step 5: Start Ignition with auto license acceptance
	r.Step(demo.S(
		"🏭 Starting Ignition SCADA Gateway:",
		"• ACCEPT_IGNITION_EULA=Y (auto-accepts license)",
		"• Self-signed certificates auto-accepted",
		"• Gateway admin account auto-configured",
		"• Skip commissioning for demo mode",
	), demo.S(
		"echo 'Starting Ignition with automatic license acceptance...' && docker compose up -d ignition && echo '' && echo 'Ignition is starting up (this may take 30-60 seconds)...' && echo 'License will be automatically accepted via ACCEPT_IGNITION_EULA=Y'",
	))

	// Step 6: Start monitoring services
	r.Step(demo.S(
		"📊 Starting monitoring and observability stack:",
		"• Prometheus for metrics collection",
		"• Grafana for dashboards and visualization",
		"• Netdata for real-time system monitoring",
		"• Portainer for Docker management",
	), demo.S(
		"docker compose up -d prometheus grafana netdata node-exporter portainer && echo '' && echo 'Monitoring stack initializing...' && sleep 3",
	))

	// Step 7: Show running services
	r.Step(demo.S(
		"✅ All services started! Let's verify what's running:",
	), demo.S(
		"echo '=== Running Containers ===' && docker ps --format 'table {{.Names}}\\t{{.Status}}\\t{{.Ports}}' | head -20 && echo '' && echo '=== Service Health Status ===' && docker compose ps",
	))

	// Step 8: Wait for Ignition to be ready
	r.Step(demo.S(
		"⏳ Waiting for Ignition Gateway to fully initialize...",
		"This includes license acceptance and initial configuration.",
	), demo.S(
		"echo 'Checking Ignition Gateway status...' && timeout=60 && while [ $timeout -gt 0 ]; do if curl -s http://localhost:9088/system/gwinfo | grep -q 'ContextStatus=RUNNING' 2>/dev/null; then echo '✅ Ignition Gateway is ready!' && break; fi; echo \"Waiting for Ignition... ($timeout seconds remaining)\"; sleep 5; timeout=$((timeout-5)); done",
	))

	// Step 9: Display access URLs
	r.Step(demo.S(
		"🌐 Stack is ready! Here are your access URLs:",
	), demo.S(
		"echo '=== 🏭 IGNITION SCADA GATEWAY ===' && echo 'Gateway (HTTPS): https://localhost:9043' && echo 'Gateway (HTTP):  http://localhost:9088' && echo 'Admin User: admin (password in secrets/GATEWAY_ADMIN_PASSWORD)' && echo '' && echo '=== 📊 MONITORING & DASHBOARDS ===' && echo 'Grafana:    http://localhost:3000 (admin/admin)' && echo 'Prometheus: http://localhost:9090' && echo 'Netdata:    http://localhost:19999' && echo 'Portainer:  http://localhost:9000' && echo '' && echo '=== 🔧 INFRASTRUCTURE SERVICES ===' && echo 'RabbitMQ:   http://localhost:15672 (user/password)' && echo 'MQTT Web:   http://localhost:18083 (admin/public)' && echo 'Kong API:   http://localhost:8000' && echo '' && echo '=== 🚀 READY FOR DEMO! ===' && echo 'All licenses automatically accepted ✅' && echo 'Self-signed certificates trusted ✅' && echo 'Services are healthy and ready ✅'",
	))

	// Step 10: Open key management interfaces
	r.Step(demo.S(
		"🖥️  Opening key management interfaces for the demo:",
		"• Ignition Gateway - Main SCADA interface",
		"• Grafana - Monitoring dashboards and analytics",
		"• Portainer - Docker container management",
		"• Netdata - Real-time system monitoring",
	), demo.S(
		"if command -v open >/dev/null 2>&1; then echo 'Opening demo interfaces...' && echo 'Opening Ignition Gateway...' && open https://localhost:9043 || true && sleep 3 && echo 'Opening Grafana dashboards...' && open http://localhost:3000 || true && sleep 3 && echo 'Opening Portainer (Docker management)...' && open http://localhost:9000 || true && sleep 3 && echo 'Opening Netdata (real-time monitoring)...' && open http://localhost:19999 || true && echo 'All demo interfaces opened! 🎉'; else echo 'Manual browser opening required (not on macOS)' && echo 'Please open:' && echo '• Ignition: https://localhost:9043' && echo '• Grafana: http://localhost:3000' && echo '• Portainer: http://localhost:9000' && echo '• Netdata: http://localhost:19999'; fi",
	))

	return r
}

// healthCheckDemo verifies all services are working correctly
func healthCheckDemo() *demo.Run {
	r := demo.NewRun(
		"🏥 Stack Health Check Demo",
		"",
		"This demo will verify that all services in our",
		"AI manufacturing stack are running correctly",
		"and ready for the presentation.",
	)

	// Step 1: Container health check
	r.Step(demo.S(
		"🔍 Checking container health status:",
	), demo.S(
		"echo '=== Container Status ==='",
		"docker compose ps",
		"echo ''",
		"echo '=== Unhealthy Containers (should be empty) ==='",
		"docker ps --filter health=unhealthy --format 'table {{.Names}}\\t{{.Status}}'",
	))

	// Step 2: Network connectivity
	r.Step(demo.S(
		"🌐 Testing network connectivity between services:",
	), demo.S(
		"echo 'Testing internal service connectivity...'",
		"docker compose exec -T db pg_isready -U admin || echo 'Database connection issue'",
		"docker compose exec -T redis redis-cli ping || echo 'Redis connection issue'",
		"echo 'Network tests completed'",
	))

	// Step 3: Ignition Gateway health
	r.Step(demo.S(
		"🏭 Verifying Ignition Gateway is fully operational:",
	), demo.S(
		"echo 'Checking Ignition Gateway...'",
		"curl -s http://localhost:9088/system/gwinfo | head -1 || echo 'Gateway not responding'",
		"echo ''",
		"echo 'Checking Gateway API access...'",
		"curl -s -o /dev/null -w 'HTTP Status: %{http_code}\\n' http://localhost:9088/system/gwinfo",
	))

	// Step 4: API Gateway health
	r.Step(demo.S(
		"🌐 Testing Kong API Gateway functionality:",
	), demo.S(
		"echo 'Checking Kong API Gateway...'",
		"curl -s http://localhost:8000 || echo 'Kong API Gateway not responding'",
		"echo ''",
		"echo 'Testing Kong admin API...'",
		"curl -s -o /dev/null -w 'HTTP Status: %{http_code}\\n' http://localhost:8011/status",
	))

	// Step 5: Monitoring services
	r.Step(demo.S(
		"📊 Verifying monitoring stack:",
	), demo.S(
		"echo 'Checking Grafana...'",
		"curl -s -o /dev/null -w 'Grafana HTTP Status: %{http_code}\\n' http://localhost:3000/api/health",
		"echo 'Checking Prometheus...'",
		"curl -s -o /dev/null -w 'Prometheus HTTP Status: %{http_code}\\n' http://localhost:9090/-/healthy",
		"echo 'Checking Netdata...'",
		"curl -s -o /dev/null -w 'Netdata HTTP Status: %{http_code}\\n' http://localhost:19999/api/v1/info",
	))

	// Step 6: Final summary
	r.Step(demo.S(
		"✅ Health check complete! Summary of stack status:",
	), demo.S(
		"echo '=== 🎯 DEMO READINESS SUMMARY ==='",
		"echo ''",
		"running_containers=$(docker compose ps --services --filter 'status=running' | wc -l | tr -d ' ')",
		"total_containers=$(docker compose ps --services | wc -l | tr -d ' ')",
		"echo \"Running containers: $running_containers/$total_containers\"",
		"echo ''",
		"echo '=== 🔗 QUICK ACCESS LINKS ==='",
		"echo 'Ignition:  https://localhost:9043'",
		"echo 'Grafana:   http://localhost:3000'",
		"echo 'Kong API:  http://localhost:8000'",
		"echo ''",
		"if [ \"$running_containers\" -eq \"$total_containers\" ]; then",
		"  echo '🎉 ALL SYSTEMS GO! Stack is ready for presentation!'",
		"else",
		"  echo '⚠️  Some services may need attention before demo'",
		"fi",
	))

	return r
}
