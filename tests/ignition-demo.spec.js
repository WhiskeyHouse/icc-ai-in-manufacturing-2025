const { test, expect } = require('@playwright/test');

test.describe('Ignition Gateway Demo Tests', () => {
  test('should load Ignition Gateway homepage', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Ignition/);
  });

  test('should access gateway status page', async ({ page }) => {
    await page.goto('/StatusPing');
    await expect(page.locator('body')).toContainText('RUNNING');
  });

  test('should load gateway config pages', async ({ page }) => {
    await page.goto('/main/web/config');
    // Add authentication if needed
    await expect(page).toHaveURL(/config/);
  });

  test('should validate AI MCP integration endpoints', async ({ page }) => {
    // Test the validation endpoint
    const response = await page.request.get('/system/webdev/validation');
    expect(response.status()).toBe(200);
  });
});