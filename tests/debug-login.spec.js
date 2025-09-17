const { test, expect } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

test.describe('Debug Login Flow', () => {
  test('inspect login page elements', async ({ page }) => {
    // Load the password from secrets
    const passwordFile = path.join(__dirname, '..', 'secrets', 'GATEWAY_ADMIN_PASSWORD');
    const password = fs.readFileSync(passwordFile, 'utf-8').trim();
    const username = 'admin';
    
    // Clear any existing auth
    await page.context().clearCookies();
    
    // Go to home page and click Log In
    await page.goto('http://localhost:9088/app/home');
    await page.waitForTimeout(2000);
    
    const loginButton = page.locator('text="Log In"').first();
    await loginButton.click();
    await page.waitForTimeout(2000);
    
    console.log('\n=== After clicking Log In ===');
    
    // Find all input fields
    const inputs = await page.locator('input').all();
    console.log(`Found ${inputs.length} input fields:`);
    for (let i = 0; i < inputs.length; i++) {
      const type = await inputs[i].getAttribute('type');
      const name = await inputs[i].getAttribute('name');
      const id = await inputs[i].getAttribute('id');
      const placeholder = await inputs[i].getAttribute('placeholder');
      const visible = await inputs[i].isVisible();
      console.log(`  Input ${i}: type="${type}" name="${name}" id="${id}" placeholder="${placeholder}" visible=${visible}`);
    }
    
    // Find all buttons
    const buttons = await page.locator('button, input[type="submit"], input[type="button"]').all();
    console.log(`\nFound ${buttons.length} buttons:`);
    for (let i = 0; i < buttons.length; i++) {
      const text = await buttons[i].textContent();
      const type = await buttons[i].getAttribute('type');
      const visible = await buttons[i].isVisible();
      console.log(`  Button ${i}: text="${text?.trim()}" type="${type}" visible=${visible}`);
    }
    
    // Fill username
    const usernameField = page.locator('input[type="text"]').first();
    if (await usernameField.isVisible()) {
      console.log('\n=== Filling username ===');
      await usernameField.fill(username);
      await page.waitForTimeout(2000);
      
      // Take screenshot after filling username
      await page.screenshot({ path: 'test-results/after-username.png' });
      
      // Check what changed after filling username
      console.log('\n=== After filling username ===');
      
      // Find all buttons again
      const buttonsAfter = await page.locator('button, input[type="submit"], input[type="button"]').all();
      console.log(`Found ${buttonsAfter.length} buttons:`);
      for (let i = 0; i < buttonsAfter.length; i++) {
        const text = await buttonsAfter[i].textContent();
        const type = await buttonsAfter[i].getAttribute('type');
        const visible = await buttonsAfter[i].isVisible();
        const value = await buttonsAfter[i].getAttribute('value');
        console.log(`  Button ${i}: text="${text?.trim()}" type="${type}" value="${value}" visible=${visible}`);
      }
      
      // Try pressing Enter to advance to password field
      console.log('\nPressing Enter after username...');
      await usernameField.press('Enter');
      await page.waitForTimeout(2000);
        
        // Check for password field now
        const passwordField = page.locator('input[type="password"]').first();
        if (await passwordField.isVisible()) {
          console.log('\n✅ Password field appeared!');
          await passwordField.fill(password);
          await page.screenshot({ path: 'test-results/after-password.png' });
          
          // Look for submit button
          const submitButtons = await page.locator('button:visible, input[type="submit"]:visible').all();
          if (submitButtons.length > 0) {
            console.log('Clicking submit...');
            await submitButtons[0].click();
            await page.waitForTimeout(3000);
            
            console.log('Final URL:', page.url());
          }
        } else {
          console.log('\n❌ Password field still not visible');
          
          // Check all password fields again
          const allPasswordFields = await page.locator('input[type="password"]').all();
          console.log(`\nFound ${allPasswordFields.length} password fields total:`);
          for (let i = 0; i < allPasswordFields.length; i++) {
            const visible = await allPasswordFields[i].isVisible();
            const name = await allPasswordFields[i].getAttribute('name');
            console.log(`  Password field ${i}: name="${name}" visible=${visible}`);
          }
        }
    }
  });
});
