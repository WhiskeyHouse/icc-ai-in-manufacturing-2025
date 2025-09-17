#!/bin/bash
# @lint-project command for Cursor AI
# Comprehensive linting of entire Ignition project

set -euo pipefail

# Default values
TARGET_PATH=""
QUICK=false
VERBOSE=false
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --path)
            TARGET_PATH="$2"
            shift 2
            ;;
        --quick)
            QUICK=true
            shift
            ;;
        --verbose)
            VERBOSE=true
            shift
            ;;
        --check-linter)
            echo "🔍 Checking empirical linter availability..."
            python3 "$PROJECT_ROOT/scripts/lint-ignition.py" --check-linter
            exit $?
            ;;
        --help)
            echo "Usage: @lint-project [--path PROJECT_PATH] [--quick] [--verbose] [--check-linter]"
            echo ""
            echo "Options:"
            echo "  --path PATH       Path to Ignition project (default: current project)"
            echo "  --quick          Fast validation (critical issues only)"
            echo "  --verbose        Show detailed validation results"
            echo "  --check-linter   Check if empirical linter is available"
            echo ""
            echo "Examples:"
            echo "  @lint-project"
            echo "  @lint-project --path ignition-projects/DemoAIProject"
            echo "  @lint-project --quick"
            echo "  @lint-project --verbose"
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
CMD="python3 $PROJECT_ROOT/scripts/lint-ignition.py --project \"$TARGET_PATH\" --type all"

if [[ "$VERBOSE" == "true" ]]; then
    CMD="$CMD --verbose"
fi

echo "🚀 Running comprehensive project linting..."
if [[ "$QUICK" == "true" ]]; then
    echo "⚡ Quick mode: focusing on critical issues"
fi
echo "Command: $CMD"
echo ""

# Execute the command
eval "$CMD"
