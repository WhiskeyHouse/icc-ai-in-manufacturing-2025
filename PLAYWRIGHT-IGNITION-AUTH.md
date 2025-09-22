# Playwright MCP Authentication for Ignition Gateway

This guide explains how to use Playwright MCP with authentication for the Ignition Gateway, enabling automated browser testing and interaction with protected resources.

## Overview

The authentication system supports:
- **Form-based authentication** for Ignition web interface
- **Basic authentication** for API endpoints  
- **Session persistence** across test runs
- **MCP server integration** with Claude Code
- **Automatic re-authentication** on session expiry

## Architecture

```
┌─────────────────────┐
│  Playwright MCP     │
│     Server          │
└──────────┬──────────┘
           │
    ┌──────▼──────┐
    │Auth Handler │
    └──────┬──────┘
           │
    ┌──────▼──────────┐
    │ Ignition Gateway│
    │   (Port 9088)   │
    └─────────────────┘
```

## Quick Start

### 1. Setup Credentials

Ensure your Ignition admin password is stored in the secrets file:

```bash
echo "your_secure_password" > secrets/GATEWAY_ADMIN_PASSWORD
```

### 2. Start Ignition Gateway

```bash
docker compose up -d
```

Wait for the gateway to be fully running:
```bash
curl http://localhost:9088/StatusPing
# Should return: RUNNING
```

### 3. Run Authenticated Tests

```bash
# Run all authenticated tests
npx playwright test

# Run specific test file
npx playwright test tests/ignition-authenticated.spec.js

# Run in headed mode to see the browser
npx playwright test --headed

# Run with debug mode
npx playwright test --debug
```

### 4. Start MCP Server with Authentication

```bash
# Start with default settings (headed mode, port 3001)
./demos/scripts/run-playwright-mcp.sh

# Start in headless mode
./demos/scripts/run-playwright-mcp.sh --headless

# Start on custom port
./demos/scripts/run-playwright-mcp.sh --port 3002
```

## Authentication Components

### 1. Auth Helper Module (`tests/auth-helper.js`)

The core authentication module that handles:
- Loading credentials from secrets
- Form-based login
- Session management
- Authentication state persistence

**Key Methods:**
- `authenticate(page)` - Performs authentication
- `checkAuthentication(page)` - Verifies auth status
- `saveAuthState(context)` - Persists auth cookies
- `navigateAuthenticated(page, path)` - Navigate with auth

### 2. MCP Auth Handler (`tests/mcp-auth-handler.js`)

Specialized handler for MCP server integration:
- Generates MCP-compatible configuration
- Provides authentication scripts
- Handles request interception
- Manages auth headers and cookies

**Key Methods:**
- `getMCPAuthConfig()` - Returns MCP auth configuration
- `generateAuthScript()` - Creates browser auth script
- `createAuthenticatedContext(browser)` - Sets up authenticated context
- `exportMCPConfig()` - Exports full MCP configuration

### 3. Global Setup (`tests/global-setup.js`)

Runs once before all tests to:
- Perform initial authentication
- Save authentication state
- Validate existing auth state

### 4. Playwright Configuration

Enhanced configuration in `playwright.config.js`:
- Authentication state management
- Extended timeouts for auth flows
- Project dependencies for setup
- Global setup/teardown hooks

## Authentication Flow

### Form-Based Authentication

1. **Detection**: Check for login form presence
2. **Credentials**: Fill username and password fields
3. **Submission**: Submit the form
4. **Validation**: Verify successful authentication
5. **State Save**: Persist cookies and storage

```javascript
// Example usage
const authHelper = new IgnitionAuthHelper();
await authHelper.authenticate(page);
```

### Basic Authentication

For API endpoints, the system automatically adds Basic Auth headers:

```javascript
const response = await authHelper.authenticatedRequest(
  page, 
  '/system/webdev/validation'
);
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GATEWAY_ADMIN_USERNAME` | `admin` | Ignition admin username |
| `IGNITION_BASE_URL` | `http://localhost:9088` | Gateway base URL |
| `HEADLESS` | `true` | Run browser in headless mode |

### Secrets Files

| File | Purpose |
|------|---------|
| `secrets/GATEWAY_ADMIN_PASSWORD` | Gateway admin password |
| `.auth/ignition-auth.json` | Saved authentication state |

## Test Examples

### Basic Authenticated Test

```javascript
test('should access protected resource', async ({ page }) => {
  // Authentication handled by storage state
  await page.goto('/main/web/config');
  await expect(page).toHaveURL(/\/config/);
});
```

### Manual Authentication

```javascript
test('should handle manual login', async ({ page }) => {
  const authHelper = new IgnitionAuthHelper();
  
  // Clear existing auth
  await page.context().clearCookies();
  
  // Perform authentication
  await authHelper.authenticate(page);
  
  // Access protected resource
  await page.goto('/main/web/config');
});
```

