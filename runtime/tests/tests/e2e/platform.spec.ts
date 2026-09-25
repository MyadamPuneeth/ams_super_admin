import { expect, test, type Page } from '@playwright/test';

async function signIn(page: Page) {
  await page.goto('/');
  await page.getByLabel('Username').fill('platform.owner');
  await page.getByLabel('Password').fill('correct-horse-battery');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: /Good to see you/ })).toBeVisible();
}

test('owner onboards an administrator who changes the temporary password', async ({ page, context }) => {
  test.setTimeout(60_000);
  await context.grantPermissions(['clipboard-read', 'clipboard-write']);
  await signIn(page);
  await expect(page.getByRole('heading', { name: 'Registered academies' })).toBeVisible();
  await page.getByRole('button', { name: 'Add academy' }).click();
  await page.getByLabel('Academy name').fill('Future Champions');
  await page.getByLabel('Workspace slug').fill('future-champions');
  await page.getByLabel('Administrator name').fill('Maya Singh');
  await page.getByLabel('Administrator email').fill('priya@example.test');
  await page.getByLabel('Administrator username').fill('maya.admin');
  await page.getByLabel('Temporary password').fill('temporary-pass-123');
  await page.getByLabel('Confirm password').fill('temporary-pass-123');
  await page.getByRole('button', { name: 'Create academy' }).click();
  await expect(page.getByRole('heading', { name: 'Future Champions credentials' })).toBeVisible();
  await page.getByRole('button', { name: 'Copy password' }).click();
  await page.getByRole('button', { name: 'Done' }).click();
  await page.reload();
  await expect(page.getByRole('heading', { name: 'Finish credential handoff' })).toBeVisible();
  await page.getByRole('searchbox').fill('future-champions');
  const row = page.getByRole('row').filter({ hasText: 'Future Champions' });
  await expect(row).toBeVisible();
  await row.getByRole('button', { name: 'Manage plan' }).click();
  await page.getByLabel('Plan').selectOption('PRO');
  await page.getByLabel('Status').selectOption('ACTIVE');
  await page.getByRole('button', { name: 'Save subscription' }).click();
  await expect(row.getByText('Pro', { exact: true })).toBeVisible();
  page.on('dialog', dialog => void dialog.accept());
  await row.getByRole('button', { name: 'Suspend' }).click();
  await expect(row.getByText('Suspended')).toBeVisible();
  await row.getByRole('button', { name: 'Activate' }).click();
  await expect(row.getByText('Active', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page.getByRole('heading', { name: 'Welcome back' })).toBeVisible();

  await page.goto('http://127.0.0.1:5273');
  await page.getByLabel('Username').fill('maya.admin');
  await page.locator('input[name="password"]').fill('temporary-pass-123');
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page.getByRole('heading', { name: 'Create a new password' })).toBeVisible();
  await page.getByLabel('New password', { exact: true }).fill('replacement-pass-456');
  await page.getByLabel('Confirm new password', { exact: true }).fill('replacement-pass-456');
  await page.getByRole('button', { name: 'Save password and continue' }).click();
  await expect(page.getByRole('heading', { name: 'Good to see you.' })).toBeVisible();
  await expect(page.getByText('Future Champions')).toBeVisible();
  await expect(page.getByRole('button', { name: 'Athletes' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Attendance' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Fees' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Finance' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Add athlete' })).toHaveCount(0);

  const dialogPages = [
    ['Athletes', 'Add athlete'],
    ['Batches', 'Add batch'],
    ['Coaches', 'Add coach'],
    ['Branches', 'Add branch'],
    ['Fees', 'Generate invoices'],
    ['Finance', 'Add income'],
  ] as const;
  for (const [navigation, action] of dialogPages) {
    await page.getByRole('button', { name: navigation, exact: true }).click();
    await expect(page.getByRole('heading', { name: navigation === 'Branches' ? 'Branches & tables' : navigation, exact: true })).toBeVisible();
    await page.getByRole('button', { name: action }).click();
    const dialog = page.getByRole('dialog');
    await expect(dialog).toBeVisible();
    if (await dialog.locator('select').count()) await expect(dialog.locator('select').first()).toHaveCSS('min-height', '48px');
    await dialog.getByRole('button', { name: /^Close/ }).click();
  }
  await page.getByRole('button', { name: 'Attendance', exact: true }).click();
  await expect(page.getByRole('heading', { name: 'Attendance' })).toBeVisible();
  await expect(page.getByRole('alert')).toHaveCount(0);
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('workspace load failure identifies the section and retries', async ({ page }) => {
  const tokenResponse = await page.request.post('http://127.0.0.1:5273/api/auth/demo', { data: { userId: '11111111-1111-4111-8111-111111111111' } });
  const token = (await tokenResponse.json()).accessToken;
  await page.route('**/api/academies/*/coaches', route => route.abort());
  await page.goto('http://127.0.0.1:5273');
  await page.evaluate(value => sessionStorage.setItem('ams.token', value), token);
  await page.reload();
  await expect(page.getByRole('alert')).toContainText('Could not load coaches');
  await page.unroute('**/api/academies/*/coaches');
  await page.getByRole('button', { name: 'Try again' }).click();
  await expect(page.getByRole('alert')).toHaveCount(0);
});

test('dashboard stays within a phone viewport', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await signIn(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});

test('every academy page stays within a phone viewport', async ({ page }) => {
  const tokenResponse = await page.request.post('http://127.0.0.1:5273/api/auth/demo', { data: { userId: '11111111-1111-4111-8111-111111111111' } });
  const token = (await tokenResponse.json()).accessToken;
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('http://127.0.0.1:5273');
  await page.evaluate(value => sessionStorage.setItem('ams.token', value), token);
  await page.reload();
  for (const destination of ['Athletes', 'Batches', 'Coaches', 'Branches', 'Attendance', 'Fees', 'Finance']) {
    await page.getByRole('button', { name: 'Toggle navigation' }).click();
    await page.getByRole('button', { name: destination, exact: true }).click();
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth), destination).toBe(true);
  }
});
