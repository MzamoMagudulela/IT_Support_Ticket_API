from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.security import SecurityCategory, SecuritySeverity, SecurityStatus

class SecurityIncidentBase(BaseModel):
    title: str
    description: str
    category: SecurityCategory = SecurityCategory.PHISHING
    severity: SecuritySeverity = SecuritySeverity.MEDIUM
    assigned_analyst_id: Optional[int] = None

class SecurityIncidentCreate(SecurityIncidentBase):
    pass

class SecurityIncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[SecurityCategory] = None
    severity: Optional[SecuritySeverity] = None
    status: Optional[SecurityStatus] = None
    assigned_analyst_id: Optional[int] = None
    containment_actions: Optional[str] = None
    resolution_details: Optional[str] = None

class SecurityTimelineCreate(BaseModel):
    action_type: str
    notes: str

class SecurityEvidenceCreate(BaseModel):
    evidence_type: str
    description: str
    hash_sha256: Optional[str] = None

class SecurityEvidenceRead(BaseModel):
    id: int
    security_incident_id: int
    evidence_type: str
    description: str
    file_path: Optional[str] = None
    hash_sha256: Optional[str] = None
    added_by_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SecurityTimelineRead(BaseModel):
    id: int
    action_type: str
    notes: str
    author_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class SecurityIncidentRead(SecurityIncidentBase):
    id: int
    incident_number: str
    status: str
    reporter_id: int
    reporter_name: Optional[str] = None
    analyst_name: Optional[str] = None
    containment_actions: Optional[str] = None
    resolution_details: Optional[str] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    created_at: datetime
    evidence_items: List[SecurityEvidenceRead] = []
    timeline_entries: List[SecurityTimelineRead] = []

    class Config:
        from_attributes = True

class SecurityDashboardKPIs(BaseModel):
    total_security_incidents: int
    critical_alerts: int
    under_investigation: int
    resolved_incidents: int
    severity_distribution: dict
    recent_events: List[dict] = []