### Authenticated API Request

```javascript
test('should make authenticated API call', async ({ page }) => {
  const authHelper = new IgnitionAuthHelper();
  
  const response = await authHelper.authenticatedRequest(
    page,
    '/system/webdev/validation',
    { method: 'GET' }
  );
  
  expect(response.status()).toBe(200);
});
```

## MCP Integration

### Using with Claude Code

The MCP server automatically handles authentication when accessing Ignition:

1. Start the MCP server with authentication:
   ```bash
   ./demos/scripts/run-playwright-mcp.sh
   ```

2. In Claude Code, use the browser tools to interact with Ignition
3. Authentication will be handled automatically

### MCP Configuration

The system generates an MCP configuration file at `mcp-ignition-auth.json`:

```json
{
  "name": "ignition-playwright-mcp",
  "authentication": {
    "enabled": true,
    "type": "custom",
    "handler": "ignition",
    "config": {
      "type": "ignition",
      "credentials": {
        "username": "admin",
        "password": "[from secrets]",
        "baseUrl": "http://localhost:9088"
      }
    }
  }
}
```

## Troubleshooting

### Authentication Fails

1. **Check credentials**: Verify `secrets/GATEWAY_ADMIN_PASSWORD` exists
2. **Gateway status**: Ensure Ignition is running (`curl http://localhost:9088/StatusPing`)
3. **Clear auth state**: Delete `.auth/ignition-auth.json` and retry

### Session Expires

The system automatically handles session expiry:
- Detects 401/403 responses
- Re-authenticates automatically
- Retries the original request

### MCP Server Issues

1. **Port conflicts**: Use a different port with `--port` flag
2. **Browser not installed**: Run `npx playwright install chromium`
3. **Permissions**: Ensure secrets files are readable

### Debug Mode

Run tests with detailed logging:

```bash
# Playwright debug mode
npx playwright test --debug

# Verbose output
DEBUG=pw:api npx playwright test

# Save traces for debugging
npx playwright test --trace on
```

## Security Considerations

1. **Secrets Management**:
   - Never commit password files to git
   - Use `.gitignore` for secrets directory
   - Rotate credentials regularly

2. **Session Storage**:
   - Auth state stored in `.auth/` directory
   - Clear after testing if needed
   - Don't share auth state files

3. **Network Security**:
   - Use HTTPS in production
   - Configure firewall rules
   - Limit access to gateway ports

## Advanced Usage

### Custom Authentication Flow

```javascript
class CustomAuthHandler extends IgnitionAuthHelper {
  async authenticate(page) {
    // Custom authentication logic
    await page.goto('/custom-login');
    // ... custom steps
    await super.authenticate(page);
  }
}
```

### Multiple User Roles

```javascript
const users = {
  admin: { username: 'admin', password: 'admin_pass' },
  operator: { username: 'operator', password: 'op_pass' },
  viewer: { username: 'viewer', password: 'view_pass' }
};

for (const [role, creds] of Object.entries(users)) {
  test(`test as ${role}`, async ({ page }) => {
    const authHelper = new IgnitionAuthHelper();
    authHelper.credentials = { ...creds, baseUrl };
    await authHelper.authenticate(page);
    // Test with specific role
  });
}
```

### Parallel Testing

Configure parallel execution with separate auth states:

```javascript
// playwright.config.js
projects: [
  {
    name: 'admin-tests',
    use: { storageState: '.auth/admin.json' }
  },
  {
    name: 'operator-tests', 
    use: { storageState: '.auth/operator.json' }
  }
]
```

## API Reference

### IgnitionAuthHelper

| Method | Description |
|--------|-------------|
| `authenticate(page)` | Perform authentication |
| `checkAuthentication(page)` | Check auth status |
| `saveAuthState(context)` | Save auth cookies |
| `loadAuthState()` | Load saved auth |
| `clearAuthState()` | Clear saved auth |
| `authenticatedRequest(page, endpoint, options)` | Make authenticated API request |
| `navigateAuthenticated(page, path)` | Navigate with auth |

### MCPAuthHandler

| Method | Description |
|--------|-------------|
| `getMCPAuthConfig()` | Get MCP auth config |
| `generateAuthScript()` | Generate auth script |
| `getAuthHeaders()` | Get auth headers |
| `createAuthenticatedContext(browser)` | Create auth context |
| `exportMCPConfig()` | Export MCP config |
| `saveMCPConfig(path)` | Save config to file |

## Next Steps

1. **Customize authentication** for your specific Ignition setup
2. **Add role-based tests** for different user permissions
3. **Integrate with CI/CD** pipelines
4. **Monitor auth metrics** and session management
5. **Extend MCP handlers** for custom workflows

For more information, see:
- [Playwright Documentation](https://playwright.dev)
- [Ignition User Manual](https://docs.inductiveautomation.com)
- [MCP Protocol Specification](https://github.com/microsoft/mcp)
