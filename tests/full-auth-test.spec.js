const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('Full Authentication Flow', () => {
  test('complete login and access config', async ({ page }) => {
    // Load credentials
    const passwordFile = path.join(__dirname, '..', 'secrets', 'GATEWAY_ADMIN_PASSWORD');
    const password = fs.readFileSync(passwordFile, 'utf-8').trim();
    const username = 'admin';
    
    console.log('Starting fresh authentication flow...');
    
    // Clear cookies to ensure fresh login
    await page.context().clearCookies();
    
    // Step 1: Navigate to home
    console.log('\n1. Navigating to home page...');
    await page.goto('http://localhost:9088/app/home');
    await page.waitForTimeout(2000);
    console.log('   URL:', page.url());
    
    // Step 2: Click Log In
    console.log('\n2. Clicking Log In button...');
    const loginButton = page.locator('text="Log In"').first();
    await loginButton.click();
    await page.waitForTimeout(2000);
    console.log('   URL:', page.url());
    
    // Step 3: Enter username
    console.log('\n3. Entering username...');
    const usernameField = page.locator('input[name="username"]').first();
    await usernameField.fill(username);
    console.log('   Username entered:', username);
    
    // Step 4: Press Enter to reveal password field
    console.log('\n4. Pressing Enter to reveal password field...');
    await usernameField.press('Enter');
    await page.waitForTimeout(2000);
    
    // Step 5: Check for password field
    const passwordField = page.locator('input[type="password"]:visible').first();
    const hasPassword = await passwordField.isVisible().catch(() => false);
    console.log('   Password field visible:', hasPassword);
    
    if (hasPassword) {
      // Step 6: Enter password
      console.log('\n5. Entering password...');
      await passwordField.fill(password);
      console.log('   Password entered: [HIDDEN]');
      
      // Step 7: Submit password
      console.log('\n6. Submitting password (pressing Enter)...');
      await passwordField.press('Enter');
      await page.waitForTimeout(3000);
      
      console.log('   URL after password submit:', page.url());
      
      // Check if we're logged in or need another action
      if (page.url().includes('login')) {
        console.log('\n7. Still on login page, checking for buttons...');
        
        // Look for any visible buttons
        const visibleButtons = await page.locator('button:visible, input[type="submit"]:visible').all();
        console.log(`   Found ${visibleButtons.length} visible buttons`);
        
        for (let i = 0; i < visibleButtons.length; i++) {
          const text = await visibleButtons[i].textContent();
          console.log(`   Button ${i}: "${text?.trim()}"`);
        }
        
        // Click the first visible button if any
        if (visibleButtons.length > 0) {
          console.log('   Clicking first button...');
          await visibleButtons[0].click();
          await page.waitForTimeout(3000);
        }
      }
      
      // Final check
      console.log('\n8. Final status:');
      console.log('   URL:', page.url());
      console.log('   Logged in:', !page.url().includes('login'));
      
      // Try to access config page
      if (!page.url().includes('login')) {
        console.log('\n9. Attempting to access config page...');
        await page.goto('http://localhost:9088/web/config');
        await page.waitForTimeout(2000);
        console.log('   Config page URL:', page.url());
        console.log('   Config access:', page.url().includes('/web/config') ? '✅ SUCCESS' : '❌ FAILED');
      }
    } else {
      console.log('❌ Password field never became visible');
    }
    
    // Take final screenshot
    await page.screenshot({ path: 'test-results/final-auth-state.png' });
  });
});
