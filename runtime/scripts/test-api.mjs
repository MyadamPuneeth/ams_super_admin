import { spawn } from 'node:child_process';
import { once } from 'node:events';
import { bootstrapPlatformOwner, embedded, migrate, seed } from './database.mjs';
import exitHook from 'async-exit-hook';

// embedded-postgres installs process hooks that conflict with a child test runner.
// This script owns shutdown explicitly in its finally block.
for (const event of ['beforeExit', 'message', 'exit', 'SIGHUP', 'SIGINT', 'SIGTERM', 'SIGBREAK']) exitHook.unhookEvent(event);

const port = 56000 + Math.floor(Math.random() * 1000);
const db = await embedded({ port, directory: `.local/integration-${Date.now()}` });
try {
  await migrate(db.adminUrl);
  await migrate(db.adminUrl);
  await seed(db.adminUrl);
  process.env.PLATFORM_OWNER_USERNAME = 'platform.owner'; process.env.PLATFORM_OWNER_PASSWORD = 'correct-horse-battery'; process.env.PLATFORM_OWNER_NAME = 'Platform owner';
  await bootstrapPlatformOwner(db.adminUrl);
  const child = spawn('python', ['-m', 'uv', 'run', '--project', 'runtime/api', 'pytest', 'runtime/api/tests'], {
    stdio: 'inherit', windowsHide: true,
    env: { ...process.env, DATABASE_URL: db.appUrl, NODE_ENV: 'test', DEV_AUTH: 'true', CREDENTIAL_HANDOFF_KEY: 'test-handoff-key-with-at-least-32-characters' },
  });
  const [code] = await once(child, 'exit');
  process.exitCode = code || 0;
} finally { await db.server.stop(); }
