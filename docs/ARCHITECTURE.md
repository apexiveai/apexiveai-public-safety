# APEXIVEAI PUBLIC SAFETY — Architecture Baseline

## Product boundary
Police and traffic operations platform for authorized government customers. The product supports records, workflow, evidence custody, citations, reporting and administration. It does not make law-enforcement decisions or infer guilt/risk.

## Architecture
- Modular monolith backend (FastAPI) with explicit domain boundaries.
- React web client, .NET WPF desktop client, Flutter Android client.
- PostgreSQL + PostGIS; Redis for cache/ephemeral coordination; object storage for attachments.
- Keycloak OIDC; API validates signed JWTs using JWKS.
- Append-only audit events; production audit storage should be exported to separately controlled immutable/WORM storage.

## Production gates
1. Replace development `create_all` with Alembic migrations before production.
2. Set `AUTH_ENABLED=true`; configure public HTTPS issuer URL, API audience and client redirect origins.
3. Remove development credentials and rotate all secrets.
4. Enforce organization, department and station scopes in every query and write path.
5. Add rate limits, CSRF protections where applicable, security headers, backup encryption and restore drills.
6. Complete threat modeling, privacy impact assessment, penetration testing and customer authorization.
7. Use dedicated customer environments and customer-controlled keys for government deployments.

## Initial domains
Identity, organization, police RMS, case management, evidence, traffic citations, vehicle verification, accidents, patrol, dispatch, GIS, analytics and audit.
