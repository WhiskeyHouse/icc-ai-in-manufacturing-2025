const { chromium } = require('@playwright/test');
const { IgnitionAuthHelper } = require('./auth-helper');
const path = require('path');
const fs = require('fs');

/**
 * Global setup for Playwright tests
 * Performs authentication once and saves state for all tests
 */
async function globalSetup(config) {
  console.log('🔧 Running global setup for Ignition Gateway tests...');
  
  const authHelper = new IgnitionAuthHelper();
  const authStoragePath = path.join(__dirname, '..', '.auth', 'ignition-auth.json');
  
  // Check if we already have valid auth state
  if (fs.existsSync(authStoragePath)) {
    console.log('✅ Found existing authentication state');
    
    // Optionally validate the auth state is still valid
    const browser = await chromium.launch();
    const context = await browser.newContext({
      storageState: authStoragePath,
      baseURL: config.projects[0].use.baseURL
    });
    const page = await context.newPage();
    
    try {
      const isValid = await authHelper.checkAuthentication(page);
      if (isValid) {
        console.log('✅ Existing authentication state is valid');
        await browser.close();
        return;
      } else {
        console.log('⚠️ Authentication state expired, re-authenticating...');
        fs.unlinkSync(authStoragePath);
      }
    } catch (error) {
      console.log('⚠️ Error checking auth state:', error.message);
      if (fs.existsSync(authStoragePath)) {
        fs.unlinkSync(authStoragePath);
      }
    } finally {
      await browser.close();
    }
  }
  
  // Perform fresh authentication
  console.log('🔐 Performing authentication with Ignition Gateway...');
  
  const browser = await chromium.launch({ 
    headless: process.env.HEADLESS !== 'false',
    args: ['--ignore-certificate-errors']
  });
  
  const context = await browser.newContext({
    ignoreHTTPSErrors: true,
    baseURL: config.projects[0].use.baseURL
  });
  
  const page = await context.newPage();
  
  try {
    // Authenticate
    await authHelper.authenticate(page);
    
    // Save authentication state
    await authHelper.saveAuthState(context);
    
    console.log('✅ Authentication successful and state saved');
  } catch (error) {
    console.error('❌ Authentication failed:', error);
    throw error;
  } finally {
    await browser.close();
  }
  
  console.log('✅ Global setup complete');
}

module.exports = globalSetup;
