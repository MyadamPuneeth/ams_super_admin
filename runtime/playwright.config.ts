import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
  testDir: './tests/tests/e2e',
  fullyParallel: false,
  workers: 1,
  timeout: 30_000,
  use: { baseURL: 'http://127.0.0.1:5274', trace: 'retain-on-failure' },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: [
    { command: 'node scripts/dev.mjs --test --frontend --api-port=3202 --frontend-port=5274', url: 'http://127.0.0.1:5274', timeout: 180_000, reuseExistingServer: false, env: { PLATFORM_OWNER_USERNAME: 'platform.owner', PLATFORM_OWNER_PASSWORD: 'correct-horse-battery', PLATFORM_OWNER_NAME: 'Platform owner', CREDENTIAL_HANDOFF_KEY: 'test-handoff-key-with-at-least-32-characters', WEB_ORIGINS: 'http://127.0.0.1:5273,http://127.0.0.1:5274' } },
    { command: 'node ../../user-app/node_modules/vite/bin/vite.js ../../user-app --host 127.0.0.1 --port 5273 --strictPort', url: 'http://127.0.0.1:5273', timeout: 180_000, reuseExistingServer: false, env: { API_PORT: '3202', FRONTEND_PORT: '5273' } },
  ],
});
