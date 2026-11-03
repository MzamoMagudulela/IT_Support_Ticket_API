from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.incident import IncidentSeverity, IncidentStatus

class IncidentBase(BaseModel):
    title: str
    description: str
    is_major: bool = False
    parent_incident_id: Optional[int] = None
    affected_service: str
    severity: IncidentSeverity = IncidentSeverity.SEV3_MEDIUM
    incident_commander_id: Optional[int] = None

class IncidentCreate(IncidentBase):
    linked_ticket_ids: List[int] = []

class IncidentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    affected_service: Optional[str] = None
    incident_commander_id: Optional[int] = None
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None
    post_incident_report: Optional[str] = None

class IncidentRead(IncidentBase):
    id: int
    incident_number: str
    status: str
    reporter_id: int
    reporter_name: Optional[str] = None
    commander_name: Optional[str] = None
    detected_at: datetime
    resolved_at: Optional[datetime] = None
    root_cause: Optional[str] = None
    resolution_summary: Optional[str] = None
    post_incident_report: Optional[str] = None
    linked_ticket_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class ProblemRecordCreate(BaseModel):
    title: str
    description: str
    root_cause: Optional[str] = None
    workaround: Optional[str] = None
    permanent_fix: Optional[str] = None

class KnownErrorCreate(BaseModel):
    error_code: str
    title: str
    description: str
    symptoms: str
    workaround: str
    permanent_solution: Optional[str] = None
