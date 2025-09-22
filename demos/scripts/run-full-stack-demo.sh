#!/bin/bash
set -euo pipefail

# WHK Full Stack Demo Runner
# Comprehensive demonstration of complete manufacturing infrastructure + linting

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_SCRIPT="$REPO_ROOT/demos/python/demo-full-stack.py"
SERVICES_ROOT="$REPO_ROOT/../whk-services-deployments"

echo "🏭 WHK Full Stack Demo - Complete Manufacturing Infrastructure"
echo "=============================================================="
echo ""
echo "This demo showcases the complete WHK manufacturing ecosystem:"
echo "• 🌐 Kong API Gateway & microservices architecture"
echo "• 🏭 Ignition SCADA industrial automation platform"
echo "• 💾 PostgreSQL, Redis, Vector DB, RabbitMQ, MQTT"
echo "• 📊 Prometheus, Grafana, Portainer monitoring stack"
echo "• 🤖 AI/ML infrastructure ready for intelligent automation"
echo "• 🔗 Complete service integration demonstration"
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not installed. Please install uv first."
    exit 1
fi

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is required but not available."
    exit 1
fi

# Check if WHK services directory exists
if [ ! -d "$SERVICES_ROOT" ]; then
    echo "❌ WHK services directory not found at $SERVICES_ROOT"
    echo "   Please ensure the whk-services-deployments repository is cloned"
    echo "   at the expected location."
    exit 1
else
    echo "✅ WHK services directory found - complete infrastructure available!"
fi

echo ""

# Check for command line arguments
AUTO_MODE=false
SERVICES_ONLY=false
CLEANUP=false
CLEANUP_ALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --auto|-a)
            AUTO_MODE=true
            shift
            ;;
        --services-only)
            SERVICES_ONLY=true
            shift
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --cleanup-all)
            CLEANUP_ALL=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto, -a        Run full demo automatically without user prompts"
            echo "  --services-only   Start services only, skip integration demo"
            echo "  --cleanup         Stop all running services and exit"
            echo "  --cleanup-all     Stop ALL demo services (comprehensive cleanup)"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                # Interactive full demo"
            echo "  $0 --auto         # Automated full demo"
            echo "  $0 --services-only # Start infrastructure only"
            echo "  $0 --cleanup      # Stop all services"
            echo "  $0 --cleanup-all  # Comprehensive cleanup (all demos)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Build command
CMD=(uv run python "$PYTHON_SCRIPT")

if [ "$AUTO_MODE" = true ]; then
    CMD+=('--auto')
    echo "🤖 Running in AUTO mode - full demo without user interaction"
elif [ "$SERVICES_ONLY" = true ]; then
    CMD+=('--services-only')
    echo "🔧 Starting services only - skipping integration demo"
elif [ "$CLEANUP" = true ]; then
    CMD+=('--cleanup')
    echo "🧹 Cleaning up services..."
elif [ "$CLEANUP_ALL" = true ]; then
    CMD+=('--cleanup-all')
    echo "🧹 Comprehensive cleanup - stopping ALL demo services..."
else
    echo "🎬 Choose demo mode:"
    echo "1. Full interactive demo (recommended)"
    echo "2. Services only (infrastructure)"
    echo "3. Cleanup (stop services)"
    echo "4. Comprehensive cleanup (stop ALL demo services)"
    echo ""
    echo "💡 Tip: Use '$0 --auto' for automated full demo"
    echo ""
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1)
            echo "🎬 Running full interactive demo..."
            ;;
        2)
            CMD+=('--services-only')
            echo "🔧 Starting services only - skipping integration demo..."
            ;;
        3)
            CMD+=('--cleanup')
            echo "🧹 Cleaning up services..."
            ;;
        4)
            CMD+=('--cleanup-all')
            echo "🧹 Comprehensive cleanup - stopping ALL demo services..."
            ;;
        *)
            echo "❌ Invalid choice. Please run again with 1-4."
            exit 1
            ;;
    esac
fi

echo ""
CMD_DISPLAY=$(printf ' %q' "${CMD[@]}")
echo "🚀 Executing:${CMD_DISPLAY}"
echo ""

# Execute the demo
cd "$REPO_ROOT"
exec "${CMD[@]}"
