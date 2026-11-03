from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
import enum
from app.models.base import TimeStampedModel

class IncidentSeverity(str, enum.Enum):
    SEV1_CRITICAL = "SEV1_CRITICAL"
    SEV2_HIGH = "SEV2_HIGH"
    SEV3_MEDIUM = "SEV3_MEDIUM"
    SEV4_LOW = "SEV4_LOW"

class IncidentStatus(str, enum.Enum):
    DETECTED = "DETECTED"
    INVESTIGATING = "INVESTIGATING"
    IDENTIFIED = "IDENTIFIED"
    MONITORING = "MONITORING"
    RESOLVED = "RESOLVED"

# Association table between incidents and support tickets
incident_tickets = Table(
    'incident_ticket_links',
    TimeStampedModel.metadata,
    Column('incident_id', Integer, ForeignKey('incidents.id', ondelete='CASCADE'), primary_key=True),
    Column('ticket_id', Integer, ForeignKey('tickets.id', ondelete='CASCADE'), primary_key=True)
)

class Incident(TimeStampedModel):
    __tablename__ = "incidents"

    incident_number = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    is_major = Column(Boolean, default=False, nullable=False, index=True)
    parent_incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)
    
    affected_service = Column(String(100), nullable=False, index=True)
    incident_commander_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=True)
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    
    severity = Column(String(20), default=IncidentSeverity.SEV3_MEDIUM.value, nullable=False, index=True)
    status = Column(String(20), default=IncidentStatus.DETECTED.value, nullable=False, index=True)
    
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime, nullable=True)
    
    root_cause = Column(Text, nullable=True)
    resolution_summary = Column(Text, nullable=True)
    post_incident_report = Column(Text, nullable=True)

    # Relationships
    parent_incident = relationship("Incident", remote_side="Incident.id", backref="child_incidents")
    incident_commander = relationship("User", foreign_keys=[incident_commander_id])
    reporter = relationship("User", foreign_keys=[reporter_id])
    linked_tickets = relationship("Ticket", secondary=incident_tickets, backref="linked_incidents")

class ProblemRecord(TimeStampedModel):
    __tablename__ = "problem_records"

    problem_number = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    workaround = Column(Text, nullable=True)
    permanent_fix = Column(Text, nullable=True)
    status = Column(String(30), default="OPEN", nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    owner = relationship("User")

class KnownError(TimeStampedModel):
    __tablename__ = "known_errors"

    error_code = Column(String(50), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    symptoms = Column(Text, nullable=False)
    workaround = Column(Text, nullable=False)
    permanent_solution = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
