# AMS

AMS is a multi-academy table tennis management platform. The first completed foundation provides secure academy workspaces, branches and tables, staff invitations, access management, audit records and platform onboarding.

## Applications

- `user-app` on http://localhost:5173 for academy staff and members.
- `super-admin-app` on http://localhost:5174 for academy onboarding and workspace status.
- `mobile-app` on http://localhost:5175 for installable attendance check-in.

## Run locally

Requirements: Node.js 22.12 or later, Python 3.12 or later, and the configured local PostgreSQL service.

```powershell
npm install
python -m pip install uv
npm run dev
```

The command applies only pending migrations to the configured native database, starts all three applications, and preserves data after AMS stops. Use `npm run dev:preview-db` only when you need the isolated bundled preview database.

To run one application with its own FastAPI process, use one of these commands:

```powershell
npm run dev:user
npm run dev:super-admin
npm run dev:mobile
npm run dev:api
```

Each application command validates PostgreSQL access, applies pending migrations, and starts the API on port 3001 plus the selected frontend. Run only one of these individual commands at a time because each owns port 3001; use `npm run dev` when you need all three frontends together.

The API documentation is available at [http://127.0.0.1:3001/api/docs](http://127.0.0.1:3001/api/docs).

## Use your persistent local PostgreSQL server

AMS can use the PostgreSQL service installed on your computer, which lets pgAdmin connect even when the development server is stopped.

1. In pgAdmin, confirm that you can connect to your existing PostgreSQL service at `127.0.0.1:5432` using the administrator password you chose when PostgreSQL was installed.
2. Copy `.env.local-postgres.example` to `.env` and replace `REPLACE_WITH_YOUR_POSTGRES_PASSWORD` with your PostgreSQL administrator password.
3. Start AMS with:

```powershell
npm run dev
```

The command creates the `ams` database if needed, installs the restricted `ams_app` role, applies pending AMS migrations and seeds the database only if it is empty. In pgAdmin, connect to `127.0.0.1:5432`, database `ams`, as `postgres` to inspect all tables. The application connects as the restricted `ams_app` role, so its row-level security rules remain active.

## Verification

```powershell
npm test
npm run test:e2e
npm run check
```

`npm test` runs the FastAPI pytest suite against an isolated PostgreSQL database and verifies tenant policies, invitation races, revoked membership and suspension. `npm run test:e2e` verifies the real browser paths and responsive layouts.
