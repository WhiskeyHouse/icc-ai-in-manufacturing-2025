const { defineConfig, devices } = require('@playwright/test');
const path = require('path');
const fs = require('fs');

// Load authentication configuration
const authStoragePath = path.join(__dirname, '.auth', 'ignition-auth.json');

module.exports = defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  
  // Global test configuration
  use: {
    baseURL: process.env.IGNITION_BASE_URL || 'http://localhost:9088',
    trace: 'on-first-retry',
    
    // Screenshot on failure
    screenshot: 'only-on-failure',
    
    // Video on failure for debugging
    video: 'retain-on-failure',
    
    // Extended timeout for authentication flows
    actionTimeout: 15000,
    navigationTimeout: 30000,
    
    // Accept downloads (for export functionality)
    acceptDownloads: true,
    
    // Ignore HTTPS errors for self-signed certificates
    ignoreHTTPSErrors: true,
    
    // Viewport size
    viewport: { width: 1280, height: 720 },
  },

  // Global setup for authentication
  globalSetup: require.resolve('./tests/global-setup.js'),
  
  // Global teardown
  globalTeardown: require.resolve('./tests/global-teardown.js'),

  projects: [
    {
      name: 'chromium',
      use: { 
        ...devices['Desktop Chrome'],
        // Use saved authentication state
        storageState: fs.existsSync(authStoragePath) ? authStoragePath : undefined,
      },
    },
    {
      name: 'firefox',
      use: { 
        ...devices['Desktop Firefox'],
        // Use saved authentication state
        storageState: fs.existsSync(authStoragePath) ? authStoragePath : undefined,
      },
    },
    {
      name: 'webkit',
      use: { 
        ...devices['Desktop Safari'],
        // Use saved authentication state
        storageState: fs.existsSync(authStoragePath) ? authStoragePath : undefined,
      },
    },
  ],

  webServer: {
    command: 'echo "Ignition Gateway should be running on port 9088"',
    port: 9088,
    reuseExistingServer: !process.env.CI,
  },
});