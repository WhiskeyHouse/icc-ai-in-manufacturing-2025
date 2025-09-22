#!/bin/bash
set -euo pipefail

# Ignition MCP Server Demo Runner
# Comprehensive demonstration of Ignition FastMCP server integration

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PYTHON_SCRIPT="$REPO_ROOT/demos/python/demo-ignition-mcp.py"
IGNITION_MCP_DIR="$REPO_ROOT/../ignition-mcp"

echo "🏭 Ignition MCP Server Demo - AI-Powered Gateway Integration"
echo "=========================================================="
echo ""
echo "This demo showcases the Ignition FastMCP server capabilities:"
echo "• 🤖 42+ dynamically generated tools from Ignition 8.3 OpenAPI"
echo "• 🏭 Real-time Gateway 8.3+ management and monitoring"
echo "• 🔗 Natural language control through AI assistants"
echo "• ⚡ Async operations with comprehensive error handling"
echo "• 🛡️ Secure authentication and enterprise-grade integration"
echo "• 📊 Complete operational coverage of modern Gateway API surface"
echo "• 🆕 Built on latest Ignition 8.3+ REST API specification"
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not installed. Please install uv first."
    echo "   Visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Check if ignition-mcp directory exists
if [ ! -d "$IGNITION_MCP_DIR" ]; then
    echo "❌ Ignition MCP directory not found: $IGNITION_MCP_DIR"
    echo "   Please ensure the ignition-mcp repository is cloned in the parent directory"
    exit 1
else
    echo "✅ Ignition MCP directory found - FastMCP server available!"
fi

echo ""

# Parse command line arguments
AUTO_MODE=false
CLEANUP=false
SECTION=""

while [[ $# -gt 0 ]]; do
    case ${1:-} in
        --auto|-a)
            AUTO_MODE=true
            shift
            ;;
        --cleanup)
            CLEANUP=true
            shift
            ;;
        --section|-s)
            SECTION="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --auto, -a        Run demo automatically without user prompts"
            echo "  --section, -s     Run specific section (prereq|architecture|server|tools|gateway|ai|benefits|steps)"
            echo "  --cleanup         Stop any running MCP servers and exit"
            echo "  --help, -h        Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                    # Interactive full demo"
            echo "  $0 --auto            # Automated full demo"
            echo "  $0 --section server  # Start MCP server only"
            echo "  $0 --cleanup         # Stop running servers"
            echo ""
            echo "Demo Sections:"
            echo "  prereq       - Check prerequisites and dependencies"
            echo "  architecture - Show MCP server architecture overview"
            echo "  server       - Start and test MCP server"
            echo "  tools        - Discover and showcase available tools"
            echo "  gateway      - Test Ignition Gateway connectivity"
            echo "  ai           - Show AI assistant integration examples"
            echo "  benefits     - Display integration benefits and impact"
            echo "  steps        - Show next steps and usage guide"
            exit 0
            ;;
        *)
            echo "❌ Unknown option: ${1:-}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Handle cleanup
if [ "$CLEANUP" = true ]; then
    echo "🧹 Cleaning up MCP servers..."
    
    # Kill any processes using port 8007
    if lsof -ti:8007 >/dev/null 2>&1; then
        echo "🛑 Stopping processes using port 8007..."
        lsof -ti:8007 | xargs kill -9 2>/dev/null || true
        sleep 2
    fi
    
    # Kill any fastmcp processes
    echo "🛑 Stopping FastMCP processes..."
    pkill -f "fastmcp.*mcp_server.py" 2>/dev/null || true
    pkill -f "mcp_server.py" 2>/dev/null || true
    
    # Additional cleanup for uv processes
    pkill -f "uv.*fastmcp" 2>/dev/null || true
    
    echo "✅ Cleanup completed"
    exit 0
fi

# Build the command
CMD=(uv run python "$PYTHON_SCRIPT")

if [ "$AUTO_MODE" = true ]; then
    CMD+=('--auto')
    echo "🤖 Running in AUTO mode - full demo without user interaction"
elif [ -n "$SECTION" ]; then
    CMD+=('--section' "$SECTION")
    echo "🔧 Running section: $SECTION"
else
    # Interactive mode - show menu
    echo "Choose demo mode:"
    echo "1) Full interactive demo"
    echo "2) Architecture overview only"
    echo "3) Start MCP server only"
    echo "4) Tool discovery only"
    echo "5) AI integration examples"
    echo "6) Cleanup and exit"
    echo ""
    read -p "Enter your choice (1-6): " choice
    
    case $choice in
        1)
            echo "🎬 Running full interactive demo..."
            ;;
        2)
            CMD+=('--section' 'architecture')
            echo "🏗️ Showing architecture overview..."
            ;;
        3)
            CMD+=('--section' 'server')
            echo "🚀 Starting MCP server..."
            ;;
        4)
            CMD+=('--section' 'tools')
            echo "🔍 Discovering tools..."
            ;;
        5)
            CMD+=('--section' 'ai')
            echo "🤖 Showing AI integration examples..."
            ;;
        6)
            echo "🧹 Cleaning up and exiting..."
            # Kill any processes using port 8007
            if lsof -ti:8007 >/dev/null 2>&1; then
                echo "🛑 Stopping processes using port 8007..."
                lsof -ti:8007 | xargs kill -9 2>/dev/null || true
                sleep 2
            fi
            echo "🛑 Stopping FastMCP processes..."
            pkill -f "fastmcp.*mcp_server.py" 2>/dev/null || true
            pkill -f "mcp_server.py" 2>/dev/null || true
            pkill -f "uv.*fastmcp" 2>/dev/null || true
            echo "✅ Cleanup completed"
            exit 0
            ;;
        *)
            echo "❌ Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

echo ""
CMD_DISPLAY=$(printf ' %q' "${CMD[@]}")
echo "🚀 Executing:${CMD_DISPLAY}"
echo ""

# Execute the command
cd "$REPO_ROOT"
exec "${CMD[@]}"
