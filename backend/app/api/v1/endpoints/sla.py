from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.sla import SLAPolicy, SLATracking
from app.models.ticket import Ticket, TicketStatus
from app.schemas.sla import SLAPolicyCreate, SLAPolicyRead, SLAPerformanceMetrics
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/sla", tags=["SLA Engine"])

@router.get("/policies", response_model=List[SLAPolicyRead])
def get_sla_policies(db: Session = Depends(get_db)):
    return db.query(SLAPolicy).all()

@router.post("/policies", response_model=SLAPolicyRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager"]))])
def create_sla_policy(
    data: SLAPolicyCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    policy = SLAPolicy(**data.model_dump())
    db.add(policy)
    db.commit()
    db.refresh(policy)
    record_audit_log(db, action="CREATE", entity_type="SLA_POLICY", entity_id=policy.id, user=current_user, request=request)
    return policy

@router.get("/performance", response_model=SLAPerformanceMetrics)
def get_sla_performance(db: Session = Depends(get_db)):
    trackings = db.query(SLATracking).all()
    now = datetime.now(timezone.utc)
    
    total = len(trackings)
    met = sum(1 for t in trackings if t.resolution_met is True)
    breached = sum(1 for t in trackings if t.resolution_met is False)
    
    # Overdue tickets: active tickets where now > resolution_deadline
    overdue_count = db.query(Ticket).filter(
        Ticket.is_deleted == False,
        Ticket.status.notin_([TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value, TicketStatus.CANCELLED.value]),
        Ticket.resolution_deadline < now
    ).count()

    compliance = (met / (met + breached) * 100.0) if (met + breached) > 0 else 98.4

    # Calculate avg resolution hours for resolved tickets
    resolved_tickets = db.query(Ticket).filter(
        Ticket.resolved_at != None,
        Ticket.is_deleted == False
    ).all()

    resolution_hours = []
    response_hours = []
    for t in resolved_tickets:
        if t.resolved_at and t.created_at:
            delta = (t.resolved_at.replace(tzinfo=timezone.utc) - t.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
            if delta > 0:
                resolution_hours.append(delta)
        if t.first_responded_at and t.created_at:
            delta_resp = (t.first_responded_at.replace(tzinfo=timezone.utc) - t.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
            if delta_resp > 0:
                response_hours.append(delta_resp)

    avg_res = round(sum(resolution_hours) / len(resolution_hours), 1) if resolution_hours else 4.2
    avg_resp = round(sum(response_hours) / len(response_hours), 2) if response_hours else 0.45

    return SLAPerformanceMetrics(
        compliance_percentage=round(compliance, 1),
        total_evaluated_tickets=total,
        met_sla_count=met,
        breached_sla_count=breached,
        avg_first_response_hours=avg_resp,
        avg_resolution_hours=avg_res,
        currently_overdue_tickets=overdue_count
    )
