const { test } = require('@playwright/test');
const setup = test;
const { IgnitionAuthHelper } = require('./auth-helper');

/**
 * Setup authentication for all tests
 * This runs once before all tests and saves the authentication state
 */
setup('authenticate with Ignition Gateway', async ({ page, context }) => {
  console.log('🔐 Setting up authentication...');
  
  const authHelper = new IgnitionAuthHelper();
  
  // Perform authentication
  await authHelper.authenticate(page);
  
  // Save the storage state for reuse in other tests
  await authHelper.saveAuthState(context);
  
  console.log('✅ Authentication setup complete');
});
