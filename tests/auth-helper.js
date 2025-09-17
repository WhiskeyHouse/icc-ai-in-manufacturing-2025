const fs = require('fs');
const path = require('path');

/**
 * Ignition Gateway Authentication Helper
 * Handles authentication for Playwright tests and MCP interactions
 */
class IgnitionAuthHelper {
  constructor() {
    // Load credentials from environment or secrets files
    this.credentials = this.loadCredentials();
    this.authStoragePath = path.join(__dirname, '..', '.auth', 'ignition-auth.json');
  }

  /**
   * Load credentials from secrets files and environment variables
   */
  loadCredentials() {
    const secretsPath = path.join(__dirname, '..', 'secrets');
    
    // Read password from secrets file
    let password = '';
    const passwordFile = path.join(secretsPath, 'GATEWAY_ADMIN_PASSWORD');
    if (fs.existsSync(passwordFile)) {
      password = fs.readFileSync(passwordFile, 'utf-8').trim();
    }

    // Get username from environment or use default
    const username = process.env.GATEWAY_ADMIN_USERNAME || 'admin';

    return {
      username,
      password,
      baseUrl: process.env.IGNITION_BASE_URL || 'http://localhost:9088'
    };
  }

  /**
   * Authenticate with Ignition Gateway
   * @param {Page} page - Playwright page object
   */
  async authenticate(page) {
    const { username, password, baseUrl } = this.credentials;

    // Check if already authenticated
    const isAuthenticated = await this.checkAuthentication(page);
    if (isAuthenticated) {
      console.log('Already authenticated with Ignition Gateway');
      return true;
    }

    try {
      // Navigate to home page first
      await page.goto(`${baseUrl}/app/home`);
      
      // Wait for page to load
      await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
      
      // Look for and click the login button - exact match for "Log In"
      const loginButton = await page.locator('button:has-text("Log In"), a:has-text("Log In")').first();
      let hasLoginButton = await loginButton.isVisible().catch(() => false);
      
      if (!hasLoginButton) {
        // Try alternative selector
        const altButton = await page.locator('text="Log In"').first();
        hasLoginButton = await altButton.isVisible().catch(() => false);
        if (hasLoginButton) {
          console.log('Login button found, clicking...');
          await altButton.click();
        }
      } else {
        console.log('Login button found, clicking...');
        await loginButton.click();
      }
      
      if (hasLoginButton) {
        await page.waitForTimeout(2000); // Wait for navigation
      }

      // Check if we're now on a login page (first check for username field)
      const usernameField = await page.locator('input[type="text"], input[name*="user"], input[placeholder*="user" i], input#username').first();
      const hasUsernameField = await usernameField.isVisible().catch(() => false);

      if (hasUsernameField) {
        console.log('Login form detected, performing authentication...');
        
        // Step 1: Fill username
        console.log('Filling username...');
        await usernameField.fill(username);
        await page.waitForTimeout(1000);
        
        // Step 2: Press Enter to reveal password field
        console.log('Pressing Enter to proceed to password...');
        await usernameField.press('Enter');
        await page.waitForTimeout(2000); // Wait for password field to appear
        
        // Step 3: Now look for password field
        const passwordField = await page.locator('input[type="password"]').first();
        const hasPasswordField = await passwordField.isVisible().catch(() => false);
        
        if (hasPasswordField) {
          console.log('Filling password...');
          await passwordField.fill(password);
          await page.waitForTimeout(1000);
          
          // Step 4: Press Enter or click Continue after password
          console.log('Submitting password...');
          
          // First try pressing Enter
          await passwordField.press('Enter');
          await page.waitForTimeout(2000);
          
          // Check if we're still on login page (might need another Continue)
          const stillOnLogin = page.url().includes('login');
          if (stillOnLogin) {
            // Look for Continue button after password
            const continueAfterPassword = await page.locator('button:has-text("Continue"), button:has-text("Sign In"), button:has-text("Log In")').first();
            if (await continueAfterPassword.isVisible()) {
              console.log('Clicking final Continue/Sign In button...');
              await continueAfterPassword.click();
            }
          }
        } else {
          console.log('Warning: Password field not found after pressing Enter');
        }
        
        // Wait for navigation after login
        await page.waitForLoadState('networkidle', { timeout: 10000 });
        
        console.log('Authentication successful');
        return true;
      }

      // Alternative: Check for basic auth prompt
      const basicAuthUrl = `http://${username}:${password}@localhost:9088`;
      if (!isAuthenticated && baseUrl.includes('localhost')) {
        console.log('Attempting basic authentication...');
        await page.goto(basicAuthUrl);
        await page.waitForLoadState('networkidle', { timeout: 5000 });
      }

      return true;
    } catch (error) {
      console.error('Authentication failed:', error.message);
      throw error;
    }
  }

  /**
   * Check if currently authenticated
   * @param {Page} page - Playwright page object
   */
  async checkAuthentication(page) {
    try {
      // Try to access the web config page which requires authentication
      const response = await page.request.get('/web/config', {
        failOnStatusCode: false
      });
      
      // If we get 200, we're authenticated
      // If we get 401/403, we need to authenticate
      return response.status() === 200;
    } catch (error) {
      return false;
    }
  }

  /**
   * Save authentication state for reuse
   * @param {BrowserContext} context - Playwright browser context
   */
  async saveAuthState(context) {
    const authDir = path.dirname(this.authStoragePath);
    if (!fs.existsSync(authDir)) {
      fs.mkdirSync(authDir, { recursive: true });
    }
    
    await context.storageState({ path: this.authStoragePath });
    console.log('Authentication state saved to:', this.authStoragePath);
  }

  /**
   * Load saved authentication state
   * @returns {Object|null} Storage state object or null if not found
   */
  loadAuthState() {
    if (fs.existsSync(this.authStoragePath)) {
      const state = JSON.parse(fs.readFileSync(this.authStoragePath, 'utf-8'));
      console.log('Loaded authentication state from:', this.authStoragePath);
      return state;
    }
    return null;
  }

  /**
   * Clear saved authentication state
   */
  clearAuthState() {
    if (fs.existsSync(this.authStoragePath)) {
      fs.unlinkSync(this.authStoragePath);
      console.log('Cleared authentication state');
    }
  }

  /**
   * Perform authenticated API request
   * @param {Page} page - Playwright page object
   * @param {string} endpoint - API endpoint path
   * @param {Object} options - Request options
   */
  async authenticatedRequest(page, endpoint, options = {}) {
    const { baseUrl } = this.credentials;
    
    // Ensure we're authenticated first
    await this.authenticate(page);
    
    // Make the request
    const url = endpoint.startsWith('http') ? endpoint : `${baseUrl}${endpoint}`;
    return await page.request.fetch(url, {
      ...options,
      failOnStatusCode: false
    });
  }

  /**
   * Handle authentication for different Ignition pages
   * @param {Page} page - Playwright page object
   * @param {string} targetPath - Target path to navigate to
   */
  async navigateAuthenticated(page, targetPath) {
    const { baseUrl } = this.credentials;
    
    // First authenticate
    await this.authenticate(page);
    
    // Then navigate to target
    const url = targetPath.startsWith('http') ? targetPath : `${baseUrl}${targetPath}`;
    await page.goto(url);
    
    // Check if we were redirected to login
    const currentUrl = page.url();
    if (currentUrl.includes('login') || currentUrl.includes('auth')) {
      console.log('Redirected to login, re-authenticating...');
      await this.authenticate(page);
      await page.goto(url);
    }
    
    return page;
  }
}

module.exports = { IgnitionAuthHelper };
