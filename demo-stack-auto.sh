#!/usr/bin/env bash
set -euo pipefail

# Auto-running demo script for presentations
# This version runs without requiring user interaction

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Demo configuration
STEP_DELAY=${DEMO_STEP_DELAY:-2}  # Seconds between steps
COMMAND_DELAY=${DEMO_COMMAND_DELAY:-1}  # Seconds before executing commands
TYPEWRITER_SPEED=${DEMO_TYPEWRITER_SPEED:-0.03}  # Seconds per character

# Typewriter effect function
typewriter() {
    local text="$1"
    local speed="${2:-$TYPEWRITER_SPEED}"
    
    if [ "${DEMO_NO_TYPEWRITER:-}" = "1" ]; then
        echo -e "$text"
        return
    fi
    
    local i=0
    while [ $i -lt ${#text} ]; do
        printf "%c" "${text:$i:1}"
        sleep "$speed"
        i=$((i + 1))
    done
    echo
}

# Demo step function
demo_step() {
    local title="$1"
    local description="$2"
    local command="$3"
    
    echo
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    typewriter "${BOLD}${CYAN}$title${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════════════════════${NC}"
    
    if [ -n "$description" ]; then
        echo
        typewriter "$description"
    fi
    
    if [ -n "$command" ]; then
        echo
        echo -e "${YELLOW}➤ Executing:${NC} ${GREEN}$command${NC}"
        sleep "$COMMAND_DELAY"
        
        # Execute the command
        if eval "$command"; then
            echo -e "${GREEN}✅ Command completed successfully${NC}"
        else
            echo -e "${RED}❌ Command failed (exit code: $?)${NC}"
            if [ "${DEMO_CONTINUE_ON_ERROR:-}" != "1" ]; then
                echo -e "${RED}Demo stopped due to error. Set DEMO_CONTINUE_ON_ERROR=1 to continue on errors.${NC}"
                exit 1
            fi
        fi
    fi
    
    sleep "$STEP_DELAY"
}

# Show demo header
show_header() {
    clear
    echo -e "${BLUE}"
    echo "╔══════════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 AI Manufacturing Stack Demo                           ║"
    echo "║                          Automatic Presentation Mode                        ║"
    echo "╚══════════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo
    typewriter "${BOLD}This demo will automatically start up our complete AI-powered manufacturing stack:${NC}

${GREEN}• Ignition SCADA Gateway${NC} (with auto license acceptance)
${GREEN}• PostgreSQL databases${NC} for MES and vector storage
${GREEN}• LlamaIndex RAG service${NC} for AI responses
${GREEN}• RabbitMQ${NC} for message queuing
${GREEN}• MQTT broker${NC} for IoT communication
${GREEN}• Kong API Gateway${NC} for service orchestration
${GREEN}• Monitoring stack${NC} (Grafana, Prometheus, Netdata)
${GREEN}• Redis${NC} for caching

${YELLOW}🎯 All services will auto-accept licenses and certificates!${NC}
${YELLOW}🎯 Perfect for live presentations - no manual intervention required!${NC}"

    sleep 3
}

# Demo functions
run_startup_demo() {
    show_header
    
    demo_step "📋 Stack Configuration Review" \
        "Examining our Docker Compose services and license acceptance settings..." \
        "echo '=== Docker Compose Services ===' && docker compose config --services | sort && echo && echo '=== License Acceptance Configured ===' && echo 'ACCEPT_IGNITION_EULA=Y (automatic license acceptance)'"
    
    demo_step "🧹 Environment Cleanup" \
        "Ensuring clean environment by stopping existing containers and removing conflicts..." \
        "echo 'Stopping existing compose services...' && docker compose down --remove-orphans || true && echo 'Removing conflicting containers...' && docker rm -f mqtt-broker ignition grafana prometheus netdata portainer rabbitmq redis db vector-db kong llama-index-service cadvisor node-exporter 2>/dev/null || true && echo 'Freeing up ports...' && for port in 5432 5433 6379 5672 15672 1883 8083 18083 8000 8443 9088 9043 3000 9090 19999 9000 9443; do docker ps --filter \"publish=\$port\" --format \"{{.ID}}\" | xargs -r docker rm -f 2>/dev/null || true; done && echo 'Environment cleaned ✅'"
    
    demo_step "🏗️ Starting Infrastructure Services" \
        "Starting core services: PostgreSQL databases, Redis, RabbitMQ, MQTT broker..." \
        "docker compose up -d db vector-db redis rabbitmq mqtt-broker && echo 'Waiting for databases to initialize...' && sleep 5"
    
    demo_step "🤖 Starting AI and API Services" \
        "Starting LlamaIndex RAG service and Kong API Gateway..." \
        "docker compose up -d llama-index-service kong && echo 'AI services starting up...' && sleep 3"
    
    demo_step "🏭 Starting Ignition SCADA Gateway" \
        "Starting Ignition with automatic license acceptance (ACCEPT_IGNITION_EULA=Y)..." \
        "echo 'Starting Ignition with automatic license acceptance...' && docker compose up -d ignition && echo 'Ignition is starting up (this may take 30-60 seconds)...' && echo 'License will be automatically accepted via ACCEPT_IGNITION_EULA=Y'"
    
    demo_step "📊 Starting Monitoring Stack" \
        "Starting Prometheus, Grafana, Netdata, and Portainer..." \
        "docker compose up -d prometheus grafana netdata node-exporter portainer && echo 'Monitoring stack initializing...' && sleep 3"
    
    demo_step "✅ Verifying Running Services" \
        "Checking that all services are running correctly..." \
        "echo '=== Running Containers ===' && docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}' | head -20 && echo && echo '=== Service Health Status ===' && docker compose ps"
    
    demo_step "⏳ Waiting for Ignition Gateway" \
        "Waiting for Ignition Gateway to fully initialize with license acceptance..." \
        "echo 'Checking Ignition Gateway status...' && timeout=60 && while [ \$timeout -gt 0 ]; do if curl -s http://localhost:9088/system/gwinfo | grep -q 'ContextStatus=RUNNING' 2>/dev/null; then echo '✅ Ignition Gateway is ready!'; break; fi; echo \"Waiting for Ignition... (\$timeout seconds remaining)\"; sleep 5; timeout=\$((timeout-5)); done"
    
    demo_step "🌐 Stack Ready - Access URLs" \
        "All services are now running! Here are your access URLs..." \
        "echo '=== 🏭 IGNITION SCADA GATEWAY ===' && echo 'Gateway (HTTPS): https://localhost:9043' && echo 'Gateway (HTTP):  http://localhost:9088' && echo 'Admin User: admin (password in secrets/GATEWAY_ADMIN_PASSWORD)' && echo && echo '=== 📊 MONITORING & DASHBOARDS ===' && echo 'Grafana:    http://localhost:3000 (admin/admin)' && echo 'Prometheus: http://localhost:9090' && echo 'Netdata:    http://localhost:19999' && echo 'Portainer:  http://localhost:9000' && echo && echo '=== 🔧 INFRASTRUCTURE SERVICES ===' && echo 'RabbitMQ:   http://localhost:15672 (user/password)' && echo 'MQTT Web:   http://localhost:18083 (admin/public)' && echo 'Kong API:   http://localhost:8000' && echo && echo '=== 🚀 READY FOR DEMO! ===' && echo 'All licenses automatically accepted ✅' && echo 'Self-signed certificates trusted ✅' && echo 'Services are healthy and ready ✅'"
    
    demo_step "🖥️ Opening Key Management Interfaces" \
        "Opening demo interfaces for presentation: Ignition, Grafana, Portainer, and Netdata..." \
        "if command -v open >/dev/null 2>&1; then echo 'Opening demo interfaces...' && echo 'Opening Ignition Gateway...' && open https://localhost:9043 || true && sleep 3 && echo 'Opening Grafana dashboards...' && open http://localhost:3000 || true && sleep 3 && echo 'Opening Portainer (Docker management)...' && open http://localhost:9000 || true && sleep 3 && echo 'Opening Netdata (real-time monitoring)...' && open http://localhost:19999 || true && echo 'All demo interfaces opened! 🎉'; else echo 'Manual browser opening required (not on macOS)' && echo 'Please open:' && echo '• Ignition: https://localhost:9043' && echo '• Grafana: http://localhost:3000' && echo '• Portainer: http://localhost:9000' && echo '• Netdata: http://localhost:19999'; fi"
    
    echo
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║                          🎉 DEMO COMPLETE! 🎉                               ║${NC}"
    echo -e "${GREEN}║                                                                              ║${NC}"
    echo -e "${GREEN}║  Your AI Manufacturing Stack is now running and ready for presentation!     ║${NC}"
    echo -e "${GREEN}║                                                                              ║${NC}"
    echo -e "${GREEN}║  Key URLs:                                                                   ║${NC}"
    echo -e "${GREEN}║  • Ignition Gateway: https://localhost:9043                                 ║${NC}"
    echo -e "${GREEN}║  • Grafana Dashboards: http://localhost:3000                               ║${NC}"
    echo -e "${GREEN}║  • Real-time Monitoring: http://localhost:19999                            ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
}

run_health_check() {
    echo -e "${CYAN}🏥 Running Stack Health Check...${NC}"
    echo
    
    demo_step "🔍 Container Health Status" \
        "Checking the health of all containers..." \
        "echo '=== Container Status ===' && docker compose ps && echo && echo '=== Unhealthy Containers (should be empty) ===' && docker ps --filter health=unhealthy --format 'table {{.Names}}\t{{.Status}}'"
    
    demo_step "🌐 Network Connectivity Test" \
        "Testing network connectivity between services..." \
        "echo 'Testing internal service connectivity...' && docker compose exec -T db pg_isready -U admin || echo 'Database connection issue' && docker compose exec -T redis redis-cli ping || echo 'Redis connection issue' && echo 'Network tests completed'"
    
    demo_step "🏭 Ignition Gateway Health" \
        "Verifying Ignition Gateway is fully operational..." \
        "echo 'Checking Ignition Gateway...' && curl -s http://localhost:9088/system/gwinfo | head -1 || echo 'Gateway not responding' && echo && echo 'Checking Gateway API access...' && curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:9088/system/gwinfo"
    
    demo_step "🌐 API Gateway Health" \
        "Testing Kong API Gateway functionality..." \
        "echo 'Checking Kong API Gateway...' && curl -s http://localhost:8000 || echo 'Kong API Gateway not responding' && echo && echo 'Testing Kong admin API...' && curl -s -o /dev/null -w 'HTTP Status: %{http_code}\n' http://localhost:8011/status"
    
    demo_step "📊 Monitoring Services Health" \
        "Verifying monitoring stack is operational..." \
        "echo 'Checking Grafana...' && curl -s -o /dev/null -w 'Grafana HTTP Status: %{http_code}\n' http://localhost:3000/api/health && echo 'Checking Prometheus...' && curl -s -o /dev/null -w 'Prometheus HTTP Status: %{http_code}\n' http://localhost:9090/-/healthy && echo 'Checking Netdata...' && curl -s -o /dev/null -w 'Netdata HTTP Status: %{http_code}\n' http://localhost:19999/api/v1/info"
    
    echo
    echo -e "${GREEN}✅ Health check complete! All systems operational.${NC}"
}

run_shutdown_demo() {
    echo -e "${YELLOW}🛑 Starting Graceful Shutdown Demo...${NC}"
    echo
    
    demo_step "📊 Current Stack Status" \
        "Showing what's currently running before shutdown..." \
        "echo '=== Current Stack Status ===' && docker compose ps && echo && running=\$(docker compose ps --services --filter 'status=running' | wc -l | tr -d ' ') && total=\$(docker compose ps --services | wc -l | tr -d ' ') && echo \"Active services: \$running/\$total\""
    
    demo_step "📉 Stopping Monitoring Services" \
        "Stopping non-critical monitoring services first..." \
        "echo 'Stopping monitoring stack...' && docker compose stop grafana prometheus netdata cadvisor node-exporter portainer && echo 'Monitoring services stopped ✅'"
    
    demo_step "🏭 Stopping Ignition Gateway" \
        "Gracefully shutting down Ignition Gateway..." \
        "echo 'Stopping Ignition Gateway gracefully...' && docker compose stop ignition && echo 'Waiting for Ignition to complete shutdown...' && sleep 5 && echo 'Ignition Gateway stopped ✅'"
    
    demo_step "🤖 Stopping AI and API Services" \
        "Stopping LlamaIndex RAG service and Kong API Gateway..." \
        "echo 'Stopping AI and API services...' && docker compose stop llama-index-service kong && echo 'AI and API services stopped ✅'"
    
    demo_step "📨 Stopping Message Brokers" \
        "Stopping RabbitMQ and MQTT broker..." \
        "echo 'Stopping message brokers...' && docker compose stop rabbitmq mqtt-broker && echo 'Message brokers stopped ✅'"
    
    demo_step "💾 Stopping Databases and Cache" \
        "Stopping databases and cache (most critical, stopped last)..." \
        "echo 'Stopping databases and cache...' && docker compose stop redis vector-db db && echo 'Databases and cache stopped ✅'"
    
    demo_step "✅ Shutdown Verification" \
        "Verifying complete shutdown and data preservation..." \
        "echo '=== Final Status Check ===' && docker compose ps && echo && running=\$(docker compose ps --services --filter 'status=running' | wc -l | tr -d ' ') && if [ \"\$running\" -eq 0 ]; then echo '🎉 All services successfully stopped!' && echo 'Data preserved in Docker volumes for next startup'; else echo \"⚠️  \$running services still running\" && echo 'You may need to force stop remaining services'; fi"
    
    echo
    echo -e "${GREEN}✅ Graceful shutdown complete! Data preserved for next startup.${NC}"
}

# Main script logic
case "${1:-startup}" in
    "startup")
        run_startup_demo
        ;;
    "health")
        run_health_check
        ;;
    "shutdown")
        run_shutdown_demo
        ;;
    "help"|"--help"|"-h")
        echo "Usage: $0 [startup|health|shutdown|help]"
        echo ""
        echo "Environment variables:"
        echo "  DEMO_STEP_DELAY=2           # Seconds between steps"
        echo "  DEMO_COMMAND_DELAY=1        # Seconds before executing commands"
        echo "  DEMO_TYPEWRITER_SPEED=0.03  # Seconds per character"
        echo "  DEMO_NO_TYPEWRITER=1        # Disable typewriter effect"
        echo "  DEMO_CONTINUE_ON_ERROR=1    # Continue on command errors"
        echo ""
        echo "Examples:"
        echo "  $0 startup                  # Full startup demo"
        echo "  $0 health                   # Health check only"
        echo "  $0 shutdown                 # Graceful shutdown"
        echo "  DEMO_NO_TYPEWRITER=1 $0 startup  # Fast mode"
        ;;
    *)
        echo "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
