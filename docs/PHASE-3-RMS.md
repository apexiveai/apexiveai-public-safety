# Phase 3 — Police Records Management System

Phase 3 adds organization-scoped RMS APIs for person records, cases, assignments, investigation entries, evidence metadata, custody events, approvals, and audit events. The web dashboard includes a searchable directory of the 7 regions, 7 states, and Naypyidaw Union Territory.

## API

All paths below are under `/api/v1/rms`. Requests require the existing authenticated principal and role checks. IDs are UUIDs unless noted.

| Method | Path | Purpose |
|---|---|---|
| POST / GET | `/persons` | Create or search person records (`organization_id`, optional `search`, capped `limit`) |
| POST / GET | `/cases` | Create or list organization-scoped cases |
| POST / GET | `/cases/{case_id}/persons/{person_id}`; `/cases/{case_id}/persons` | Link a person to a case and read case-person links |
| POST / GET | `/cases/{case_id}/assignments` | Assign a case; read assignment history |
| POST | `/cases/{case_id}/start-investigation` | Move an open case into investigation |
| POST / GET | `/cases/{case_id}/investigation-entries` | Append and read investigation notes |
| POST / GET | `/cases/{case_id}/evidence` | Register and list evidence metadata |
| POST / GET | `/evidence/{evidence_id}/custody` | Append a custody event and read the custody chain |
| POST | `/cases/{case_id}/submit-for-approval` | Submit an open or investigated case |
| POST / GET | `/cases/{case_id}/approvals` | Record an approval decision and read approval history |

### Workflow rules

- Cases are created as `OPEN`; an authorized case-writing role can start investigation, then submit for approval.
- Only `APS_ADMIN`, `GOV_ADMIN`, or `DEPT_ADMIN` can assign cases or approve/reject them.
- A case creator cannot approve their own case. Approval closes the case; rejection returns it to `UNDER_INVESTIGATION`.
- Investigation entries and custody events are append-only through this API.
- Evidence must first be received into custody. Transfers/returns must identify the current custodian as the source.
- Person, case, evidence, and workflow reads/writes generate application audit events. Search text and note/evidence content are not copied into audit details.
- `AUDITOR` can read approval history and the existing organization audit endpoint, but not person or case record contents.
- Access is organization-scoped; the platform administrator role is the only cross-organization exception. Department/station-level claims and assignment-member validation still require an identity-directory integration.

## Data and deployment boundaries

The app's development startup uses SQLAlchemy `create_all`; this is not a production schema migration strategy. Create and review versioned Alembic migrations for all Phase 3 tables before deploying. Database audit rows are not tamper-proof; export them to independently controlled immutable storage for operational use.

Person names, dates of birth, and notes are sensitive. Do not enter real records in this unauthenticated development environment. A production deployment must enable Keycloak/OIDC, enforce customer-specific organization and department scope, apply encryption and retention policies, and complete legal/privacy review and security testing. Evidence `storage_reference` is an internal object key only; this API does not upload evidence files. Store files in an approved encrypted object store and add malware scanning, integrity hashes, retention, and authorization before enabling uploads.

## National directory and live video

The dashboard directory contains Ayeyarwady, Bago, Magway, Mandalay, Sagaing, Tanintharyi, Yangon; Chin, Kachin, Kayah, Kayin, Mon, Rakhine, Shan; and Naypyidaw Union Territory. It is an administrative catalog and schematic, not a geographic GIS, operational connectivity check, or live map.

No RTSP/WebRTC provider, camera endpoints, stream credentials, recording pipeline, or regional source systems are configured. The dashboard intentionally reports zero connected feeds and does not display placeholder video as if it were live. Before any authorized deployment, select a customer-approved video provider and define authenticated operator access, encryption, consent/notice and legal basis, audit logs, retention/deletion, and incident-response controls. Live streaming is therefore **not yet operational** in this foundation build.
