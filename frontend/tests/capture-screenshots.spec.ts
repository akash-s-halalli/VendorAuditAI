import { test, expect } from '@playwright/test';

test.use({ viewport: { width: 1600, height: 900 } });

test('capture screenshots', async ({ page }) => {
    console.log('Navigating to Login...');
    await page.goto('https://vendor-audit-ai.netlify.app/login');
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'screenshots/01_login.png', fullPage: true });

    console.log('Checking for Demo button...');
    // Check for any button with "Demo" text
    const demoBtn = page.getByRole('button', { name: /demo/i });

    if (await demoBtn.count() > 0 && await demoBtn.isVisible()) {
        console.log('Clicking Demo button...');
        await demoBtn.click();
    } else {
        console.log('No Demo button found. Attempting registration fallback...');
        await page.getByText('Create account').click();
        await page.waitForURL('**/register');
        console.log('Register page loaded.');
        await page.screenshot({ path: 'screenshots/02_register.png', fullPage: true });

        const uniqueId = Date.now();
        await page.getByLabel('Full Name').fill('Demo User');
        await page.getByLabel('Email').fill(`demo_${uniqueId}@example.com`);
        await page.getByLabel('Organization Name').fill('Demo Corp');
        await page.getByLabel('Password').fill('Password123!');
        await page.getByLabel('Confirm Password').fill('Password123!');

        console.log('Submitting registration...');
        await page.getByRole('button', { name: /create account|register|sign up/i }).click();
    }

    console.log('Waiting for Dashboard...');
    // Increase timeout to 30s
    await page.waitForURL('**/dashboard', { timeout: 30000 });
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(3000);
    console.log('Dashboard loaded.');

    await page.screenshot({ path: 'screenshots/03_dashboard.png', fullPage: true });

    // Navigation helper
    const captureNav = async (name: string, selector: string) => {
        console.log(`Navigating to ${name}...`);
        try {
            await page.getByText(selector).click();
            await page.waitForLoadState('networkidle');
            await page.waitForTimeout(2000);
            await page.screenshot({ path: `screenshots/04_${name.toLowerCase()}.png`, fullPage: true });
        } catch (e) {
            console.log(`Failed to capture ${name}: ${e}`);
        }
    };

    await captureNav('Vendors', 'Vendors');
    await captureNav('Analysis', 'Analysis');
    await captureNav('Agents', 'Agents');
});
