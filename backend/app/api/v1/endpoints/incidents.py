from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.incident import (
    Incident, ProblemRecord, KnownError, incident_tickets,
    IncidentSeverity, IncidentStatus
)
from app.models.ticket import Ticket
from app.schemas.incident import (
    IncidentCreate, IncidentUpdate, IncidentRead,
    ProblemRecordCreate, KnownErrorCreate
)
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/incidents", tags=["Incidents"])

def format_incident_read(inc: Incident) -> IncidentRead:
    return IncidentRead(
        id=inc.id,
        incident_number=inc.incident_number,
        title=inc.title,
        description=inc.description,
        is_major=inc.is_major,
        parent_incident_id=inc.parent_incident_id,
        affected_service=inc.affected_service,
        incident_commander_id=inc.incident_commander_id,
        commander_name=inc.incident_commander.full_name if inc.incident_commander else None,
        reporter_id=inc.reporter_id,
        reporter_name=inc.reporter.full_name if inc.reporter else None,
        severity=IncidentSeverity(inc.severity),
        status=inc.status,
        detected_at=inc.detected_at,
        resolved_at=inc.resolved_at,
        root_cause=inc.root_cause,
        resolution_summary=inc.resolution_summary,
        post_incident_report=inc.post_incident_report,
        linked_ticket_count=len(inc.linked_tickets),
        created_at=inc.created_at
    )

@router.get("", response_model=List[IncidentRead])
def get_incidents(
    is_major: Optional[bool] = None,
    status: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Incident)
    if is_major is not None:
        query = query.filter(Incident.is_major == is_major)
    if status:
        query = query.filter(Incident.status == status.upper())
    if severity:
        query = query.filter(Incident.severity == severity.upper())

    results = query.order_by(desc(Incident.created_at)).all()
    return [format_incident_read(inc) for inc in results]

@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident_by_id(
    incident_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")
    return format_incident_read(inc)

@router.post("", response_model=IncidentRead)
def create_incident(
    data: IncidentCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    count = db.query(Incident).count() + 1
    inc_num = f"INC-{datetime.now(timezone.utc).year}-{count:04d}"

    incident = Incident(
        incident_number=inc_num,
        title=data.title,
        description=data.description,
        is_major=data.is_major,
        parent_incident_id=data.parent_incident_id,
        affected_service=data.affected_service,
        severity=data.severity.value,
        status=IncidentStatus.DETECTED.value,
        incident_commander_id=data.incident_commander_id,
        reporter_id=current_user.id
    )

    if data.linked_ticket_ids:
        tickets = db.query(Ticket).filter(Ticket.id.in_(data.linked_ticket_ids)).all()
        incident.linked_tickets.extend(tickets)

    db.add(incident)
    db.commit()
    db.refresh(incident)

    record_audit_log(
        db, action="CREATE", entity_type="INCIDENT", entity_id=incident.id,
        user=current_user, request=request,
        new_values={"number": incident.incident_number, "is_major": incident.is_major}
    )

    return format_incident_read(incident)

@router.patch("/{incident_id}", response_model=IncidentRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def update_incident(
    incident_id: int,
    data: IncidentUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_status = inc.status
    if data.title is not None:
        inc.title = data.title
    if data.description is not None:
        inc.description = data.description
    if data.severity is not None:
        inc.severity = data.severity.value
    if data.status is not None:
        inc.status = data.status.value
        if data.status == IncidentStatus.RESOLVED:
            inc.resolved_at = datetime.now(timezone.utc)
    if data.affected_service is not None:
        inc.affected_service = data.affected_service
    if data.incident_commander_id is not None:
        inc.incident_commander_id = data.incident_commander_id
    if data.root_cause is not None:
        inc.root_cause = data.root_cause
    if data.resolution_summary is not None:
        inc.resolution_summary = data.resolution_summary
    if data.post_incident_report is not None:
        inc.post_incident_report = data.post_incident_report

    db.commit()
    db.refresh(inc)

    record_audit_log(
        db, action="UPDATE", entity_type="INCIDENT", entity_id=inc.id,
        user=current_user, request=request,
        old_values={"status": old_status}, new_values={"status": inc.status}
    )

    return format_incident_read(inc)

@router.post("/{incident_id}/link-tickets", response_model=dict, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def link_tickets_to_incident(
    incident_id: int,
    ticket_ids: List[int],
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    inc = db.query(Incident).filter(Incident.id == incident_id).first()
    if not inc:
        raise HTTPException(status_code=404, detail="Incident not found")

    tickets = db.query(Ticket).filter(Ticket.id.in_(ticket_ids)).all()
    for t in tickets:
        if t not in inc.linked_tickets:
            inc.linked_tickets.append(t)
    db.commit()
    return {"message": f"Successfully linked {len(tickets)} tickets to incident {inc.incident_number}"}

# Problem Records & Known Errors
@router.get("/problems/list")
def list_problems(db: Session = Depends(get_db)):
    return db.query(ProblemRecord).all()

@router.post("/problems/create", dependencies=[Depends(RoleChecker(["admin", "it_manager", "technician"]))])
def create_problem_record(data: ProblemRecordCreate, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    count = db.query(ProblemRecord).count() + 1
    num = f"PRB-{datetime.now(timezone.utc).year}-{count:04d}"
    prb = ProblemRecord(
        problem_number=num,
        title=data.title,
        description=data.description,
        root_cause=data.root_cause,
        workaround=data.workaround,
        permanent_fix=data.permanent_fix,
        owner_id=current_user.id
    )
    db.add(prb)
    db.commit()
    db.refresh(prb)
    return prb

@router.get("/known-errors/list")
def list_known_errors(db: Session = Depends(get_db)):
    return db.query(KnownError).filter(KnownError.is_active == True).all()

@router.post("/known-errors/create", dependencies=[Depends(RoleChecker(["admin", "it_manager", "technician"]))])
def create_known_error(data: KnownErrorCreate, db: Session = Depends(get_db)):
    ke = KnownError(
        error_code=data.error_code,
        title=data.title,
        description=data.description,
        symptoms=data.symptoms,
        workaround=data.workaround,
        permanent_solution=data.permanent_solution
    )
    db.add(ke)
    db.commit()
    db.refresh(ke)
    return ke
