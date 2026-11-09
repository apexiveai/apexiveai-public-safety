import uuid
from datetime import date, datetime, timezone
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

def utcnow(): return datetime.now(timezone.utc)

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Department(Base):
    __tablename__ = "departments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    code: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(200))
    department_type: Mapped[str] = mapped_column(String(30))
    status: Mapped[str] = mapped_column(String(20), default="ACTIVE")

class Station(Base):
    __tablename__ = "stations"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id", ondelete="RESTRICT"), index=True)
    code: Mapped[str] = mapped_column(String(40))
    name: Mapped[str] = mapped_column(String(200))
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

class CaseRecord(Base):
    __tablename__ = "case_records"
    __table_args__ = (Index("ix_case_org_status", "organization_id", "status"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    station_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("stations.id", ondelete="RESTRICT"), index=True)
    case_number: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(250))
    summary: Mapped[str] = mapped_column(Text)
    classification: Mapped[str] = mapped_column(String(30), default="RESTRICTED")
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    created_by: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class TrafficCitation(Base):
    __tablename__ = "traffic_citations"
    __table_args__ = (Index("ix_citation_org_status", "organization_id", "status"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    citation_number: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    vehicle_registration: Mapped[str] = mapped_column(String(40), index=True)
    violation_code: Mapped[str] = mapped_column(String(40))
    location_text: Mapped[str] = mapped_column(String(250))
    fine_amount_minor: Mapped[int] = mapped_column(default=0)
    currency: Mapped[str] = mapped_column(String(3), default="MMK")
    status: Mapped[str] = mapped_column(String(30), default="DRAFT")
    created_by: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[str] = mapped_column(String(80), index=True)
    actor_sub: Mapped[str] = mapped_column(String(160), index=True)
    action: Mapped[str] = mapped_column(String(100))
    resource_type: Mapped[str] = mapped_column(String(80))
    resource_id: Mapped[str] = mapped_column(String(120))
    details: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)

class PersonRecord(Base):
    __tablename__ = "person_records"
    __table_args__ = (Index("ix_person_org_name", "organization_id", "full_name"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("organizations.id", ondelete="RESTRICT"), index=True)
    record_number: Mapped[str] = mapped_column(String(80), index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class CasePersonLink(Base):
    __tablename__ = "case_person_links"
    __table_args__ = (Index("ix_case_person_case", "case_id"),)
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case_records.id", ondelete="RESTRICT"), index=True)
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("person_records.id", ondelete="RESTRICT"), index=True)
    relationship_type: Mapped[str] = mapped_column(String(30))
    created_by: Mapped[str] = mapped_column(String(120))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class CaseAssignment(Base):
    __tablename__ = "case_assignments"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case_records.id", ondelete="RESTRICT"), index=True)
    assignee_sub: Mapped[str] = mapped_column(String(160), index=True)
    assigned_by: Mapped[str] = mapped_column(String(160))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class InvestigationEntry(Base):
    __tablename__ = "investigation_entries"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case_records.id", ondelete="RESTRICT"), index=True)
    author_sub: Mapped[str] = mapped_column(String(160))
    entry_type: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class EvidenceItem(Base):
    __tablename__ = "evidence_items"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case_records.id", ondelete="RESTRICT"), index=True)
    evidence_number: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str] = mapped_column(String(1000))
    evidence_type: Mapped[str] = mapped_column(String(40))
    storage_reference: Mapped[str | None] = mapped_column(String(500), nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class EvidenceCustody(Base):
    __tablename__ = "evidence_custody"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_items.id", ondelete="RESTRICT"), index=True)
    action: Mapped[str] = mapped_column(String(20))
    from_custodian: Mapped[str | None] = mapped_column(String(160), nullable=True)
    to_custodian: Mapped[str] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    recorded_by: Mapped[str] = mapped_column(String(160))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class CaseApproval(Base):
    __tablename__ = "case_approvals"
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("case_records.id", ondelete="RESTRICT"), index=True)
    decision: Mapped[str] = mapped_column(String(20))
    reviewer_sub: Mapped[str] = mapped_column(String(160))
    notes: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
