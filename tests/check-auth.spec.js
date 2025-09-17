const { test, expect } = require('@playwright/test');

test.describe('Check Ignition Authentication', () => {
  test('explore Ignition gateway structure', async ({ page }) => {
    // Go to the main page
    await page.goto('/');
    
    // Take a screenshot of the homepage
    await page.screenshot({ path: 'test-results/homepage.png' });
    
    // Log the current URL
    console.log('Current URL:', page.url());
    
    // Log all visible links
    const links = await page.locator('a').all();
    console.log(`Found ${links.length} links`);
    
    for (const link of links.slice(0, 10)) {
      const href = await link.getAttribute('href');
      const text = await link.textContent();
      if (href) {
        console.log(`  Link: "${text?.trim()}" -> ${href}`);
      }
    }
    
    // Check if we're on a login page or main page
    const title = await page.title();
    console.log('Page title:', title);
    
    // Check for common Ignition elements
    const hasLogin = await page.locator('text=/login|sign in/i').count();
    const hasConfig = await page.locator('text=/config|settings/i').count();
    const hasProjects = await page.locator('text=/project/i').count();
    
    console.log('Has login elements:', hasLogin > 0);
    console.log('Has config elements:', hasConfig > 0);
    console.log('Has project elements:', hasProjects > 0);
    
    // Try to find the actual config URL
    if (hasConfig > 0) {
      const configLink = await page.locator('a:has-text("Config"), a:has-text("Settings"), a:has-text("Configuration")').first();
      if (await configLink.count() > 0) {
        const configHref = await configLink.getAttribute('href');
        console.log('Config link found:', configHref);
      }
    }
  });
  
  test('check authentication status', async ({ page }) => {
    // Check if we can access the status page
    const response = await page.request.get('/StatusPing');
    console.log('Status ping response:', response.status(), await response.text());
    
    // Try to access various potential protected endpoints
    const endpoints = [
      '/web/config',
      '/config',
      '/gateway/config',
      '/system/config',
      '/data/perspective/client',
      '/main',
      '/app'
    ];
    
    for (const endpoint of endpoints) {
      const resp = await page.request.get(endpoint, { failOnStatusCode: false });
      console.log(`${endpoint}: ${resp.status()}`);
      if (resp.status() === 302) {
        const location = resp.headers()['location'];
        console.log(`  -> Redirects to: ${location}`);
      }
    }
  });
});
