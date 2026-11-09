from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_principal
from app.models import (
    AuditLog,
    CaseApproval,
    CaseAssignment,
    CasePersonLink,
    CaseRecord,
    Department,
    EvidenceCustody,
    EvidenceItem,
    InvestigationEntry,
    Organization,
    PersonRecord,
    Station,
)
from app.schemas import (
    CaseApprovalCreate,
    CaseApprovalRead,
    CaseAssignmentCreate,
    CaseAssignmentRead,
    CaseCreate,
    CaseRead,
    EvidenceCreate,
    EvidenceCustodyCreate,
    EvidenceCustodyRead,
    EvidenceRead,
    InvestigationEntryCreate,
    InvestigationEntryRead,
    PersonCaseLinkCreate,
    PersonCaseLinkRead,
    PersonCreate,
    PersonRead,
)

router = APIRouter(prefix="/api/v1/rms", tags=["Police RMS"])

CASE_READ_ROLES = {
    "APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN", "POLICE_OFFICER", "CASE_INVESTIGATOR",
}
CASE_WRITE_ROLES = {"APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN", "POLICE_OFFICER", "CASE_INVESTIGATOR"}
EVIDENCE_ROLES = CASE_WRITE_ROLES | {"EVIDENCE_CUSTODIAN"}
APPROVAL_ROLES = {"APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN"}


def _require_role(principal: dict, roles: set[str]) -> None:
    if not roles.intersection(principal.get("roles", [])):
        raise HTTPException(status_code=403, detail="Insufficient permissions")


def _assert_org_access(principal: dict, organization_id: UUID) -> None:
    if "APS_ADMIN" not in principal.get("roles", []) and str(principal.get("org_id", "")) != str(organization_id):
        raise HTTPException(status_code=403, detail="Organization scope denied")


def _audit(
    db: Session,
    principal: dict,
    organization_id: UUID,
    action: str,
    resource_type: str,
    resource_id: UUID,
    details: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            organization_id=str(organization_id),
            actor_sub=str(principal["sub"]),
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            details=details or {},
        )
    )


def _get_case(db: Session, principal: dict, case_id: UUID) -> CaseRecord:
    case = db.get(CaseRecord, case_id)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")
    _assert_org_access(principal, case.organization_id)
    return case


def _ensure_active_case(case: CaseRecord) -> None:
    if case.status in {"CLOSED", "PENDING_APPROVAL"}:
        raise HTTPException(status_code=409, detail="Case is not accepting workflow changes")


