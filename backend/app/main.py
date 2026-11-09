from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.core.config import settings
from app.core.database import Base, engine, get_db
from app.core.security import get_current_principal, require_roles
from app.models import Organization, Department, Station, CaseRecord, TrafficCitation, AuditLog
from app.schemas import OrganizationCreate, OrganizationRead, CaseCreate, CaseRead, CitationCreate, CitationRead
from app.routers.organization_structure import router as organization_structure_router
from app.routers.rms import router as rms_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Development convenience only. Production must use versioned Alembic migrations.
    if settings.app_env == "development":
        Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.app_name, version="0.2.0", lifespan=lifespan, docs_url="/docs" if settings.app_env != "production" else None)
app.include_router(organization_structure_router)
app.include_router(rms_router)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["GET", "POST", "PATCH"], allow_headers=["Authorization", "Content-Type", "X-Request-ID"])

@app.get("/health/live", tags=["Health"])
def live(): return {"status": "alive", "product": "APEXIVEAI PUBLIC SAFETY"}

@app.get("/health/ready", tags=["Health"])
def ready(db: Session = Depends(get_db)):
    db.execute(select(1))
    return {"status": "ready", "database": "connected"}

@app.get(settings.api_v1_prefix + "/me", tags=["Identity"])
def me(principal: dict = Depends(get_current_principal)):
    return {"subject": principal.get("sub"), "username": principal.get("preferred_username"), "roles": principal.get("roles", [])}

@app.post(settings.api_v1_prefix + "/organizations", response_model=OrganizationRead, tags=["Administration"])
def create_organization(payload: OrganizationCreate, db: Session = Depends(get_db), principal: dict = Depends(require_roles("APS_ADMIN", "GOV_ADMIN"))):
    exists = db.scalar(select(Organization).where(Organization.code == payload.code))
    if exists: raise HTTPException(409, "Organization code already exists")
    row = Organization(code=payload.code, name=payload.name)
    db.add(row); db.flush()
    db.add(AuditLog(organization_id=str(row.id), actor_sub=str(principal["sub"]), action="ORGANIZATION_CREATED", resource_type="organization", resource_id=str(row.id), details={"code": row.code}))
    db.commit(); db.refresh(row)
    return row

@app.get(settings.api_v1_prefix + "/organizations", response_model=list[OrganizationRead], tags=["Administration"])
def list_organizations(db: Session = Depends(get_db), principal: dict = Depends(require_roles("APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN", "AUDITOR"))):
    return list(db.scalars(select(Organization).order_by(Organization.name)).all())

def assert_org_access(principal: dict, organization_id) -> None:
    # Only the platform-level administrator may cross organization boundaries.
    if "APS_ADMIN" in principal.get("roles", []):
        return
    if str(principal.get("org_id", "")) != str(organization_id):
        raise HTTPException(403, "Organization scope denied")

@app.post(settings.api_v1_prefix + "/cases", response_model=CaseRead, tags=["Police RMS"])
def create_case(payload: CaseCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    if not set(principal.get("roles", [])).intersection({"APS_ADMIN", "GOV_ADMIN", "POLICE_OFFICER", "CASE_INVESTIGATOR"}):
        raise HTTPException(403, "Insufficient permissions")
    assert_org_access(principal, payload.organization_id)
    station = db.get(Station, payload.station_id)
    if station is None:
        raise HTTPException(422, "Station does not exist")
    department = db.get(Department, station.department_id)
    if department is None or department.organization_id != payload.organization_id:
        raise HTTPException(422, "Station is not part of the specified organization")
    row = CaseRecord(**payload.model_dump(), created_by=str(principal["sub"]))
    db.add(row); db.flush()
    db.add(AuditLog(organization_id=str(row.organization_id), actor_sub=str(principal["sub"]), action="CASE_CREATED", resource_type="case", resource_id=str(row.id), details={"case_number": row.case_number}))
    db.commit(); db.refresh(row)
    return row

@app.get(settings.api_v1_prefix + "/cases", response_model=list[CaseRead], tags=["Police RMS"])
def list_cases(organization_id: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    if not set(principal.get("roles", [])).intersection(
        {"APS_ADMIN", "GOV_ADMIN", "DEPT_ADMIN", "POLICE_OFFICER", "CASE_INVESTIGATOR"}
    ):
        raise HTTPException(403, "Insufficient permissions")
    assert_org_access(principal, organization_id)
    return list(db.scalars(select(CaseRecord).where(CaseRecord.organization_id == organization_id).order_by(CaseRecord.created_at.desc()).limit(200)).all())

@app.post(settings.api_v1_prefix + "/traffic/citations", response_model=CitationRead, tags=["Traffic Management"])
def create_citation(payload: CitationCreate, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    if not set(principal.get("roles", [])).intersection({"APS_ADMIN", "GOV_ADMIN", "TRAFFIC_OFFICER", "TRAFFIC_COMMANDER"}):
        raise HTTPException(403, "Insufficient permissions")
    assert_org_access(principal, payload.organization_id)
    row = TrafficCitation(**payload.model_dump(), created_by=str(principal["sub"]))
    db.add(row); db.flush()
    db.add(AuditLog(organization_id=str(row.organization_id), actor_sub=str(principal["sub"]), action="TRAFFIC_CITATION_CREATED", resource_type="traffic_citation", resource_id=str(row.id), details={"citation_number": row.citation_number}))
    db.commit(); db.refresh(row)
    return row

@app.get(settings.api_v1_prefix + "/traffic/citations", response_model=list[CitationRead], tags=["Traffic Management"])
def list_citations(organization_id: str, db: Session = Depends(get_db), principal: dict = Depends(get_current_principal)):
    assert_org_access(principal, organization_id)
    return list(db.scalars(select(TrafficCitation).where(TrafficCitation.organization_id == organization_id).order_by(TrafficCitation.created_at.desc()).limit(200)).all())
