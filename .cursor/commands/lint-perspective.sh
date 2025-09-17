#!/bin/bash
# @lint-perspective command for Cursor AI
# Lint Perspective components using empirical linter

set -euo pipefail

# Default values
TARGET_PATH=""
COMPONENT_TYPE=""
VERBOSE=false
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            TARGET_PATH="$2"
            shift 2
            ;;
        --component)
            COMPONENT_TYPE="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: @lint-perspective [--path PROJECT_PATH] [--component COMPONENT_TYPE] [--verbose]"
            echo ""
            echo "Options:"
            echo "  --path PATH        Path to Ignition project (default: current project)"
            echo "  --component TYPE   Filter to specific component type (e.g., ia.display.button)"
            echo "  --verbose         Show detailed validation results"
            echo ""
            echo "Examples:"
            echo "  @lint-perspective"
            echo "  @lint-perspective --path ignition-projects/DemoAIProject"
            echo "  @lint-perspective --component ia.input.button --verbose"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Determine target path
if [[ -z "$TARGET_PATH" ]]; then
    # Try to find an Ignition project in current directory
    if [[ -d "ignition-projects" ]]; then
        # Find the first project directory
        TARGET_PATH=$(find ignition-projects -maxdepth 1 -type d -name "*" | head -n 1)
        if [[ -n "$TARGET_PATH" ]]; then
            echo "🔍 Auto-detected project: $TARGET_PATH"
        fi
    fi
    
    # Fallback to current directory
    if [[ -z "$TARGET_PATH" ]]; then
        TARGET_PATH="."
        echo "🔍 Using current directory: $TARGET_PATH"
    fi
fi

# Build command
CMD="python3 $PROJECT_ROOT/scripts/lint-ignition.py --project \"$TARGET_PATH\" --type perspective"

if [[ -n "$COMPONENT_TYPE" ]]; then
    CMD="$CMD --component \"$COMPONENT_TYPE\""
fi

if [[ "$VERBOSE" == "true" ]]; then
    CMD="$CMD --verbose"
fi

echo "🚀 Running Perspective component linting..."
echo "Command: $CMD"
echo ""

# Execute the command
eval "$CMD"
