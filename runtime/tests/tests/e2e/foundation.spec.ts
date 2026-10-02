import { expect, test } from '@playwright/test';

test('administrator creates a branch/table and issues an invitation', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await expect(page.getByRole('heading', { name: 'Hello, Aarav.' })).toBeVisible();
  await page.getByRole('link', { name: 'Branches & tables' }).click();
  await page.getByRole('button', { name: 'Add branch', exact: true }).click();
  await page.getByLabel('Branch name').fill('Jayanagar');
  await page.getByLabel('City', { exact: true }).fill('Bengaluru');
  await page.getByLabel('Address', { exact: true }).fill('28, Sports Avenue');
  await page.getByRole('button', { name: 'Create branch' }).click();
  const card = page.locator('article').filter({ has: page.getByRole('heading', { name: 'Jayanagar' }) });
  await expect(card).toBeVisible();
  await card.getByRole('button', { name: 'Add table' }).click();
  await page.getByLabel('Table name').fill('Centre table');
  await page.getByRole('dialog').getByRole('button', { name: 'Add table', exact: true }).click();
  await expect(card.getByText('Centre table')).toBeVisible();
  await page.reload();
  await expect(card.getByText('Centre table')).toBeVisible();
  await page.getByRole('link', { name: 'Team & access' }).click();
  await page.getByRole('button', { name: 'Invite a member' }).click();
  await page.getByLabel('Email address').fill('priya@example.test');
  await page.getByRole('button', { name: 'Create invitation' }).click();
  const url = await page.getByLabel('Invitation link').inputValue();
  await page.getByRole('button', { name: 'Close dialog' }).click();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await page.getByLabel('Preview account').selectOption('55555555-5555-4555-8555-555555555555');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await expect(page.getByRole('heading', { name: 'Your workspace is waiting' })).toBeVisible();
  await page.goto(new URL(url).pathname + new URL(url).hash);
  await page.getByRole('button', { name: 'Accept invitation' }).click();
  await expect(page.getByRole('heading', { name: 'Hello, Priya.' })).toBeVisible();
  await expect(page.getByRole('link', { name: 'Team & access' })).toHaveCount(0);
});

test('coach has scoped access and the mobile layout stays within the viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await page.getByLabel('Preview account').selectOption('22222222-2222-4222-8222-222222222222');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await expect(page.getByRole('heading', { name: 'Hello, Nisha.' })).toBeVisible();
  await page.getByRole('button', { name: 'Open navigation' }).click();
  await page.getByRole('link', { name: 'Branches & tables' }).click();
  await expect(page.getByRole('heading', { name: 'Indiranagar', exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Whitefield', exact: true })).toHaveCount(0);
  await expect(page.getByRole('button', { name: 'Add branch' })).toHaveCount(0);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
  await page.screenshot({ path: '.local/screenshots/mobile-branches.png', fullPage: true });
});

test('platform owner can onboard and suspend an academy', async ({ page }) => {
  await page.goto('/');
  await page.getByLabel('Preview account').selectOption('44444444-4444-4444-8444-444444444444');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await page.getByRole('button', { name: 'Onboard academy' }).click();
  await page.getByLabel('Academy name').fill('Future Champions');
  await page.getByLabel('Workspace slug').fill('future-champions');
  await page.getByLabel('Administrator email').fill('priya@example.test');
  await page.getByRole('button', { name: 'Create academy & invitation' }).click();
  await expect(page.getByLabel('Invitation link')).toBeVisible();
  await page.getByRole('button', { name: 'Close dialog' }).click();
  page.on('dialog', dialog => void dialog.accept());
  const row = page.getByRole('row').filter({ hasText: 'Future Champions' });
  await row.getByRole('button', { name: 'Suspend' }).click();
  await expect(row.getByText('Suspended')).toBeVisible();
});

test('overview is usable at desktop size', async ({ page }) => {
  await page.setViewportSize({ width: 1440, height: 1000 });
  await page.goto('/');
  await page.getByRole('button', { name: 'Open workspace' }).click();
  await expect(page.getByRole('heading', { name: 'Hello, Aarav.' })).toBeVisible();
  await expect(page.getByText('Active branches', { exact: true })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Your spaces' })).toBeVisible();
  await page.screenshot({ path: '.local/screenshots/overview.png', fullPage: true });
});
