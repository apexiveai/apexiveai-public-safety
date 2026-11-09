from datetime import date, datetime
from pydantic import BaseModel, Field, ConfigDict, field_validator
from uuid import UUID

class OrganizationCreate(BaseModel):
    code: str = Field(min_length=2, max_length=40, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=2, max_length=200)

class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    code: str
    name: str
    status: str

class CaseCreate(BaseModel):
    organization_id: UUID
    station_id: UUID
    case_number: str = Field(min_length=3, max_length=80)
    title: str = Field(min_length=3, max_length=250)
    summary: str = Field(min_length=1, max_length=10000)
    classification: str = Field(default="RESTRICTED", pattern="^(INTERNAL|CONFIDENTIAL|RESTRICTED)$")

class CaseRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    station_id: UUID
    case_number: str
    title: str
    classification: str
    status: str
    created_by: str

class CitationCreate(BaseModel):
    organization_id: UUID
    citation_number: str = Field(min_length=3, max_length=80)
    vehicle_registration: str = Field(min_length=2, max_length=40)
    violation_code: str = Field(min_length=2, max_length=40)
    location_text: str = Field(min_length=2, max_length=250)
    fine_amount_minor: int = Field(default=0, ge=0)

class CitationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    citation_number: str
    vehicle_registration: str
    violation_code: str
    location_text: str
    fine_amount_minor: int
    currency: str
    status: str

class DepartmentCreate(BaseModel):
    organization_id: UUID
    code: str = Field(min_length=2, max_length=40, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=2, max_length=200)
    department_type: str = Field(min_length=2, max_length=30, pattern=r"^[A-Z_]+$")

class DepartmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    code: str
    name: str
    department_type: str
    status: str

class StationCreate(BaseModel):
    department_id: UUID
    code: str = Field(min_length=2, max_length=40, pattern=r"^[A-Z0-9_-]+$")
    name: str = Field(min_length=2, max_length=200)
    address: str | None = Field(default=None, max_length=2000)

class StationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    department_id: UUID
    code: str
    name: str
    address: str | None

class PersonCreate(BaseModel):
    organization_id: UUID
    record_number: str = Field(min_length=3, max_length=80, pattern=r"^[A-Z0-9_-]+$")
    full_name: str = Field(min_length=2, max_length=200)
    date_of_birth: date | None = None
    notes: str | None = Field(default=None, max_length=5000)

class PersonRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    record_number: str
    full_name: str
    date_of_birth: date | None
    notes: str | None
    created_by: str
    created_at: datetime

class PersonCaseLinkCreate(BaseModel):
    relationship_type: str = Field(pattern=r"^(SUBJECT|WITNESS|VICTIM|REPORTING_PARTY)$")

class PersonCaseLinkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    person_id: UUID
    relationship_type: str
    created_by: str
    created_at: datetime

class CaseAssignmentCreate(BaseModel):
    assignee_sub: str = Field(min_length=1, max_length=160)

class CaseAssignmentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    assignee_sub: str
    assigned_by: str
    active: bool
    created_at: datetime

class InvestigationEntryCreate(BaseModel):
    entry_type: str = Field(pattern=r"^(NOTE|INTERVIEW|ACTION|FINDING)$")
    content: str = Field(min_length=1, max_length=5000)

class InvestigationEntryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    author_sub: str
    entry_type: str
    content: str
    created_at: datetime

class EvidenceCreate(BaseModel):
    evidence_number: str = Field(min_length=3, max_length=80, pattern=r"^[A-Z0-9_-]+$")
    description: str = Field(min_length=2, max_length=1000)
    evidence_type: str = Field(min_length=2, max_length=40, pattern=r"^[A-Z_]+$")
    storage_reference: str | None = Field(default=None, max_length=500)

    @field_validator("storage_reference")
    @classmethod
    def internal_storage_reference_only(cls, value: str | None) -> str | None:
        if value and "://" in value:
            raise ValueError("Use an internal object-storage key, not a URL")
        return value

class EvidenceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    evidence_number: str
    description: str
    evidence_type: str
    storage_reference: str | None
    recorded_by: str
    created_at: datetime

class EvidenceCustodyCreate(BaseModel):
    action: str = Field(pattern=r"^(RECEIVE|TRANSFER|RETURN)$")
    from_custodian: str | None = Field(default=None, max_length=160)
    to_custodian: str = Field(min_length=1, max_length=160)
    notes: str | None = Field(default=None, max_length=1000)

class EvidenceCustodyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    evidence_id: UUID
    action: str
    from_custodian: str | None
    to_custodian: str
    notes: str | None
    recorded_by: str
    created_at: datetime

class CaseApprovalCreate(BaseModel):
    decision: str = Field(pattern=r"^(APPROVE|REJECT)$")
    notes: str | None = Field(default=None, max_length=1000)

class CaseApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    case_id: UUID
    decision: str
    reviewer_sub: str
    notes: str | None
    created_at: datetime
