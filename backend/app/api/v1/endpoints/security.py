from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.security import (
    SecurityIncident, SecurityEvidence, SecurityTimeline, SecurityEvent,
    SecurityCategory, SecuritySeverity, SecurityStatus
)
from app.schemas.security import (
    SecurityIncidentCreate, SecurityIncidentUpdate, SecurityIncidentRead,
    SecurityEvidenceCreate, SecurityTimelineCreate, SecurityDashboardKPIs,
    SecurityEvidenceRead, SecurityTimelineRead
)
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/security", tags=["Cybersecurity Operations"])

def format_sec_incident(s: SecurityIncident) -> SecurityIncidentRead:
    evidence_list = [
        SecurityEvidenceRead(
            id=e.id,
            security_incident_id=e.security_incident_id,
            evidence_type=e.evidence_type,
            description=e.description,
            file_path=e.file_path,
            hash_sha256=e.hash_sha256,
            added_by_name=e.added_by.full_name if e.added_by else None,
            created_at=e.created_at
        ) for e in s.evidence_items
    ]

    timeline_list = [
        SecurityTimelineRead(
            id=t.id,
            action_type=t.action_type,
            notes=t.notes,
            author_name=t.author.full_name if t.author else None,
            created_at=t.created_at
        ) for t in s.timeline_entries
    ]

    return SecurityIncidentRead(
        id=s.id,
        incident_number=s.incident_number,
        title=s.title,
        description=s.description,
        category=SecurityCategory(s.category),
        severity=SecuritySeverity(s.severity),
        status=s.status,
        assigned_analyst_id=s.assigned_analyst_id,
        reporter_id=s.reporter_id,
        reporter_name=s.reporter.full_name if s.reporter else None,
        analyst_name=s.assigned_analyst.full_name if s.assigned_analyst else None,
        containment_actions=s.containment_actions,
        resolution_details=s.resolution_details,
        detected_at=s.detected_at,
        resolved_at=s.resolved_at,
        created_at=s.created_at,
        evidence_items=evidence_list,
        timeline_entries=timeline_list
    )

@router.get("/dashboard", response_model=SecurityDashboardKPIs, dependencies=[Depends(RoleChecker(["admin", "security_analyst", "it_manager", "auditor"]))])
def get_security_dashboard(db: Session = Depends(get_db)):
    total = db.query(SecurityIncident).count()
    critical = db.query(SecurityIncident).filter(SecurityIncident.severity == SecuritySeverity.CRITICAL.value).count()
    investigating = db.query(SecurityIncident).filter(SecurityIncident.status == SecurityStatus.INVESTIGATING.value).count()
    resolved = db.query(SecurityIncident).filter(SecurityIncident.status == SecurityStatus.RESOLVED.value).count()

    severities = db.query(SecurityIncident.severity, func.count(SecurityIncident.id)).group_by(SecurityIncident.severity).all()
    sev_dist = {sev: count for sev, count in severities}

    recent_events = db.query(SecurityEvent).order_by(desc(SecurityEvent.created_at)).limit(10).all()
    events_json = [
        {"id": e.id, "event_type": e.event_type, "ip_address": e.ip_address, "details": e.details, "risk_score": e.risk_score, "time": e.created_at.isoformat()}
        for e in recent_events
    ]

    return SecurityDashboardKPIs(
        total_security_incidents=total,
        critical_alerts=critical,
        under_investigation=investigating,
        resolved_incidents=resolved,
        severity_distribution=sev_dist,
        recent_events=events_json
    )

