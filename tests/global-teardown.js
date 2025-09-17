const fs = require('fs');
const path = require('path');

/**
 * Global teardown for Playwright tests
 * Cleans up resources after all tests complete
 */
async function globalTeardown(config) {
  console.log('🧹 Running global teardown...');
  
  // Optionally clean up auth state after tests
  // Uncomment if you want to force re-authentication on each test run
  /*
  const authStoragePath = path.join(__dirname, '..', '.auth', 'ignition-auth.json');
  if (fs.existsSync(authStoragePath)) {
    fs.unlinkSync(authStoragePath);
    console.log('✅ Cleaned up authentication state');
  }
  */
  
  // Clean up any temporary test files
  const tempDir = path.join(__dirname, '..', 'test-results');
  if (fs.existsSync(tempDir)) {
    console.log('🗑️ Cleaning up test results...');
  }
  
  console.log('✅ Global teardown complete');
}

module.exports = globalTeardown;
