import { migrate } from './database.mjs';
if (!process.env.MIGRATION_DATABASE_URL) throw new Error('Set MIGRATION_DATABASE_URL to your migration-owner connection. Provision the restricted ams_app role first.');
await migrate(process.env.MIGRATION_DATABASE_URL);
console.log('Database migrations applied.');