@router.get("/incidents", response_model=List[SecurityIncidentRead], dependencies=[Depends(RoleChecker(["admin", "security_analyst", "it_manager", "auditor"]))])
def list_security_incidents(
    status: Optional[str] = None,
    category: Optional[str] = None,
    severity: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(SecurityIncident)
    if status:
        query = query.filter(SecurityIncident.status == status.upper())
    if category:
        query = query.filter(SecurityIncident.category == category.upper())
    if severity:
        query = query.filter(SecurityIncident.severity == severity.upper())

    results = query.order_by(desc(SecurityIncident.created_at)).all()
    return [format_sec_incident(s) for s in results]

@router.get("/incidents/{incident_id}", response_model=SecurityIncidentRead, dependencies=[Depends(RoleChecker(["admin", "security_analyst", "it_manager", "auditor"]))])
def get_security_incident_detail(incident_id: int, db: Session = Depends(get_db)):
    s = db.query(SecurityIncident).filter(SecurityIncident.id == incident_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Security incident not found")
    return format_sec_incident(s)

@router.post("/incidents", response_model=SecurityIncidentRead)
def report_security_incident(
    data: SecurityIncidentCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    count = db.query(SecurityIncident).count() + 1
    num = f"SEC-{datetime.now(timezone.utc).year}-{count:04d}"

    sec = SecurityIncident(
        incident_number=num,
        title=data.title,
        description=data.description,
        category=data.category.value,
        severity=data.severity.value,
        status=SecurityStatus.NEW.value,
        reporter_id=current_user.id,
        assigned_analyst_id=data.assigned_analyst_id
    )
    db.add(sec)
    db.flush()

    # Timeline entry
    timeline = SecurityTimeline(
        security_incident_id=sec.id,
        author_id=current_user.id,
        action_type="REPORTED",
        notes=f"Reported incident: {data.title}"
    )
    db.add(timeline)
    db.commit()
    db.refresh(sec)

    record_audit_log(db, action="SECURITY_REPORT", entity_type="SECURITY_INCIDENT", entity_id=sec.id, user=current_user, request=request)
    return format_sec_incident(sec)

@router.patch("/incidents/{incident_id}", response_model=SecurityIncidentRead, dependencies=[Depends(RoleChecker(["admin", "security_analyst"]))])
def update_security_incident(
    incident_id: int,
    data: SecurityIncidentUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    s = db.query(SecurityIncident).filter(SecurityIncident.id == incident_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Security incident not found")

    old_status = s.status
    if data.title is not None:
        s.title = data.title
    if data.description is not None:
        s.description = data.description
    if data.category is not None:
        s.category = data.category.value
    if data.severity is not None:
        s.severity = data.severity.value
    if data.status is not None:
        s.status = data.status.value
        if data.status == SecurityStatus.RESOLVED:
            s.resolved_at = datetime.now(timezone.utc)
    if data.assigned_analyst_id is not None:
        s.assigned_analyst_id = data.assigned_analyst_id
    if data.containment_actions is not None:
        s.containment_actions = data.containment_actions
    if data.resolution_details is not None:
        s.resolution_details = data.resolution_details

    # Timeline record
    timeline = SecurityTimeline(
        security_incident_id=s.id,
        author_id=current_user.id,
        action_type="STATUS_UPDATE",
        notes=f"Updated status from {old_status} to {s.status}. Severity: {s.severity}"
    )
    db.add(timeline)
    db.commit()
    db.refresh(s)

    record_audit_log(db, action="SECURITY_UPDATE", entity_type="SECURITY_INCIDENT", entity_id=s.id, user=current_user, request=request)
    return format_sec_incident(s)

@router.post("/incidents/{incident_id}/evidence", response_model=SecurityEvidenceRead, dependencies=[Depends(RoleChecker(["admin", "security_analyst"]))])
def add_security_evidence(
    incident_id: int,
    data: SecurityEvidenceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    s = db.query(SecurityIncident).filter(SecurityIncident.id == incident_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Security incident not found")

    ev = SecurityEvidence(
        security_incident_id=s.id,
        evidence_type=data.evidence_type,
        description=data.description,
        hash_sha256=data.hash_sha256,
        added_by_id=current_user.id
    )
    db.add(ev)
    db.commit()
    db.refresh(ev)
    return SecurityEvidenceRead(
        id=ev.id,
        security_incident_id=ev.security_incident_id,
        evidence_type=ev.evidence_type,
        description=ev.description,
        file_path=ev.file_path,
        hash_sha256=ev.hash_sha256,
        added_by_name=current_user.full_name,
        created_at=ev.created_at
    )
