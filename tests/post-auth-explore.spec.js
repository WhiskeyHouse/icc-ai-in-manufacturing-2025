const { test, expect } = require('@playwright/test');
const { IgnitionAuthHelper } = require('./auth-helper');

test.describe('Post-Authentication Exploration', () => {
  test('explore available pages after login', async ({ page }) => {
    const authHelper = new IgnitionAuthHelper();
    
    // Authenticate first
    console.log('Authenticating...');
    await authHelper.authenticate(page);
    
    console.log('\nAuthentication complete, exploring available pages...');
    
    // List of potential config/admin URLs to try
    const urlsToTest = [
      '/web/config',
      '/config', 
      '/admin',
      '/gateway/config',
      '/app/config',
      '/app/admin',
      '/app/gateway',
      '/data/perspective/client',
      '/system/webdev',
      '/main',
      '/app',
      '/app/home'
    ];
    
    console.log('\nTesting URLs after authentication:');
    console.log('=' .repeat(50));
    
    for (const url of urlsToTest) {
      const fullUrl = `http://localhost:9088${url}`;
      const response = await page.request.get(url, { failOnStatusCode: false });
      const status = response.status();
      
      let result = `${url.padEnd(30)} -> ${status}`;
      
      if (status === 302 || status === 301) {
        const location = response.headers()['location'];
        result += ` (redirects to: ${location})`;
      } else if (status === 200) {
        result += ' ✅';
      }
      
      console.log(result);
    }
    
    // Now navigate to the home page and look for navigation links
    console.log('\n\nNavigating to home page to find available links...');
    await page.goto('http://localhost:9088/app/home');
    
    // Find all links on the page
    const links = await page.locator('a').all();
    console.log(`\nFound ${links.length} links on home page:`);
    
    for (const link of links) {
      const href = await link.getAttribute('href');
      const text = await link.textContent();
      if (href && !href.startsWith('http') && !href.startsWith('#')) {
        console.log(`  "${text?.trim()}" -> ${href}`);
      }
    }
    
    // Look for any configuration or admin related text
    console.log('\n\nLooking for config/admin related elements...');
    const configElements = await page.locator('text=/config|admin|settings|manage/i').all();
    console.log(`Found ${configElements.length} config-related text elements`);
    
    for (const elem of configElements) {
      const text = await elem.textContent();
      console.log(`  - ${text?.trim()}`);
    }
    
    // Check if there's a menu or navigation
    const menus = await page.locator('nav, [role="navigation"], .menu, .nav').all();
    console.log(`\nFound ${menus.length} navigation elements`);
    
    // Take a screenshot of the logged-in state
    await page.screenshot({ path: 'test-results/logged-in-home.png' });
    console.log('\nScreenshot saved to test-results/logged-in-home.png');
  });
});
