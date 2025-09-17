package main

import (
	"github.com/saschagrunert/demo"
)

func main() {
	// Create a new demo CLI application
	d := demo.New()
	d.Name = "AI Manufacturing Stack Demo - Shutdown"
	d.Usage = "Interactive demo for gracefully shutting down the AI manufacturing stack"
	d.HideVersion = true

	// Register the demo runs
	d.Add(gracefulShutdownDemo(), "shutdown", "Graceful shutdown of all stack services")
	d.Add(cleanupDemo(), "cleanup", "Complete cleanup including volumes and networks")

	// Run the application
	d.Run()
}

// gracefulShutdownDemo demonstrates proper shutdown sequence
func gracefulShutdownDemo() *demo.Run {
	r := demo.NewRun(
		"🛑 AI Manufacturing Stack Graceful Shutdown",
		"",
		"This demo will walk through properly shutting down",
		"our AI-powered manufacturing stack in the correct",
		"order to prevent data loss and ensure clean shutdown:",
		"",
		"• Stop monitoring services first",
		"• Gracefully shutdown Ignition Gateway",
		"• Stop AI and API services",
		"• Finally stop infrastructure (databases, queues)",
		"",
		"Data will be preserved in Docker volumes for next startup.",
	)

	// Step 1: Show current status
	r.Step(demo.S(
		"📊 First, let's see what's currently running:",
	), demo.S(
		"echo '=== Current Stack Status ==='",
		"docker compose ps",
		"echo ''",
		"echo '=== Running Services Count ==='",
		"running=$(docker compose ps --services --filter 'status=running' | wc -l | tr -d ' ')",
		"total=$(docker compose ps --services | wc -l | tr -d ' ')",
		"echo \"Active services: $running/$total\"",
	))

	// Step 2: Stop monitoring services first (least critical)
	r.Step(demo.S(
		"📉 Stopping monitoring and observability services:",
		"These are non-critical and can be stopped first",
	), demo.S(
		"echo 'Stopping monitoring stack...'",
		"docker compose stop grafana prometheus netdata cadvisor node-exporter portainer",
		"echo 'Monitoring services stopped ✅'",
	))

	// Step 3: Stop Ignition Gateway (needs graceful shutdown)
	r.Step(demo.S(
		"🏭 Gracefully shutting down Ignition Gateway:",
		"This ensures proper project saves and license cleanup",
	), demo.S(
		"echo 'Stopping Ignition Gateway gracefully...'",
		"docker compose stop ignition",
		"echo 'Waiting for Ignition to complete shutdown...'",
		"sleep 5",
		"echo 'Ignition Gateway stopped ✅'",
	))

	// Step 4: Stop AI and API services
	r.Step(demo.S(
		"🤖 Stopping AI and API services:",
		"• LlamaIndex RAG service",
		"• Kong API Gateway",
	), demo.S(
		"echo 'Stopping AI and API services...'",
		"docker compose stop llama-index-service kong",
		"echo 'AI and API services stopped ✅'",
	))

	// Step 5: Stop message brokers
	r.Step(demo.S(
		"📨 Stopping message brokers and communication:",
		"• RabbitMQ message queue",
		"• MQTT broker for IoT",
	), demo.S(
		"echo 'Stopping message brokers...'",
		"docker compose stop rabbitmq mqtt-broker",
		"echo 'Message brokers stopped ✅'",
	))

	// Step 6: Stop databases and cache (most critical, last to stop)
	r.Step(demo.S(
		"💾 Finally, stopping databases and cache:",
		"These are stopped last to ensure data integrity",
	), demo.S(
		"echo 'Stopping databases and cache...'",
		"docker compose stop redis vector-db db",
		"echo 'Databases and cache stopped ✅'",
	))

	// Step 7: Verify all services are stopped
	r.Step(demo.S(
		"✅ Verifying complete shutdown:",
	), demo.S(
		"echo '=== Final Status Check ==='",
		"docker compose ps",
		"echo ''",
		"running=$(docker compose ps --services --filter 'status=running' | wc -l | tr -d ' ')",
		"if [ \"$running\" -eq 0 ]; then",
		"  echo '🎉 All services successfully stopped!'",
		"  echo 'Data preserved in Docker volumes for next startup'",
		"else",
		"  echo \"⚠️  $running services still running\"",
		"  echo 'You may need to force stop remaining services'",
		"fi",
	))

	// Step 8: Show preserved data
	r.Step(demo.S(
		"💾 Data preservation status:",
		"All your data is safely stored in Docker volumes",
	), demo.S(
		"echo '=== Preserved Docker Volumes ==='",
		"docker volume ls | grep -E '(postgres|redis|gw-data|grafana|prometheus)' || echo 'No matching volumes found'",
		"echo ''",
		"echo '=== Volume Storage Usage ==='",
		"docker system df -v | grep -A 20 'Local Volumes:' | head -10 || echo 'Volume info not available'",
		"echo ''",
		"echo '✅ All data preserved for next startup!'",
		"echo '   Use ./demo-stack-up to restart the stack'",
	))

	return r
}

