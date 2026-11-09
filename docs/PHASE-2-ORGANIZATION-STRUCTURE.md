# Phase 2 — Organization Structure API

All endpoints require a valid authenticated principal when `AUTH_ENABLED=true`.

## Create a department

`POST /api/v1/departments`

```json
{
  "organization_id": "ORGANIZATION_UUID",
  "code": "POLICE_OPS",
  "name": "Police Operations Department",
  "department_type": "POLICE"
}
```

Allowed department types are uppercase identifiers such as `POLICE`, `TRAFFIC`, `INVESTIGATION`, `ADMINISTRATION`, and `EVIDENCE`. The API validates the identifier format, not a fixed catalog.

## List departments

`GET /api/v1/departments?organization_id=ORGANIZATION_UUID`

## Create a station

`POST /api/v1/stations`

```json
{
  "department_id": "DEPARTMENT_UUID",
  "code": "YGN-001",
  "name": "Example Station",
  "address": "Yangon Region"
}
```

## List stations

`GET /api/v1/stations?department_id=DEPARTMENT_UUID`

## Read audit events

`GET /api/v1/audit?organization_id=ORGANIZATION_UUID&limit=100`

Creation events are written in the same database transaction as the department or station record. The audit endpoint is read-only. This database audit table is an initial application audit trail, not yet tamper-proof external archival storage.

## Access rules

- `APS_ADMIN`, `GOV_ADMIN`, and `DEPT_ADMIN` can create departments and stations.
- `APS_ADMIN` can access across organizations.
- Other users must have a matching `org_id` claim.
- Department and station listing is available to authorized organization roles.
- Audit reads are limited to `APS_ADMIN`, `GOV_ADMIN`, `DEPT_ADMIN`, and `AUDITOR`.
- Never use the local development principal or real personal/case data in production.
