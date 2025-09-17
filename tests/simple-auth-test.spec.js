const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('Simple Authentication Test', () => {
  test('verify authentication works', async ({ page }) => {
    // Load the password from secrets
    const passwordFile = path.join(__dirname, '..', 'secrets', 'GATEWAY_ADMIN_PASSWORD');
    const password = fs.readFileSync(passwordFile, 'utf-8').trim();
    const username = 'admin';
    
    console.log('Testing with username:', username);
    
    // Clear any existing auth
    await page.context().clearCookies();
    
    // Go to home page first
    await page.goto('http://localhost:9088/app/home');
    await page.waitForLoadState('domcontentloaded');
    
    // Take screenshot of home page
    await page.screenshot({ path: 'test-results/home-page.png' });
    
    // Wait a bit for any dynamic content
    await page.waitForTimeout(2000);
    
    // Click the login button - exact match for "Log In"
    const loginButton = page.locator('button:has-text("Log In"), a:has-text("Log In")').first();
    const hasLoginButton = await loginButton.isVisible().catch(() => false);
    
    if (hasLoginButton) {
      console.log('Found login button, clicking it...');
      await loginButton.click();
      await page.waitForTimeout(2000); // Wait for navigation
    } else {
      // Try alternative selectors
      const altButton = page.locator('text="Log In"').first();
      if (await altButton.isVisible().catch(() => false)) {
        console.log('Found login text, clicking it...');
        await altButton.click();
        await page.waitForTimeout(2000);
      } else {
        console.log('No login button found, navigating directly to login page');
        await page.goto('http://localhost:9088/data/app/login');
        await page.waitForLoadState('domcontentloaded');
      }
    }
    
    // Take screenshot of login page
    await page.screenshot({ path: 'test-results/login-page.png' });
    
    // Wait for the password field to appear (it might load dynamically)
    await page.waitForTimeout(2000);
    
    // Look for login form fields with more specific selectors
    const usernameField = page.locator('input[type="text"], input[name*="user"], input[placeholder*="user" i], input#username').first();
    const passwordField = page.locator('input[type="password"], input[name*="pass"], input#password').first();
    
    // Check if username field is visible first
    const hasUsername = await usernameField.isVisible().catch(() => false);
    console.log('Has username field:', hasUsername);
    
    if (hasUsername) {
      // Fill username first
      console.log('Filling username...');
      await usernameField.fill(username);
      await page.waitForTimeout(1000);
      
      // Press Enter to reveal password field
      console.log('Pressing Enter to reveal password field...');
      await usernameField.press('Enter');
      await page.waitForTimeout(2000); // Wait for password field to appear
    }
    
    // Now check for password field
    const hasPassword = await passwordField.isVisible().catch(() => false);
    console.log('Has password field after Continue:', hasPassword);
    
    // Look for submit button
    const submitButton = page.locator('button[type="submit"], input[type="submit"], button:has-text("Sign In"), button:has-text("Log In"), button:has-text("Submit")').first();
    const hasSubmit = await submitButton.isVisible().catch(() => false);
    
    console.log('Has submit button:', hasSubmit);
    
    if (hasPassword) {
      console.log('Filling password...');
      
      // Fill password (username already filled above)
      await passwordField.fill(password);
      
      // Submit by pressing Enter (no visible submit button)
      console.log('Pressing Enter to submit...');
      await passwordField.press('Enter');
      
      // Wait for navigation
      await page.waitForLoadState('domcontentloaded');
      await page.waitForTimeout(2000); // Give time for any redirects
      
      // Check where we ended up
      const currentUrl = page.url();
      console.log('After login URL:', currentUrl);
      
      // Take screenshot after login
      await page.screenshot({ path: 'test-results/after-login.png' });
      
      // Now try to access config page
      await page.goto('http://localhost:9088/web/config');
      await page.waitForLoadState('networkidle');
      
      const configUrl = page.url();
      console.log('Config page URL:', configUrl);
      
      // Take screenshot of config page attempt
      await page.screenshot({ path: 'test-results/config-page.png' });
      
      // Check if we're actually on the config page
      if (configUrl.includes('/web/config')) {
        console.log('✅ Successfully accessed config page!');
      } else {
        console.log('❌ Could not access config page, redirected to:', configUrl);
      }
    } else if (hasUsername && !hasPassword) {
      console.log('Only username field visible, trying to trigger password field...');
      
      // Try pressing Tab or Enter to trigger password field
      await usernameField.press('Tab');
      await page.waitForTimeout(1000);
      
      // Check again for password field
      const passwordFieldRetry = page.locator('input[type="password"]').first();
      const hasPasswordRetry = await passwordFieldRetry.isVisible().catch(() => false);
      
      if (hasPasswordRetry) {
        console.log('Password field appeared after Tab');
        await passwordFieldRetry.fill(password);
        
        // Try to submit
        await passwordFieldRetry.press('Enter');
        await page.waitForTimeout(2000);
      } else {
        // Try clicking next/continue button if exists
        const nextButton = page.locator('button:has-text("Next"), button:has-text("Continue")').first();
        if (await nextButton.isVisible().catch(() => false)) {
          console.log('Found Next/Continue button, clicking...');
          await nextButton.click();
          await page.waitForTimeout(2000);
          
          // Now look for password field again
          const passwordFieldFinal = page.locator('input[type="password"]').first();
          if (await passwordFieldFinal.isVisible().catch(() => false)) {
            console.log('Password field appeared after Next');
            await passwordFieldFinal.fill(password);
            await passwordFieldFinal.press('Enter');
          }
        }
      }
    } else {
      console.log('Login form not found as expected');
      
      // Log the page content for debugging
      const pageContent = await page.content();
      console.log('Page HTML (first 500 chars):', pageContent.substring(0, 500));
    }
  });
});
