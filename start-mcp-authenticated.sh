#!/bin/bash

# Start Playwright MCP with pre-authenticated browser profile
# This script sets up a browser profile with saved authentication

echo "🔐 Starting Playwright MCP with Ignition Authentication Support"

# Create a profile directory if it doesn't exist
PROFILE_DIR="$HOME/.playwright-profiles/ignition"
mkdir -p "$PROFILE_DIR"

# Check if we have a saved auth state
AUTH_FILE=".auth/ignition-auth.json"

if [ -f "$AUTH_FILE" ]; then
    echo "✅ Found saved authentication state"
    
    # Note: MCP doesn't directly support loading auth state,
    # but we can use user-data-dir for persistent profile
    echo "Starting MCP with persistent profile..."
    
    npx @playwright/mcp \
        --browser chromium \
        --executable-path "$(which chromium || which google-chrome || echo '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome')" \
        --port 3001 \
        --save-storage "$PROFILE_DIR" \
        "$@"
else
    echo "⚠️  No saved authentication found"
    echo "You'll need to log in manually when the browser opens"
    
    npx @playwright/mcp \
        --browser chromium \
        --port 3001 \
        "$@"
fi

echo ""
echo "📝 Manual Authentication Steps (if needed):"
echo "1. Navigate to http://localhost:9088/app/home"
echo "2. Click 'Log In'"
echo "3. Enter username: admin"
echo "4. Press Enter"
echo "5. Enter password: $(cat secrets/GATEWAY_ADMIN_PASSWORD 2>/dev/null || echo '[check secrets/GATEWAY_ADMIN_PASSWORD]')"
echo "6. Press Enter"
