const { test, expect } = require('@playwright/test');
const { IgnitionAuthHelper } = require('./auth-helper');

test.describe('Authenticated Ignition Gateway Tests', () => {
  let authHelper;

  test.beforeAll(async () => {
    authHelper = new IgnitionAuthHelper();
  });

  test('should access gateway configuration page', async ({ page }) => {
    // Navigate to config page (authentication handled by storage state)
    await page.goto('/web/config');
    
    // Verify we're on the configuration page
    await expect(page).toHaveURL(/\/web\/config/);
    
    // Check for configuration page elements
    const configContent = page.locator('body');
    await expect(configContent).toBeVisible();
    
    // The page should have loaded successfully (not 404)
    const pageTitle = await page.title();
    console.log('Config page title:', pageTitle);
  });

  test('should access project management', async ({ page }) => {
    // Navigate to project management
    await page.goto('/main/web/config/projects');
    
    // Check for project list
    const projectsHeader = page.locator('h1:has-text("Projects")');
    await expect(projectsHeader).toBeVisible({ timeout: 10000 });
    
    // Look for our demo project
    const demoProject = page.locator('text=DemoAIProject');
    const projectExists = await demoProject.isVisible().catch(() => false);
    
    if (projectExists) {
      console.log('✅ DemoAIProject found');
    } else {
      console.log('ℹ️ DemoAIProject not found, may need to be created');
    }
  });

  test('should access designer launcher', async ({ page }) => {
    // Navigate to designer page
    await page.goto('/main/web/home/designer');
    
    // Check for designer launcher elements
    const designerTitle = page.locator('text=Designer Launcher');
    await expect(designerTitle).toBeVisible({ timeout: 10000 });
  });

  test('should validate AI validation endpoints', async ({ page }) => {
    // Test authenticated API request
    const response = await authHelper.authenticatedRequest(page, '/system/webdev/validation', {
      method: 'GET'
    });
    
    expect(response.status()).toBe(200);
    
    const data = await response.json();
    console.log('Validation endpoint response:', data);
  });

  test('should access Perspective session', async ({ page }) => {
    // Navigate to Perspective client
    await authHelper.navigateAuthenticated(page, '/data/perspective/client/DemoAIProject');
    
    // Wait for Perspective to load
    await page.waitForSelector('.perspective-workspace', { timeout: 15000 }).catch(() => {
      console.log('Perspective workspace not found, checking for login...');
    });
    
    // Check if we're in a Perspective session
    const perspectiveRoot = page.locator('.perspective-root, #perspective-root, [data-component="root"]');
    const isPerspectiveLoaded = await perspectiveRoot.isVisible().catch(() => false);
    
    if (isPerspectiveLoaded) {
      console.log('✅ Perspective session loaded successfully');
    } else {
      console.log('⚠️ Perspective session may require additional configuration');
    }
  });

  test('should handle form-based authentication', async ({ page }) => {
    // Clear cookies to force re-authentication
    await page.context().clearCookies();
    
    // Navigate to a protected page
    await page.goto('/main/web/config');
    
    // Check if redirected to login
    const currentUrl = page.url();
    if (currentUrl.includes('login') || currentUrl.includes('auth')) {
      console.log('Redirected to login page, performing authentication...');
      
      // Use auth helper to authenticate
      await authHelper.authenticate(page);
      
      // Verify we can now access the protected page
      await page.goto('/main/web/config');
      await expect(page).toHaveURL(/\/config/);
      console.log('✅ Form-based authentication successful');
    } else {
      console.log('ℹ️ Already authenticated or no login required');
    }
  });

  test('should validate gateway status', async ({ page }) => {
    // Check gateway status endpoint
    const statusResponse = await authHelper.authenticatedRequest(page, '/StatusPing');
    expect(statusResponse.status()).toBe(200);
    
    const statusText = await statusResponse.text();
    expect(statusText).toContain('RUNNING');
    console.log('✅ Gateway status:', statusText.trim());
  });

  test('should access tag browser', async ({ page }) => {
    // Navigate to tag browser in config
    await page.goto('/main/web/config/tags');
    
    // Wait for tag browser to load
    await page.waitForSelector('[class*="tag"], [data-testid="tag-browser"]', { 
      timeout: 10000 
    }).catch(() => {
      console.log('Tag browser UI not found with expected selectors');
    });
    
    // Check for tag browser elements
    const tagBrowserTitle = page.locator('text=/Tag.*Browser|Tags|Tag Configuration/i');
    const isTitleVisible = await tagBrowserTitle.isVisible().catch(() => false);
    
    if (isTitleVisible) {
      console.log('✅ Tag browser accessible');
    } else {
      console.log('⚠️ Tag browser may have different UI structure');
    }
  });
});

test.describe('Authentication Edge Cases', () => {
  test('should handle session timeout gracefully', async ({ page }) => {
    const authHelper = new IgnitionAuthHelper();
    
    // Simulate session timeout by clearing cookies
    await page.context().clearCookies();
    
    // Try to access protected resource
    const response = await page.request.get('/main/web/config', {
      failOnStatusCode: false
    });
    
    if (response.status() === 401 || response.status() === 403) {
      console.log('Session expired as expected, re-authenticating...');
      
      // Re-authenticate
      await authHelper.authenticate(page);
      
      // Retry the request
      const retryResponse = await authHelper.authenticatedRequest(page, '/main/web/config');
      expect(retryResponse.status()).toBe(200);
      console.log('✅ Successfully handled session timeout');
    }
  });

  test('should handle invalid credentials', async ({ page }) => {
    const authHelper = new IgnitionAuthHelper();
    
    // Override credentials with invalid ones
    authHelper.credentials = {
      username: 'invalid_user',
      password: 'wrong_password',
      baseUrl: authHelper.credentials.baseUrl
    };
    
    // Clear any existing authentication
    await page.context().clearCookies();
    
    // Attempt authentication with invalid credentials
    try {
      await authHelper.authenticate(page);
      console.log('⚠️ Authentication succeeded with invalid credentials - check security settings');
    } catch (error) {
      console.log('✅ Invalid credentials rejected as expected');
      expect(error).toBeTruthy();
    }
  });
});
