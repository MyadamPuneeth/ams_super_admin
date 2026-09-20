import { cpSync, existsSync, readdirSync, readFileSync, rmSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { dirname, relative, resolve } from 'node:path';
const appRoot = resolve(fileURLToPath(new URL('../..', import.meta.url)));
const source = resolve(appRoot, 'runtime'); const peers = ['mobile-app', 'super-admin-app'].map(name => resolve(dirname(appRoot), name, 'runtime'));
const ignore = new Set(['.venv', '__pycache__', '.pytest_cache', 'node_modules', '.local', 'dist', '.env', '.git']);
function digest(root, dir = root, result = new Map()) { for (const entry of readdirSync(dir, { withFileTypes: true })) { if (ignore.has(entry.name)) continue; const path = resolve(dir, entry.name); if (entry.isDirectory()) digest(root, path, result); else result.set(relative(root, path).replaceAll('\\', '/'), createHash('sha256').update(readFileSync(path)).digest('hex')); } return result; }
for (const peer of peers) {
  if (!existsSync(dirname(peer))) throw new Error(`Missing sibling application: ${dirname(peer)}`);
  if (!process.argv.includes('--check')) { rmSync(peer, { recursive: true, force: true }); cpSync(source, peer, { recursive: true, filter: path => !ignore.has(path.split(/[\\/]/).at(-1)) }); continue; }
  const left = digest(source), right = existsSync(peer) ? digest(peer) : new Map();
  if (left.size !== right.size || [...left].some(([file, value]) => right.get(file) !== value)) throw new Error(`Runtime copy differs: ${peer}`);
}
console.log(process.argv.includes('--check') ? 'Runtime copies match.' : 'Runtime copies synchronized.');
