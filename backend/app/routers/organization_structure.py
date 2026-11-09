from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_principal
from app.models import AuditLog, Department, Organization, Station
from app.schemas import (
    DepartmentCreate,
    DepartmentRead,
    StationCreate,
    StationRead,
)

router = APIRouter(tags=["Organization Structure"])

DEPARTMENT_ROLES = {
    "APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN", "AUDITOR",
    "POLICE_OFFICER", "CASE_INVESTIGATOR", "TRAFFIC_OFFICER",
    "TRAFFIC_COMMANDER", "EVIDENCE_CUSTODIAN",
}
MANAGEMENT_ROLES = {"APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN"}


def _roles(principal: dict) -> set[str]:
    return set(principal.get("roles", []))


def _assert_org_access(principal: dict, organization_id: UUID) -> None:
    if "APS_ADMIN" in _roles(principal):
        return
    if str(principal.get("org_id", "")) != str(organization_id):
        raise HTTPException(status_code=403, detail="Organization scope denied")


def _audit(
    db: Session,
    principal: dict,
    organization_id: UUID,
    action: str,
    resource_type: str,
    resource_id: UUID,
    details: dict,
) -> None:
    db.add(
        AuditLog(
            organization_id=str(organization_id),
            actor_sub=str(principal["sub"]),
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id),
            details=details,
        )
    )


@router.post(
    "/api/v1/departments",
    response_model=DepartmentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_department(
    payload: DepartmentCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    if not _roles(principal).intersection(MANAGEMENT_ROLES):
        raise HTTPException(status_code=403, detail="Department management permission required")
    _assert_org_access(principal, payload.organization_id)

    organization = db.get(Organization, payload.organization_id)
    if organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    duplicate = db.scalar(
        select(Department).where(
            Department.organization_id == payload.organization_id,
            Department.code == payload.code,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Department code already exists in this organization")

    row = Department(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, principal, row.organization_id, "DEPARTMENT_CREATED", "department", row.id,
           {"code": row.code, "name": row.name, "department_type": row.department_type})
    db.commit()
    db.refresh(row)
    return row


@router.get("/api/v1/departments", response_model=list[DepartmentRead])
def list_departments(
    organization_id: UUID = Query(...),
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    if not _roles(principal).intersection(DEPARTMENT_ROLES):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    _assert_org_access(principal, organization_id)
    statement = (
        select(Department)
        .where(Department.organization_id == organization_id)
        .order_by(Department.name.asc())
    )
    return list(db.scalars(statement).all())


@router.post(
    "/api/v1/stations",
    response_model=StationRead,
    status_code=status.HTTP_201_CREATED,
)
def create_station(
    payload: StationCreate,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    if not _roles(principal).intersection(MANAGEMENT_ROLES):
        raise HTTPException(status_code=403, detail="Station management permission required")

    department = db.get(Department, payload.department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    _assert_org_access(principal, department.organization_id)

    duplicate = db.scalar(
        select(Station).where(
            Station.department_id == payload.department_id,
            Station.code == payload.code,
        )
    )
    if duplicate:
        raise HTTPException(status_code=409, detail="Station code already exists in this department")

    row = Station(**payload.model_dump())
    db.add(row)
    db.flush()
    _audit(db, principal, department.organization_id, "STATION_CREATED", "station", row.id,
           {"department_id": str(department.id), "code": row.code, "name": row.name})
    db.commit()
    db.refresh(row)
    return row


@router.get("/api/v1/stations", response_model=list[StationRead])
def list_stations(
    department_id: UUID = Query(...),
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    if not _roles(principal).intersection(DEPARTMENT_ROLES):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=404, detail="Department not found")
    _assert_org_access(principal, department.organization_id)
    statement = (
        select(Station)
        .where(Station.department_id == department_id)
        .order_by(Station.name.asc())
    )
    return list(db.scalars(statement).all())


@router.get("/api/v1/audit", tags=["Audit"])
def list_audit_logs(
    organization_id: UUID = Query(...),
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
    principal: dict = Depends(get_current_principal),
):
    if not _roles(principal).intersection({"APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN", "AUDITOR"}):
        raise HTTPException(status_code=403, detail="Audit access permission required")
    _assert_org_access(principal, organization_id)
    statement = (
        select(AuditLog)
        .where(AuditLog.organization_id == str(organization_id))
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    rows = db.scalars(statement).all()
    return [
        {
            "id": str(row.id),
            "organization_id": row.organization_id,
            "actor_sub": row.actor_sub,
            "action": row.action,
            "resource_type": row.resource_type,
            "resource_id": row.resource_id,
            "details": row.details,
            "created_at": row.created_at,
        }
        for row in rows
    ]
