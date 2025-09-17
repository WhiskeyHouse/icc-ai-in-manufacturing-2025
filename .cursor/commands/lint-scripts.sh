#!/bin/bash
# @lint-scripts command for Cursor AI
# Lint Jython/Python scripts using empirical linter

set -euo pipefail

# Default values
TARGET_PATH=""
VERBOSE=false
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            TARGET_PATH="$2"
            shift 2
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --help)
            echo "Usage: @lint-scripts [--path PROJECT_PATH] [--verbose]"
            echo ""
            echo "Options:"
            echo "  --path PATH    Path to Ignition project or script directory (default: current project)"
            echo "  --verbose      Show detailed validation results"
            echo ""
            echo "Examples:"
            echo "  @lint-scripts"
            echo "  @lint-scripts --path ignition-projects/Global/ignition/script-python"
            echo "  @lint-scripts --verbose"
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
CMD="python3 $PROJECT_ROOT/scripts/lint-ignition.py --project \"$TARGET_PATH\" --type scripts"

if [[ "$VERBOSE" == "true" ]]; then
    CMD="$CMD --verbose"
fi

echo "🚀 Running Jython script linting..."
echo "Command: $CMD"
echo ""

# Execute the command
eval "$CMD"
