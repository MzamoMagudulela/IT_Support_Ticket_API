from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
import enum
from app.models.base import TimeStampedModel

class SecurityCategory(str, enum.Enum):
    PHISHING = "PHISHING"
    MALWARE = "MALWARE"
    SUSPICIOUS_LOGIN = "SUSPICIOUS_LOGIN"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    DATA_EXPOSURE = "DATA_EXPOSURE"
    COMPROMISED_ACCOUNT = "COMPROMISED_ACCOUNT"
    NETWORK_INTRUSION = "NETWORK_INTRUSION"

class SecuritySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityStatus(str, enum.Enum):
    NEW = "NEW"
    INVESTIGATING = "INVESTIGATING"
    CONTAINED = "CONTAINED"
    RESOLVED = "RESOLVED"
    FALSE_POSITIVE = "FALSE_POSITIVE"

class SecurityIncident(TimeStampedModel):
    __tablename__ = "security_incidents"

    incident_number = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    category = Column(String(40), default=SecurityCategory.PHISHING.value, nullable=False, index=True)
    severity = Column(String(20), default=SecuritySeverity.MEDIUM.value, nullable=False, index=True)
    status = Column(String(30), default=SecurityStatus.NEW.value, nullable=False, index=True)
    
    reporter_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    assigned_analyst_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    containment_actions = Column(Text, nullable=True)
    resolution_details = Column(Text, nullable=True)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    resolved_at = Column(DateTime, nullable=True)

    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="security_incidents_reported")
    assigned_analyst = relationship("User", foreign_keys=[assigned_analyst_id], back_populates="security_incidents_assigned")
    evidence_items = relationship("SecurityEvidence", back_populates="security_incident", cascade="all, delete-orphan")
    timeline_entries = relationship("SecurityTimeline", back_populates="security_incident", cascade="all, delete-orphan", order_by="SecurityTimeline.created_at.asc()")

class SecurityEvidence(TimeStampedModel):
    __tablename__ = "security_evidence"

    security_incident_id = Column(Integer, ForeignKey("security_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    evidence_type = Column(String(50), nullable=False) # Log file, Screenshot, Email Header, Network PCAP
    description = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    hash_sha256 = Column(String(64), nullable=True)
    added_by_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    security_incident = relationship("SecurityIncident", back_populates="evidence_items")
    added_by = relationship("User")

class SecurityTimeline(TimeStampedModel):
    __tablename__ = "security_timelines"

    security_incident_id = Column(Integer, ForeignKey("security_incidents.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    action_type = Column(String(50), nullable=False) # TRIAGE, CONTAINMENT, ANALYSIS, RESOLUTION
    notes = Column(Text, nullable=False)

    security_incident = relationship("SecurityIncident", back_populates="timeline_entries")
    author = relationship("User")

class SecurityEvent(TimeStampedModel):
    """Application-level security event / threat alert log"""
    __tablename__ = "security_events"

    event_type = Column(String(80), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    details = Column(Text, nullable=False)
    risk_score = Column(Float, default=1.0, nullable=False) # 1.0 to 10.0

    user = relationship("User")
