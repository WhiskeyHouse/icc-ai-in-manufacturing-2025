# Playwright MCP Setup for Ignition Demo

This setup enables Playwright MCP (Model Context Protocol) integration with Claude Code for automated browser testing and interaction with the Ignition Gateway demo.

## Installation Complete ✅

The following components have been installed and configured:

### Dependencies
- `playwright` - Core browser automation library
- `@playwright/test` - Testing framework
- `@playwright/mcp` - Official Microsoft MCP server for Playwright

### Configuration Files

#### `.mcp.json`
MCP server configuration for Claude Code integration:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["@playwright/mcp"],
      "env": {
        "NODE_ENV": "development",
        "PLAYWRIGHT_BROWSERS_PATH": "0"
      }
    }
  }
}
```

#### `playwright.config.js`
Playwright test configuration optimized for Ignition Gateway (port 9088):
- Base URL: `http://localhost:9088`
- Multi-browser support (Chromium, Firefox, WebKit)
- HTML reporter enabled
- Trace on first retry

#### `tests/ignition-demo.spec.js`
Sample test suite for Ignition Gateway validation:
- Homepage load test
- Status endpoint validation
- Configuration page access
- MCP integration endpoint testing

## Usage

### Starting Playwright MCP Server
```bash
# Basic usage
npx @playwright/mcp

# With specific port
npx @playwright/mcp --port 3001

# Headless mode
npx @playwright/mcp --headless --port 3001

# Using the convenience script
./run-playwright-mcp.sh
```

### Running Tests
```bash
# Run all tests
npx playwright test

# Run in headed mode (visible browser)
npx playwright test --headed

# Run specific test file
npx playwright test tests/ignition-demo.spec.js

# Debug mode
npx playwright test --debug
```

### MCP Server Options
The Playwright MCP server supports numerous options:
- `--browser <browser>`: Choose browser (chrome, firefox, webkit, msedge)
- `--headless`: Run in headless mode
- `--device <device>`: Emulate specific device (e.g., "iPhone 15")
- `--caps <caps>`: Enable additional capabilities (vision, pdf)
- `--timeout-action <ms>`: Set action timeout (default: 5000ms)
- `--save-trace`: Save Playwright traces for debugging

## Integration with Ignition Demo

This setup is specifically configured for the Ignition Gateway demo environment:

1. **Base URL**: Configured to use `http://localhost:9088` (Ignition Gateway)
2. **Test Endpoints**: Includes validation for `/system/webdev/validation` MCP endpoints
3. **Authentication**: Ready to be configured for Ignition Gateway auth
4. **Docker Integration**: Compatible with the existing Docker Compose setup

## Claude Code Integration

With the `.mcp.json` configuration in place, Claude Code can now:
- Access browser automation tools through MCP
- Interact with web pages programmatically
- Take screenshots and generate test code
- Execute JavaScript in browser contexts
- Scrape and analyze web content

## Next Steps

1. **Start Ignition Gateway**: Ensure the gateway is running on port 9088
2. **Test MCP Connection**: Use Claude Code's MCP tools to interact with browsers
3. **Create Demo Scenarios**: Build test scenarios for your Ignition demo
4. **Configure Authentication**: Set up any needed auth for Ignition Gateway access

## Demo Commands

```bash
# Start the full demo environment
docker-compose up -d

# Run Playwright tests against running Ignition
npx playwright test --headed

# Start MCP server for Claude integration
npx @playwright/mcp --port 3001 --save-trace
```

## Troubleshooting

- Ensure Ignition Gateway is running on port 9088
- Check that all browsers are installed: `npx playwright install`
- Verify MCP server is accessible: `npx @playwright/mcp --help`
- For authentication issues, configure storage state in playwright.config.js