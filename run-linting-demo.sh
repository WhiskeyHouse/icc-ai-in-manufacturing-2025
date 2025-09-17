#!/bin/bash
set -euo pipefail

# Ignition Linting Demo Runner
# Comprehensive showcase of CLI and MCP linting capabilities

echo "🎯 Ignition Linting Demo Showcase"
echo "=================================="
echo ""
echo "This demo showcases production-validated linting for Ignition projects:"
echo "• CLI linting with scripts/lint-ignition.py"
echo "• MCP server integration for AI agents"
echo "• Real-world validation on WHK Distillery project"
echo "• 1,347 Python files with 552,399 lines of code"
echo "• 226 Perspective views with 2,660 components"
echo ""

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ uv is required but not installed. Please install uv first."
    exit 1
fi

# Check if distillery project exists
if [ ! -d "../whk-distillery01-ignition-global" ]; then
    echo "❌ WHK Distillery project not found at ../whk-distillery01-ignition-global"
    echo "   The demo will use local projects instead."
    DISTILLERY_AVAILABLE=false
else
    echo "✅ WHK Distillery project found - using real production code!"
    DISTILLERY_AVAILABLE=true
fi

echo ""

# Check for auto flag
AUTO_MODE=false
if [[ "${1:-}" == "--auto" ]]; then
    AUTO_MODE=true
    echo "🤖 Running in AUTO mode - full demo without user interaction"
    choice=1
else
    echo "🚀 Choose demo mode:"
    echo "1. Full interactive demo (recommended)"
    echo "2. Quick CLI test"
    echo "3. MCP server test"
    echo "4. Prerequisites check only"
    echo ""
    echo "💡 Tip: Use './run-linting-demo.sh --auto' for automated full demo"
    echo ""
    read -p "Enter choice (1-4): " choice
fi

case $choice in
    1)
        if [ "$AUTO_MODE" = true ]; then
            echo "🎬 Running full automated demo..."
            uv run python demo-linting-showcase.py --auto
        else
            echo "🎬 Running full interactive demo..."
            uv run python demo-linting-showcase.py
        fi
        ;;
    2)
        echo "⚡ Running quick CLI tests..."
        echo ""
        echo "📋 Checking linter availability..."
        uv run python scripts/lint-ignition.py --check-linter
        echo ""
        
        if [ "$DISTILLERY_AVAILABLE" = true ]; then
            echo "🏭 Testing on real distillery project (scripts only, limited output)..."
            timeout 30s uv run python scripts/lint-ignition.py --project ../whk-distillery01-ignition-global --type scripts || echo "⏱️  Analysis timeout (normal for large projects)"
            echo ""
            echo "🎨 Testing Perspective components..."
            uv run python scripts/lint-ignition.py --project ../whk-distillery01-ignition-global --type perspective
        else
            echo "📝 Testing on local Global project..."
            uv run python scripts/lint-ignition.py --project ignition-projects/Global --verbose
        fi
        ;;
    3)
        echo "🤖 Testing MCP server integration..."
        uv run python test-mcp-linter.py
        ;;
    4)
        echo "🔍 Checking prerequisites only..."
        uv run python demo-linting-showcase.py --section prereq
        ;;
    *)
        echo "❌ Invalid choice. Please run again with 1-4."
        exit 1
        ;;
esac

echo ""
echo "🎉 Demo complete!"
echo ""
echo "📚 Next steps:"
echo "• Review LINTING-DEMO-GUIDE.md for detailed documentation"
echo "• Use CLI: uv run python scripts/lint-ignition.py --project <path>"
echo "• Use MCP tools in Cursor AI conversations"
echo "• Integrate linting into your development workflow"
echo ""
echo "🔧 Available commands:"
echo "• ./run-linting-demo.sh --auto          # Full automated demo"
echo "• uv run python scripts/lint-ignition.py --help"
echo "• uv run python demo-linting-showcase.py --help"
echo "• uv run python demo-linting-showcase.py --auto  # Direct auto mode"
echo "• uv run python test-mcp-linter.py"
echo ""