// cleanupDemo provides complete cleanup including volumes
func cleanupDemo() *demo.Run {
	r := demo.NewRun(
		"🧹 Complete Stack Cleanup Demo",
		"",
		"⚠️  WARNING: This demo will completely remove",
		"ALL data including Docker volumes!",
		"",
		"Use this for:",
		"• Complete environment reset",
		"• Troubleshooting persistent issues",
		"• Preparing for fresh demo environment",
		"",
		"🚨 ALL DATA WILL BE LOST! 🚨",
	)

	// Step 1: Confirmation and current state
	r.Step(demo.S(
		"⚠️  DANGER ZONE: Complete cleanup preparation",
		"This will remove ALL data permanently!",
	), demo.S(
		"echo '🚨 COMPLETE CLEANUP MODE 🚨'",
		"echo 'This will permanently delete:'",
		"echo '• All containers'",
		"echo '• All Docker volumes (databases, configs, logs)'",
		"echo '• All Docker networks'",
		"echo '• All cached data'",
		"echo ''",
		"echo 'Current volumes that will be deleted:'",
		"docker volume ls | grep -E '(whiskeyhouse|postgres|redis|gw-data|grafana|prometheus|mqtt|rabbitmq)' || echo 'No matching volumes'",
	))

	// Step 2: Stop all services
	r.Step(demo.S(
		"🛑 Stopping all services (forced):",
	), demo.S(
		"echo 'Force stopping all containers...'",
		"docker compose down --timeout 10",
		"echo 'All containers stopped'",
	))

	// Step 3: Remove containers and networks
	r.Step(demo.S(
		"🗑️  Removing containers and networks:",
	), demo.S(
		"echo 'Removing containers, networks, and orphans...'",
		"docker compose down --remove-orphans --rmi local",
		"echo 'Containers and networks removed ✅'",
	))

	// Step 4: Remove all volumes (DANGEROUS!)
	r.Step(demo.S(
		"💥 REMOVING ALL VOLUMES (PERMANENT DATA LOSS!):",
		"This step cannot be undone!",
	), demo.S(
		"echo 'Removing ALL Docker volumes...'",
		"docker compose down --volumes",
		"echo ''",
		"echo 'Removing any remaining project volumes...'",
		"docker volume ls -q | grep -E '(whiskeyhouse|icc-ai)' | xargs -r docker volume rm || true",
		"echo 'All volumes removed ✅'",
	))

	// Step 5: Clean Docker system
	r.Step(demo.S(
		"🧽 Deep cleaning Docker system:",
		"Removing unused images, build cache, etc.",
	), demo.S(
		"echo 'Cleaning Docker system...'",
		"docker system prune -f",
		"echo ''",
		"echo 'Removing unused images...'",
		"docker image prune -f",
		"echo 'Docker system cleaned ✅'",
	))

	// Step 6: Verify complete cleanup
	r.Step(demo.S(
		"✅ Verifying complete cleanup:",
	), demo.S(
		"echo '=== Cleanup Verification ==='",
		"echo ''",
		"echo 'Remaining containers:'",
		"docker ps -a --format 'table {{.Names}}\\t{{.Status}}' | grep -E '(whiskeyhouse|icc-ai|ignition|postgres|redis|grafana)' || echo 'None (good!)'",
		"echo ''",
		"echo 'Remaining volumes:'",
		"docker volume ls | grep -E '(whiskeyhouse|icc-ai|postgres|redis|gw-data|grafana)' || echo 'None (good!)'",
		"echo ''",
		"echo 'Remaining networks:'",
		"docker network ls | grep -E '(whiskeyhouse|icc-ai|whk-network)' || echo 'None (good!)'",
	))

	// Step 7: Fresh start instructions
	r.Step(demo.S(
		"🎯 Environment completely reset!",
		"Ready for fresh installation",
	), demo.S(
		"echo '=== 🎉 COMPLETE CLEANUP SUCCESSFUL! ==='",
		"echo ''",
		"echo 'Environment is now completely clean:'",
		"echo '✅ All containers removed'",
		"echo '✅ All volumes deleted'",
		"echo '✅ All networks cleaned'",
		"echo '✅ Docker system pruned'",
		"echo ''",
		"echo '=== Next Steps ==='",
		"echo '1. Run: ./demo-stack-up startup'",
		"echo '2. Wait for services to initialize'",
		"echo '3. Run: ./demo-stack-up health'",
		"echo ''",
		"echo '🚀 Ready for fresh demo environment!'",
	))

	return r
}
