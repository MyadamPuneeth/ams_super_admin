import { readFile } from 'node:fs/promises';
import pg from 'pg';

const { Client } = pg;

function databaseName(connectionUrl) {
  const name = decodeURIComponent(connectionUrl.pathname.slice(1));
  if (!/^[A-Za-z_][A-Za-z0-9_]*$/.test(name)) {
    throw new Error('MIGRATION_DATABASE_URL must contain a valid PostgreSQL database name.');
  }
  return name;
}

/**
 * Creates the configured local database once, then installs prerequisites that
 * must be owned by a PostgreSQL administrator. Schema changes remain in the
 * checksum-verified SQL migration history.
 */
export async function setupLocalPostgres(migrationUrl) {
  const target = new URL(migrationUrl);
  const name = databaseName(target);
  const maintenance = new URL(target);
  maintenance.pathname = '/postgres';

  const administrator = new Client({ connectionString: maintenance.toString() });
  await administrator.connect();
  try {
    const existing = await administrator.query('SELECT 1 FROM pg_database WHERE datname = $1', [name]);
    if (existing.rowCount === 0) {
      await administrator.query(`CREATE DATABASE "${name}"`);
      console.log(`Created persistent database ${name}.`);
    }
  } finally {
    await administrator.end();
  }

  const database = new Client({ connectionString: target.toString() });
  await database.connect();
  try {
    await database.query(await readFile(new URL('./local-postgres-bootstrap.sql', import.meta.url), 'utf8'));
  } finally {
    await database.end();
  }
}

if (process.argv[1] && new URL(`file:///${process.argv[1].replace(/\\/g, '/')}`).href === import.meta.url) {
  if (!process.env.MIGRATION_DATABASE_URL) {
    throw new Error('Set MIGRATION_DATABASE_URL in .env before setting up local PostgreSQL.');
  }
  await setupLocalPostgres(process.env.MIGRATION_DATABASE_URL);
  console.log('Persistent PostgreSQL prerequisites are ready.');
}
