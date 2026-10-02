import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { test } from 'node:test';
import { fileURLToPath } from 'node:url';

test('API startup rejects missing or short handoff keys before starting the database', () => {
  for (const key of ['', 'too-short']) {
    const result = spawnSync(process.execPath, [fileURLToPath(new URL('./dev.mjs', import.meta.url)), '--api'], {
      encoding: 'utf8', windowsHide: true,
      env: { ...process.env, NODE_ENV: 'development', CREDENTIAL_HANDOFF_KEY: key },
    });
    assert.equal(result.status, 1);
    assert.match(result.stderr, /CREDENTIAL_HANDOFF_KEY.*stop and restart npm run dev/);
  }
});
