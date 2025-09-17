const fs = require('fs');
const path = require('path');

/**
 * MCP Authentication Handler for Ignition Gateway
 * This module provides authentication support for Playwright MCP server interactions
 */
class MCPAuthHandler {
  constructor() {
    this.credentials = this.loadCredentials();
    this.authCookies = null;
    this.authHeaders = null;
  }

  /**
   * Load credentials from environment and secrets
   */
  loadCredentials() {
    const secretsPath = path.join(__dirname, '..', 'secrets');
    
    // Read password from secrets file
    let password = '';
    const passwordFile = path.join(secretsPath, 'GATEWAY_ADMIN_PASSWORD');
    if (fs.existsSync(passwordFile)) {
      password = fs.readFileSync(passwordFile, 'utf-8').trim();
    }

    const username = process.env.GATEWAY_ADMIN_USERNAME || 'admin';
    const baseUrl = process.env.IGNITION_BASE_URL || 'http://localhost:9088';

    return {
      username,
      password,
      baseUrl
    };
  }

  /**
   * Get authentication configuration for MCP
   * @returns {Object} Authentication configuration
   */
  getMCPAuthConfig() {
    return {
      type: 'ignition',
      credentials: {
        username: this.credentials.username,
        password: this.credentials.password,
        baseUrl: this.credentials.baseUrl
      },
      authStrategy: 'form', // or 'basic' for basic auth
      loginUrl: `${this.credentials.baseUrl}/data/perspective/client/DemoAIProject`,
      protectedPaths: [
        '/main/web/config',
        '/data/perspective/client',
        '/system/webdev'
      ],
      publicPaths: [
        '/StatusPing',
        '/',
        '/main/web/home'
      ],
      selectors: {
        usernameInput: 'input[type="text"], input[name*="user"], input[id*="user"]',
        passwordInput: 'input[type="password"], input[name*="pass"], input[id*="pass"]',
        submitButton: 'button[type="submit"], input[type="submit"], button:has-text("Login")',
        loginForm: 'form[id*="login"], form[class*="login"]',
        logoutButton: 'button:has-text("Logout"), a:has-text("Logout")'
      },
      validation: {
        successUrl: '/main/web/config',
        successSelector: 'text=System',
        failureIndicators: ['Invalid credentials', 'Authentication failed', 'Access denied']
      }
    };
  }

  /**
   * Generate authentication script for MCP browser context
   * @returns {string} JavaScript code to handle authentication
   */
  generateAuthScript() {
    const config = this.getMCPAuthConfig();
    
    return `
      // Ignition Gateway Authentication Script for MCP
      async function handleIgnitionAuth(page) {
        const config = ${JSON.stringify(config)};
        
        // Check if we need to authenticate
        const currentUrl = page.url();
        const needsAuth = config.protectedPaths.some(path => currentUrl.includes(path));
        
        if (!needsAuth) {
          return true;
        }
        
        // Check for login form
        const loginForm = await page.locator(config.selectors.loginForm).first();
        const isLoginVisible = await loginForm.isVisible().catch(() => false);
        
        if (isLoginVisible) {
          console.log('Ignition login form detected, authenticating...');
          
          // Fill credentials
          await page.locator(config.selectors.usernameInput).first().fill(config.credentials.username);
          await page.locator(config.selectors.passwordInput).first().fill(config.credentials.password);
          
          // Submit form
          await page.locator(config.selectors.submitButton).first().click();
          
          // Wait for navigation
          await page.waitForLoadState('networkidle', { timeout: 10000 });
          
          // Validate authentication
          const successElement = await page.locator(config.validation.successSelector).first();
          const isAuthenticated = await successElement.isVisible().catch(() => false);
          
          if (isAuthenticated) {
            console.log('✅ Ignition authentication successful');
            return true;
          } else {
            console.error('❌ Ignition authentication failed');
            return false;
          }
        }
        
        return true;
      }
      
      // Auto-execute on page navigation
      if (typeof page !== 'undefined') {
        handleIgnitionAuth(page);
      }
    `;
  }

  /**
   * Get authentication headers for API requests
   * @returns {Object} Headers object with authentication
   */
  getAuthHeaders() {
    const { username, password } = this.credentials;
    const basicAuth = Buffer.from(`${username}:${password}`).toString('base64');
    
    return {
      'Authorization': `Basic ${basicAuth}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    };
  }

  /**
   * Create MCP browser context with authentication
   * @param {Object} browser - Playwright browser instance
   * @returns {Object} Configured browser context
   */
  async createAuthenticatedContext(browser) {
    const context = await browser.newContext({
      baseURL: this.credentials.baseUrl,
      ignoreHTTPSErrors: true,
      httpCredentials: {
        username: this.credentials.username,
        password: this.credentials.password
      },
      extraHTTPHeaders: this.getAuthHeaders()
    });

    // Add authentication script to all pages
    await context.addInitScript(this.generateAuthScript());

    // Set up request interception for authentication
    await context.route('**/*', async (route, request) => {
      const url = request.url();
      
      // Check if this is a protected path
      const protectedPaths = this.getMCPAuthConfig().protectedPaths;
      const needsAuth = protectedPaths.some(path => url.includes(path));
      
      if (needsAuth && this.authCookies) {
        // Add authentication cookies if available
        const headers = {
          ...request.headers(),
          'Cookie': this.authCookies
        };
        await route.continue({ headers });
      } else {
        await route.continue();
      }
    });

    return context;
  }

  /**
   * Export configuration for MCP server
   * @returns {Object} MCP-compatible configuration
   */
  exportMCPConfig() {
    return {
      name: 'ignition-playwright-mcp',
      authentication: {
        enabled: true,
        type: 'custom',
        handler: 'ignition',
        config: this.getMCPAuthConfig()
      },
      browser: {
        headless: process.env.HEADLESS !== 'false',
        args: [
          '--ignore-certificate-errors',
          '--disable-web-security',
          '--disable-features=IsolateOrigins,site-per-process'
        ]
      },
      navigation: {
        waitUntil: 'networkidle',
        timeout: 30000
      },
      hooks: {
        beforeNavigate: this.generateAuthScript(),
        afterNavigate: `
          // Check if authentication is still valid
          const isAuthenticated = await page.evaluate(() => {
            return !window.location.href.includes('login');
          });
          if (!isAuthenticated) {
            await handleIgnitionAuth(page);
          }
        `
      }
    };
  }

  /**
   * Save MCP configuration to file
   * @param {string} outputPath - Path to save configuration
   */
  saveMCPConfig(outputPath = null) {
    const config = this.exportMCPConfig();
    const configPath = outputPath || path.join(__dirname, '..', 'mcp-ignition-auth.json');
    
    fs.writeFileSync(configPath, JSON.stringify(config, null, 2));
    console.log(`✅ MCP authentication configuration saved to: ${configPath}`);
    
    return configPath;
  }
}

// Export for use in MCP and tests
module.exports = { MCPAuthHandler };

// If run directly, generate the configuration file
if (require.main === module) {
  const handler = new MCPAuthHandler();
  handler.saveMCPConfig();
  console.log('MCP Authentication Configuration:');
  console.log(JSON.stringify(handler.exportMCPConfig(), null, 2));
}
