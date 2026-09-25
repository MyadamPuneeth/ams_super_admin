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
npm start
```

Run this command from the application you want to launch. It applies pending migrations to the configured PostgreSQL database, then starts that app's Vite frontend and Python FastAPI backend. The apps share the same commands but use separate ports: user (5173/3001), super-admin (5174/3102), and mobile (5175/3003).

For the super-admin app, set `PLATFORM_OWNER_USERNAME`, `PLATFORM_OWNER_PASSWORD`, and `PLATFORM_OWNER_NAME` in `.env`. Startup securely hashes the password and creates or updates the PostgreSQL platform-owner account. Production also requires a random `PLATFORM_SESSION_SECRET` of at least 32 characters.

Academy onboarding also requires a stable `CREDENTIAL_HANDOFF_KEY` of at least 32 characters. Configure `SMTP_HOST`, `SMTP_PORT`, `SMTP_SECURITY` (`starttls`, `ssl`, or `none`), `SMTP_USERNAME`, `SMTP_PASSWORD`, and `SMTP_FROM` to email the first administrator's temporary credentials. If SMTP delivery fails, the academy is still created and the platform owner can retry from the dashboard.

## Startup options

```powershell
npm start
npm run start:api
npm run start:preview
```

`npm start` launches the frontend plus its Python API against the configured local PostgreSQL service. `npm run start:api` launches only the Python API. `npm run start:preview` launches the frontend plus Python API with an isolated embedded PostgreSQL database. The existing `npm run dev`, `npm run dev:api`, and `npm run dev:preview-db` commands remain equivalent aliases.

The API documentation is available at `http://127.0.0.1:<api-port>/api/docs`.

## Use your persistent local PostgreSQL server

AMS can use the PostgreSQL service installed on your computer, which lets pgAdmin connect even when the development server is stopped.

1. In pgAdmin, confirm that you can connect to your existing PostgreSQL service at `127.0.0.1:5432` using the administrator password you chose when PostgreSQL was installed.
2. Copy `.env.local-postgres.example` to `.env` and replace `REPLACE_WITH_YOUR_POSTGRES_PASSWORD` with your PostgreSQL administrator password.
3. Start AMS with:

```powershell
npm start
```

The command creates the `ams` database if needed, installs the restricted `ams_app` role, applies pending AMS migrations and seeds the database only if it is empty. In pgAdmin, connect to `127.0.0.1:5432`, database `ams`, as `postgres` to inspect all tables. The application connects as the restricted `ams_app` role, so its row-level security rules remain active.

## Verification

```powershell
npm run build
npm test
npm run test:e2e
npm run contracts
```

`npm run build` type-checks and builds the frontend. `npm test` runs the FastAPI pytest suite against an isolated PostgreSQL database. `npm run test:e2e` verifies platform-owner workflows in Chromium. `npm run contracts` regenerates and validates the FastAPI OpenAPI client contract.
