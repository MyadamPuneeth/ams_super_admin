import { mkdirSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import openapiTS, { astToString } from 'openapi-typescript';
const source = "import json; from ams_api.main import app; print(json.dumps(app.openapi()))";
const document = JSON.parse(execFileSync('python', ['-m', 'uv', 'run', '--project', 'apps/api', 'python', '-c', source], { encoding: 'utf8' }));
mkdirSync('packages/api-client/src', { recursive: true });
writeFileSync('packages/api-client/openapi.json', JSON.stringify(document, null, 2) + '\n');
writeFileSync('packages/api-client/src/schema.d.ts', astToString(await openapiTS(document)));
console.log('Generated OpenAPI document and client types from FastAPI routes.');
