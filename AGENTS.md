# Repository Guidelines

## Project Structure & Module Organization

This is the AMS platform-owner frontend. Keep browser code in `src/`: `main.tsx` is the React entry point and `style.css` contains its styling. The Vite and TypeScript configuration lives at the repository root.

`runtime/` contains the local service stack: FastAPI code is in `runtime/api/ams_api/`, PostgreSQL migrations are in `runtime/api/prisma/migrations/`, and the generated TypeScript client is in `runtime/api-client/`. Runtime scripts belong in `runtime/scripts/`; end-to-end tests are in `runtime/tests/tests/e2e/` and API tests in `runtime/api/tests/`.

## Build, Test, and Development Commands

- `npm run dev` starts this frontend with the API against the configured external PostgreSQL database.
- `npm run dev:preview-db` starts the frontend with the isolated preview database.
- `npm run build` runs TypeScript validation and produces the Vite production build.
- `npm run typecheck` checks TypeScript without emitting files.
- `npm test` runs the API integration-test wrapper; `npm run contracts` regenerates the OpenAPI client artifacts when API routes change.

Use Node.js 22.12+ and Python 3.12+. Copy an example environment file to `.env`; never commit credentials or local database URLs.

## Coding Style & Naming Conventions

Use TypeScript with strict typing. Match the existing two-space indentation, semicolons, single quotes, and PascalCase React component/type names. Use camelCase for variables and functions; React hooks remain `useX`. Keep API route, schema, and database changes aligned with generated client types rather than duplicating request types in the UI.

Python follows the existing `snake_case` functions/modules and `PascalCase` classes. Make authorization and tenant-scoping checks explicit in backend changes.

## Testing Guidelines

Add backend coverage to `runtime/api/tests/test_*.py`; use pytest-style `test_*` methods and assertions. Add browser workflows to `runtime/tests/tests/e2e/*.spec.ts` using Playwright's accessible locators (`getByRole`, `getByLabel`). Test both success and authorization/tenant boundaries for API work. Run the smallest relevant command before opening a PR, then run `npm run build` for UI changes.

## Commit & Pull Request Guidelines

The available history starts with `Initial super admin app`, so no established commit convention exists. Use short imperative subjects, for example `Add academy suspension status`. Keep commits focused.

PRs should explain the user-visible change, link the issue when applicable, list validation commands, and include screenshots for UI changes. Call out migrations, environment variables, or regenerated API-client files explicitly.
