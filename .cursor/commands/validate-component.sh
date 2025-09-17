#!/bin/bash
# @validate-component command for Cursor AI
# Validate a single Perspective component (inline validation)

set -euo pipefail

# Default values
FIX=false
INPUT_FILE=""
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --fix)
            FIX=true
            shift
            ;;
        --file)
            INPUT_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: @validate-component [--fix] [--file JSON_FILE]"
            echo ""
            echo "Options:"
            echo "  --fix         Attempt to auto-fix common issues"
            echo "  --file FILE   Validate component from JSON file"
            echo ""
            echo "Examples:"
            echo "  @validate-component"
            echo "  @validate-component --fix"
            echo "  @validate-component --file component.json"
            echo ""
            echo "Note: If no file is specified, the command will look for component JSON"
            echo "      in the current selection or clipboard."
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Create temporary file for component validation
TEMP_FILE=$(mktemp /tmp/component_validation.XXXXXX.json)
trap "rm -f $TEMP_FILE" EXIT

# Get component JSON
if [[ -n "$INPUT_FILE" ]]; then
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo "❌ File not found: $INPUT_FILE"
        exit 1
    fi
    cp "$INPUT_FILE" "$TEMP_FILE"
    echo "📄 Validating component from file: $INPUT_FILE"
else
    # Try to get from clipboard or current selection
    # This is a simplified approach - in practice, Cursor would provide the selection
    echo "📋 Please provide component JSON via --file option or paste it when prompted:"
    echo "Enter component JSON (press Ctrl+D when done):"
    cat > "$TEMP_FILE"
fi

# Validate the JSON format first
if ! python3 -m json.tool "$TEMP_FILE" > /dev/null 2>&1; then
    echo "❌ Invalid JSON format in component data"
    exit 1
fi

echo ""
echo "🔍 Validating Perspective component..."

# Run validation using the AI integration script
if [[ "$FIX" == "true" ]]; then
    echo "🔧 Auto-fix mode enabled"
    python3 "$PROJECT_ROOT/scripts/ai-lint-integration.py" --test-component "$TEMP_FILE" --auto-fix
else
    python3 "$PROJECT_ROOT/scripts/ai-lint-integration.py" --test-component "$TEMP_FILE"
fi

VALIDATION_RESULT=$?

if [[ $VALIDATION_RESULT -eq 0 ]]; then
    echo ""
    echo "✅ Component validation completed successfully"
else
    echo ""
    echo "⚠️  Component validation found issues (see details above)"
fi

exit $VALIDATION_RESULT
