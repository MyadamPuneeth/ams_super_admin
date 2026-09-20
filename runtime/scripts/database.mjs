import EmbeddedPostgres from 'embedded-postgres';
import pg from 'pg';
import { existsSync, mkdirSync, readdirSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';
import { createHash } from 'node:crypto';

const appRoot = resolve(fileURLToPath(new URL('../..', import.meta.url)));
const migrationRoot = resolve(appRoot, 'runtime/api/prisma/migrations');
const seedFile = resolve(appRoot, 'runtime/scripts/seed.sql');
export const localUrl = 'postgresql://ams_app:ams_local_only@127.0.0.1:55432/ams';
export const localAdminUrl = 'postgresql://postgres:ams_local_admin@127.0.0.1:55432/ams';
export async function embedded({ port = 55432, directory = resolve(appRoot, '.local/postgres') } = {}) {
  mkdirSync(directory, { recursive: true });
  const server = new EmbeddedPostgres({ databaseDir: directory, user: 'postgres', password: 'ams_local_admin', port, persistent: true, postgresFlags: ['-h', '127.0.0.1'], onLog: () => {}, onError: message => { if (String(message).includes('FATAL')) console.error(String(message)); } });
  if (!existsSync(resolve(directory, 'PG_VERSION'))) await server.initialise();
  await server.start();
  const connection = server.getPgClient('postgres', '127.0.0.1'); await connection.connect();
  try {
    if (!(await connection.query("SELECT 1 FROM pg_database WHERE datname = 'ams'")).rowCount) await connection.query('CREATE DATABASE ams');
    if (!(await connection.query("SELECT 1 FROM pg_roles WHERE rolname = 'ams_app'")).rowCount) await connection.query("CREATE ROLE ams_app LOGIN PASSWORD 'ams_local_only' NOSUPERUSER NOBYPASSRLS NOCREATEDB NOCREATEROLE");
  } finally { await connection.end(); }
  return { server, adminUrl: `postgresql://postgres:ams_local_admin@127.0.0.1:${port}/ams`, appUrl: `postgresql://ams_app:ams_local_only@127.0.0.1:${port}/ams` };
}
export async function migrate(connectionString) {
  const client = new pg.Client({ connectionString }); await client.connect();
  try {
    await client.query('SELECT pg_advisory_lock(71420919)');
    await client.query('CREATE TABLE IF NOT EXISTS public.ams_migrations (name text PRIMARY KEY, checksum text NOT NULL, applied_at timestamptz NOT NULL DEFAULT now())');
    for (const name of readdirSync(migrationRoot).sort().filter(n => existsSync(resolve(migrationRoot, n, 'migration.sql')))) {
      const sql = readFileSync(resolve(migrationRoot, name, 'migration.sql'), 'utf8'); const checksum = createHash('sha256').update(sql).digest('hex');
      const result = await client.query('SELECT checksum FROM public.ams_migrations WHERE name = $1', [name]);
      if (result.rowCount) { if (result.rows[0].checksum !== checksum) throw new Error(`Applied migration changed: ${name}`); continue; }
      await client.query('BEGIN');
      try { await client.query(sql); await client.query('INSERT INTO public.ams_migrations(name, checksum) VALUES($1, $2)', [name, checksum]); await client.query('COMMIT'); }
      catch (error) { await client.query('ROLLBACK'); throw error; }
    }
  } finally { await client.query('SELECT pg_advisory_unlock(71420919)'); await client.end(); }
}
export async function seed(connectionString) {
  const client = new pg.Client({ connectionString }); await client.connect();
  try { await client.query('BEGIN'); if ((await client.query('SELECT 1 FROM "Academy" LIMIT 1')).rowCount) { await client.query('COMMIT'); return; } await client.query(readFileSync(seedFile, 'utf8')); await client.query('COMMIT'); }
  catch (error) { await client.query('ROLLBACK'); throw error; }
  finally { await client.end(); }
}
