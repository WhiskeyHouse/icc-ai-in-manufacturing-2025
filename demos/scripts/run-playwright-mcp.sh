#!/bin/bash

# Playwright MCP Server startup script for Ignition Demo with Authentication

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$REPO_ROOT"

echo "🚀 Starting Playwright MCP Server for Ignition Demo..."

# Set environment variables
export NODE_ENV=development
export MCP_SERVER_NAME="ignition-playwright-mcp"

# Load Ignition credentials
if [ -f "secrets/GATEWAY_ADMIN_PASSWORD" ]; then
    export IGNITION_PASSWORD=$(cat secrets/GATEWAY_ADMIN_PASSWORD)
    echo "✅ Loaded Ignition credentials from secrets"
else
    echo "⚠️ Warning: GATEWAY_ADMIN_PASSWORD not found in secrets/"
fi

export GATEWAY_ADMIN_USERNAME=${GATEWAY_ADMIN_USERNAME:-admin}
export IGNITION_BASE_URL=${IGNITION_BASE_URL:-http://localhost:9088}

echo "📋 Configuration:"
echo "  - Gateway URL: $IGNITION_BASE_URL"
echo "  - Admin Username: $GATEWAY_ADMIN_USERNAME"
echo "  - Password: [PROTECTED]"

# Generate MCP authentication configuration
echo "🔐 Generating authentication configuration..."
node tests/mcp-auth-handler.js

# Function to start MCP with authentication
start_mcp_with_auth() {
    local MODE=$1
    local PORT=${2:-3001}
    local EXTRA_ARGS=""
    
    if [ "$MODE" == "headless" ]; then
        EXTRA_ARGS="--headless"
    fi
    
    echo ""
    echo "🎭 Starting Playwright MCP Server..."
    echo "  Mode: ${MODE:-headed}"
    echo "  Port: $PORT"
    echo ""
    
    # Start the MCP server with authentication support
    npx @playwright/mcp \
        --port $PORT \
        --browser chromium \
        --timeout-action 15000 \
        --timeout-navigation 30000 \
        --save-trace \
        $EXTRA_ARGS
}

# Parse command line arguments
MODE="headed"
PORT=3001

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless|-h)
            MODE="headless"
            shift
            ;;
        --port|-p)
            PORT="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [--headless] [--port PORT]"
            echo ""
            echo "Options:"
            echo "  --headless, -h    Run in headless mode"
            echo "  --port, -p PORT   Specify port (default: 3001)"
            echo "  --help           Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Start the server
start_mcp_with_auth "$MODE" "$PORT"