@router.post("/persons", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(
    payload: PersonCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_WRITE_ROLES)
    _assert_org_access(principal, payload.organization_id)
    if db.get(Organization, payload.organization_id) is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    existing = db.scalar(
        select(PersonRecord).where(
            PersonRecord.organization_id == payload.organization_id,
            PersonRecord.record_number == payload.record_number,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Person record number already exists")
    row = PersonRecord(**payload.model_dump(), created_by=str(principal["sub"]))
    db.add(row)
    db.flush()
    _audit(db, principal, row.organization_id, "PERSON_RECORD_CREATED", "person", row.id)
    db.commit()
    db.refresh(row)
    return row


@router.get("/persons", response_model=list[PersonRead])
def list_persons(
    organization_id: UUID = Query(...),
    search: str | None = Query(default=None, min_length=2, max_length=100),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_READ_ROLES)
    _assert_org_access(principal, organization_id)
    statement = select(PersonRecord).where(PersonRecord.organization_id == organization_id)
    if search:
        statement = statement.where(PersonRecord.full_name.ilike(f"%{search}%"))
    rows = list(db.scalars(statement.order_by(PersonRecord.created_at.desc()).limit(limit)).all())
    _audit(db, principal, organization_id, "PERSON_RECORDS_READ", "person_search", organization_id,
           {"result_count": len(rows)})
    db.commit()
    return rows


@router.post("/cases", response_model=CaseRead, status_code=status.HTTP_201_CREATED)
def create_case(
    payload: CaseCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_WRITE_ROLES)
    _assert_org_access(principal, payload.organization_id)
    station = db.get(Station, payload.station_id)
    if station is None:
        raise HTTPException(status_code=422, detail="Station does not exist")
    department = db.get(Department, station.department_id)
    if department is None or department.organization_id != payload.organization_id:
        raise HTTPException(status_code=422, detail="Station is not part of the specified organization")
    duplicate = db.scalar(
        select(CaseRecord).where(
            CaseRecord.organization_id == payload.organization_id,
            CaseRecord.case_number == payload.case_number,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Case number already exists")
    row = CaseRecord(**payload.model_dump(), created_by=str(principal["sub"]))
    db.add(row)
    db.flush()
    _audit(db, principal, row.organization_id, "CASE_CREATED", "case", row.id,
           {"case_number": row.case_number})
    db.commit()
    db.refresh(row)
    return row


@router.get("/cases", response_model=list[CaseRead])
def list_cases(
    organization_id: UUID = Query(...),
    limit: int = Query(default=100, ge=1, le=200),
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_READ_ROLES)
    _assert_org_access(principal, organization_id)
    rows = list(
        db.scalars(
            select(CaseRecord)
            .where(CaseRecord.organization_id == organization_id)
            .order_by(CaseRecord.created_at.desc())
            .limit(limit)
        ).all()
    )
    _audit(db, principal, organization_id, "CASE_RECORDS_READ", "case_search", organization_id,
           {"result_count": len(rows)})
    db.commit()
    return rows


@router.get("/cases/{case_id}/persons", response_model=list[PersonCaseLinkRead])
def list_case_persons(
    case_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_READ_ROLES)
    case = _get_case(db, principal, case_id)
    rows = list(
        db.scalars(
            select(CasePersonLink)
            .where(CasePersonLink.case_id == case.id)
            .order_by(CasePersonLink.created_at.asc())
        ).all()
    )
    _audit(db, principal, case.organization_id, "CASE_PERSON_LINKS_READ", "case_person_link", case.id,
           {"result_count": len(rows)})
    db.commit()
    return rows


@router.post("/cases/{case_id}/persons/{person_id}", response_model=PersonCaseLinkRead, status_code=201)
def link_person_to_case(
    case_id: UUID,
    person_id: UUID,
    payload: PersonCaseLinkCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_WRITE_ROLES)
    case = _get_case(db, principal, case_id)
    _ensure_active_case(case)
    person = db.get(PersonRecord, person_id)
    if person is None or person.organization_id != case.organization_id:
        raise HTTPException(status_code=404, detail="Person record not found in this organization")
    existing = db.scalar(
        select(CasePersonLink).where(
            CasePersonLink.case_id == case.id,
            CasePersonLink.person_id == person.id,
        )
    )
    if existing:
        raise HTTPException(status_code=409, detail="Person is already linked to this case")
    row = CasePersonLink(
        case_id=case.id,
        person_id=person.id,
        relationship_type=payload.relationship_type,
        created_by=str(principal["sub"]),
    )
    db.add(row)
    db.flush()
    _audit(db, principal, case.organization_id, "PERSON_LINKED_TO_CASE", "case_person_link", row.id,
           {"case_id": str(case.id), "person_id": str(person.id)})
    db.commit()
    db.refresh(row)
    return row


@router.post("/cases/{case_id}/assignments", response_model=CaseAssignmentRead, status_code=201)
def assign_case(
    case_id: UUID,
    payload: CaseAssignmentCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, APPROVAL_ROLES)
    case = _get_case(db, principal, case_id)
    _ensure_active_case(case)
    previous = db.scalars(
        select(CaseAssignment).where(CaseAssignment.case_id == case.id, CaseAssignment.active.is_(True))
    ).all()
    for assignment in previous:
        assignment.active = False
    row = CaseAssignment(
        case_id=case.id,
        assignee_sub=payload.assignee_sub,
        assigned_by=str(principal["sub"]),
    )
    db.add(row)
    _audit(db, principal, case.organization_id, "CASE_ASSIGNED", "case_assignment", row.id,
           {"case_id": str(case.id), "assignee_sub": payload.assignee_sub})
    db.commit()
    db.refresh(row)
    return row


@router.get("/cases/{case_id}/assignments", response_model=list[CaseAssignmentRead])
def list_case_assignments(
    case_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_READ_ROLES)
    case = _get_case(db, principal, case_id)
    rows = list(
        db.scalars(
            select(CaseAssignment)
            .where(CaseAssignment.case_id == case.id)
            .order_by(CaseAssignment.created_at.asc())
        ).all()
    )
    _audit(db, principal, case.organization_id, "CASE_ASSIGNMENT_HISTORY_READ", "case_assignment", case.id,
           {"result_count": len(rows)})
    db.commit()
    return rows


@router.post("/cases/{case_id}/start-investigation", response_model=CaseRead)
def start_investigation(
    case_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_WRITE_ROLES)
    case = _get_case(db, principal, case_id)
    if case.status != "OPEN":
        raise HTTPException(status_code=409, detail="Only open cases can start an investigation")
    case.status = "UNDER_INVESTIGATION"
    _audit(db, principal, case.organization_id, "INVESTIGATION_STARTED", "case", case.id)
    db.commit()
    db.refresh(case)
    return case


@router.post("/cases/{case_id}/investigation-entries", response_model=InvestigationEntryRead, status_code=201)
def create_investigation_entry(
    case_id: UUID,
    payload: InvestigationEntryCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_WRITE_ROLES)
    case = _get_case(db, principal, case_id)
    _ensure_active_case(case)
    row = InvestigationEntry(
        case_id=case.id,
        author_sub=str(principal["sub"]),
        entry_type=payload.entry_type,
        content=payload.content,
    )
    db.add(row)
    db.flush()
    _audit(db, principal, case.organization_id, "INVESTIGATION_ENTRY_CREATED", "investigation_entry", row.id,
           {"case_id": str(case.id), "entry_type": row.entry_type})
    db.commit()
    db.refresh(row)
    return row


@router.get("/cases/{case_id}/investigation-entries", response_model=list[InvestigationEntryRead])
def list_investigation_entries(
    case_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_READ_ROLES)
    case = _get_case(db, principal, case_id)
    rows = list(
        db.scalars(
            select(InvestigationEntry)
            .where(InvestigationEntry.case_id == case.id)
            .order_by(InvestigationEntry.created_at.asc())
        ).all()
    )
    _audit(db, principal, case.organization_id, "INVESTIGATION_HISTORY_READ", "investigation_entry", case.id,
           {"result_count": len(rows)})
    db.commit()
    return rows


@router.post("/cases/{case_id}/evidence", response_model=EvidenceRead, status_code=201)
def register_evidence(
    case_id: UUID,
    payload: EvidenceCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, EVIDENCE_ROLES)
    case = _get_case(db, principal, case_id)
    _ensure_active_case(case)
    duplicate = db.scalar(
        select(EvidenceItem).where(
            EvidenceItem.case_id == case.id,
            EvidenceItem.evidence_number == payload.evidence_number,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Evidence number already exists")
    row = EvidenceItem(**payload.model_dump(), case_id=case.id, recorded_by=str(principal["sub"]))
    db.add(row)
    db.flush()
    _audit(db, principal, case.organization_id, "EVIDENCE_REGISTERED", "evidence", row.id,
           {"case_id": str(case.id), "evidence_number": row.evidence_number})
    db.commit()
    db.refresh(row)
    return row


@router.get("/cases/{case_id}/evidence", response_model=list[EvidenceRead])
def list_evidence(
    case_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, EVIDENCE_ROLES)
    case = _get_case(db, principal, case_id)
    rows = list(
        db.scalars(
            select(EvidenceItem)
            .where(EvidenceItem.case_id == case.id)
            .order_by(EvidenceItem.created_at.desc())
        ).all()
    )
    _audit(db, principal, case.organization_id, "EVIDENCE_REGISTER_READ", "evidence", case.id,
           {"result_count": len(rows)})
    db.commit()
    return rows


@router.post("/evidence/{evidence_id}/custody", response_model=EvidenceCustodyRead, status_code=201)
def record_custody(
    evidence_id: UUID,
    payload: EvidenceCustodyCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, EVIDENCE_ROLES)
    evidence = db.get(EvidenceItem, evidence_id)
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    case = _get_case(db, principal, evidence.case_id)
    latest = db.scalar(
        select(EvidenceCustody)
        .where(EvidenceCustody.evidence_id == evidence.id)
        .order_by(EvidenceCustody.created_at.desc())
        .limit(1)
    )
    if payload.action == "RECEIVE" and latest:
        raise HTTPException(status_code=409, detail="Evidence already has a custody record")
    if payload.action in {"TRANSFER", "RETURN"}:
        if latest is None:
            raise HTTPException(status_code=409, detail="Evidence must be received before transfer or return")
        if payload.from_custodian != latest.to_custodian:
            raise HTTPException(status_code=409, detail="Current custodian does not match the custody chain")
    row = EvidenceCustody(
        evidence_id=evidence.id,
        action=payload.action,
        from_custodian=payload.from_custodian,
        to_custodian=payload.to_custodian,
        notes=payload.notes,
        recorded_by=str(principal["sub"]),
    )
    db.add(row)
    db.flush()
    _audit(db, principal, case.organization_id, "EVIDENCE_CUSTODY_RECORDED", "evidence_custody", row.id,
           {"evidence_id": str(evidence.id), "action": row.action})
    db.commit()
    db.refresh(row)
    return row


@router.get("/evidence/{evidence_id}/custody", response_model=list[EvidenceCustodyRead])
def list_custody(
    evidence_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, EVIDENCE_ROLES)
    evidence = db.get(EvidenceItem, evidence_id)
    if evidence is None:
        raise HTTPException(status_code=404, detail="Evidence item not found")
    case = _get_case(db, principal, evidence.case_id)
    rows = list(
        db.scalars(
            select(EvidenceCustody)
            .where(EvidenceCustody.evidence_id == evidence.id)
            .order_by(EvidenceCustody.created_at.asc())
        ).all()
    )
    _audit(db, principal, case.organization_id, "EVIDENCE_CUSTODY_READ", "evidence_custody", evidence.id,
           {"result_count": len(rows)})
    db.commit()
    return rows


@router.post("/cases/{case_id}/submit-for-approval", response_model=CaseRead)
def submit_case_for_approval(
    case_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, CASE_WRITE_ROLES)
    case = _get_case(db, principal, case_id)
    if case.status not in {"OPEN", "UNDER_INVESTIGATION"}:
        raise HTTPException(status_code=409, detail="Case cannot be submitted from its current status")
    case.status = "PENDING_APPROVAL"
    _audit(db, principal, case.organization_id, "CASE_SUBMITTED_FOR_APPROVAL", "case", case.id)
    db.commit()
    db.refresh(case)
    return case


@router.post("/cases/{case_id}/approvals", response_model=CaseApprovalRead, status_code=201)
def review_case(
    case_id: UUID,
    payload: CaseApprovalCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, APPROVAL_ROLES)
    case = _get_case(db, principal, case_id)
    if case.status != "PENDING_APPROVAL":
        raise HTTPException(status_code=409, detail="Case is not pending approval")
    if case.created_by == str(principal["sub"]):
        raise HTTPException(status_code=403, detail="The case creator cannot approve their own case")
    case.status = "CLOSED" if payload.decision == "APPROVE" else "UNDER_INVESTIGATION"
    row = CaseApproval(
        case_id=case.id,
        decision=payload.decision,
        reviewer_sub=str(principal["sub"]),
        notes=payload.notes,
    )
    db.add(row)
    db.flush()
    _audit(db, principal, case.organization_id, "CASE_APPROVAL_RECORDED", "case_approval", row.id,
           {"case_id": str(case.id), "decision": row.decision})
    db.commit()
    db.refresh(row)
    return row


@router.get("/cases/{case_id}/approvals", response_model=list[CaseApprovalRead])
def list_case_approvals(
    case_id: UUID,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    _require_role(principal, APPROVAL_ROLES | {"AUDITOR"})
    case = _get_case(db, principal, case_id)
    rows = list(
        db.scalars(
            select(CaseApproval)
            .where(CaseApproval.case_id == case.id)
            .order_by(CaseApproval.created_at.asc())
        ).all()
    )
    _audit(db, principal, case.organization_id, "CASE_APPROVAL_HISTORY_READ", "case_approval", case.id,
           {"result_count": len(rows)})
    db.commit()
    return rows
