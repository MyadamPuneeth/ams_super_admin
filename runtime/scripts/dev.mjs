import { bootstrapPlatformOwner, embedded, migrate, seed } from './database.mjs';
import { setupLocalPostgres } from './local-postgres-setup.mjs';
import { spawn } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import net from 'node:net';
import { resolve } from 'node:path';

if (process.env.NODE_ENV === 'production') throw new Error('The local runner cannot run in production.');
const appRoot = resolve(fileURLToPath(new URL('../..', import.meta.url)));
const apiRoot = resolve(appRoot, 'runtime/api');
const testMode = process.argv.includes('--test');
const externalDatabase = process.argv.includes('--external-db');
const startFrontend = process.argv.includes('--frontend');
const startApi = process.argv.includes('--api') || startFrontend;
const option = name => process.argv.find(value => value.startsWith(`--${name}=`))?.slice(name.length + 3);
const apiPort = Number(option('api-port') || process.env.API_PORT || 3001);
const frontendPort = Number(option('frontend-port') || process.env.FRONTEND_PORT || 5173);
if (!Number.isInteger(apiPort) || !Number.isInteger(frontendPort)) throw new Error('API and frontend ports must be integers.');
if (externalDatabase && (!process.env.DATABASE_URL || !process.env.MIGRATION_DATABASE_URL)) throw new Error('Set DATABASE_URL and MIGRATION_DATABASE_URL in .env.');
const database = externalDatabase
  ? { appUrl: process.env.DATABASE_URL, adminUrl: process.env.MIGRATION_DATABASE_URL }
  : await embedded({ port: testMode ? 57000 + Math.floor(Math.random() * 1000) : 55432, directory: resolve(appRoot, testMode ? `.local/e2e-${process.pid}` : '.local/postgres') });
const children = [];
let stopping = false;
async function stop(code = 0) {
  if (stopping) return;
  stopping = true;
  for (const child of children) child.kill();
  if (database.server) await database.server.stop();
  process.exit(code);
}
process.on('SIGINT', () => void stop()); process.on('SIGTERM', () => void stop());
function run(command, args, extra = {}) {
  const child = spawn(command, args, { cwd: appRoot, stdio: 'inherit', windowsHide: true, env: { ...process.env, ...extra } });
  children.push(child); child.on('error', error => { console.error(error.message); void stop(1); }); return child;
}
async function assertFree(port) {
  await new Promise((done, reject) => {
    const listener = net.createServer();
    listener.once('error', error => reject(new Error(`Port ${port} is unavailable. Stop its owner before starting this application.`, { cause: error })));
    listener.listen(port, '127.0.0.1', () => listener.close(done));
  });
}
try {
  await Promise.all([startApi && assertFree(apiPort), startFrontend && assertFree(frontendPort)].filter(Boolean));
  if (externalDatabase) await setupLocalPostgres(database.adminUrl);
  await migrate(database.adminUrl); await seed(database.adminUrl); await bootstrapPlatformOwner(database.adminUrl);
  const origins = process.env.WEB_ORIGINS || 'http://localhost:5173,http://localhost:5174,http://localhost:5175';
  if (startApi) {
    const api = run('python', ['-m', 'uv', 'run', '--project', apiRoot, 'uvicorn', 'ams_api.main:app', '--host', '127.0.0.1', '--port', String(apiPort), ...(testMode ? [] : ['--reload'])], {
      DATABASE_URL: database.appUrl, NODE_ENV: testMode ? 'test' : 'development', DEV_AUTH: 'true', PORT: String(apiPort), WEB_ORIGINS: origins,
      USER_APP_ORIGIN: process.env.USER_APP_ORIGIN || 'http://localhost:5173', MOBILE_APP_ORIGIN: process.env.MOBILE_APP_ORIGIN || 'http://localhost:5175', UV_CACHE_DIR: resolve(appRoot, '.local/uv-cache'),
    });
    api.on('exit', code => { if (!stopping) void stop(code || 1); });
  }
  if (startFrontend) {
    const web = run(process.execPath, [resolve(appRoot, 'node_modules/vite/bin/vite.js'), '--host', '127.0.0.1'], { API_PORT: String(apiPort), FRONTEND_PORT: String(frontendPort) });
    web.on('exit', code => { if (!stopping) void stop(code || 1); });
  }
  console.log(startFrontend ? `Application: http://localhost:${frontendPort} · API: http://127.0.0.1:${apiPort}` : `API: http://127.0.0.1:${apiPort}`);
} catch (error) { console.error(error); await stop(1); }
