# APEXIVEAI PUBLIC SAFETY

**Police + Traffic Operations | Web + Windows Desktop + Android**

Proprietary government enterprise software by ApexiveAI Company., Ltd.

## Current baseline: 0.1.0
Includes a runnable development foundation: FastAPI API, React dashboard, PostgreSQL/PostGIS, Redis, Keycloak realm bootstrap, initial organization/case/citation models, API health checks and audit event records.

## Quick start (Windows CMD)
```cmd
copy .env.example .env
docker compose up --build -d
cd frontend-web
npm install
npm run dev
```

Open Web: http://localhost:5173
API: http://localhost:8000
API docs: http://localhost:8000/docs
Keycloak: http://localhost:8080 (admin / change_this_keycloak_password)

## Important security notice
This is a development foundation, not an approved operational law-enforcement system. `AUTH_ENABLED=false` is strictly local-development mode. Do not load real citizen, case, evidence, vehicle or personnel data. Before production: enable OIDC, create Alembic migrations, enforce complete org/department/station scope, add immutable external audit storage, harden secrets/networking, complete legal/privacy review and security testing.

See `docs/ARCHITECTURE.md` and `docs/DEVELOPMENT.md`.
