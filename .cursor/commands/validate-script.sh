#!/bin/bash
# @validate-script command for Cursor AI
# Validate a single Jython script (inline validation)

set -euo pipefail

# Default values
CONTEXT=""
INPUT_FILE=""
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --context)
            CONTEXT="$2"
            shift 2
            ;;
        --file)
            INPUT_FILE="$2"
            shift 2
            ;;
        --help)
            echo "Usage: @validate-script [--context CONTEXT] [--file SCRIPT_FILE]"
            echo ""
            echo "Options:"
            echo "  --context CTX    Validation context (e.g., button_click, transform, startup)"
            echo "  --file FILE      Validate script from Python file"
            echo ""
            echo "Examples:"
            echo "  @validate-script"
            echo "  @validate-script --context button_click"
            echo "  @validate-script --file script.py --context transform"
            echo ""
            echo "Note: If no file is specified, the command will look for script content"
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

# Create temporary file for script validation
TEMP_FILE=$(mktemp /tmp/script_validation.XXXXXX.py)
trap "rm -f $TEMP_FILE" EXIT

# Get script content
if [[ -n "$INPUT_FILE" ]]; then
    if [[ ! -f "$INPUT_FILE" ]]; then
        echo "❌ File not found: $INPUT_FILE"
        exit 1
    fi
    cp "$INPUT_FILE" "$TEMP_FILE"
    echo "📄 Validating script from file: $INPUT_FILE"
else
    # Try to get from clipboard or current selection
    # This is a simplified approach - in practice, Cursor would provide the selection
    echo "📋 Please provide Jython script via --file option or paste it when prompted:"
    echo "Enter Jython script (press Ctrl+D when done):"
    cat > "$TEMP_FILE"
fi

# Check if file has content
if [[ ! -s "$TEMP_FILE" ]]; then
    echo "❌ No script content provided"
    exit 1
fi

echo ""
echo "🔍 Validating Jython script..."
if [[ -n "$CONTEXT" ]]; then
    echo "📝 Context: $CONTEXT"
fi

# Run validation using the AI integration script
python3 "$PROJECT_ROOT/scripts/ai-lint-integration.py" --test-script "$TEMP_FILE"

VALIDATION_RESULT=$?

if [[ $VALIDATION_RESULT -eq 0 ]]; then
    echo ""
    echo "✅ Script validation completed successfully"
else
    echo ""
    echo "⚠️  Script validation found issues (see details above)"
fi

exit $VALIDATION_RESULT
