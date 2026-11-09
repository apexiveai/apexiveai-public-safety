from uuid import uuid4

import pytest
from fastapi import HTTPException
from pydantic import ValidationError

from app.main import app
from app.routers.rms import _assert_org_access, _require_role
from app.schemas import EvidenceCreate


def test_rms_routes_are_registered():
    paths = app.openapi()["paths"]
    assert "/api/v1/rms/persons" in paths
    assert "/api/v1/rms/cases/{case_id}/approvals" in paths
    assert "/api/v1/rms/evidence/{evidence_id}/custody" in paths


def test_evidence_storage_reference_rejects_public_urls():
    with pytest.raises(ValidationError):
        EvidenceCreate(
            evidence_number="EVD-001",
            description="Sealed evidence package",
            evidence_type="DOCUMENT",
            storage_reference="https://example.invalid/evidence",
        )


def test_rms_roles_and_organization_scope_are_enforced():
    with pytest.raises(HTTPException) as role_error:
        _require_role({"roles": ["AUDITOR"]}, {"CASE_INVESTIGATOR"})
    assert role_error.value.status_code == 403

    with pytest.raises(HTTPException) as scope_error:
        _assert_org_access({"roles": ["CASE_INVESTIGATOR"], "org_id": str(uuid4())}, uuid4())
    assert scope_error.value.status_code == 403
