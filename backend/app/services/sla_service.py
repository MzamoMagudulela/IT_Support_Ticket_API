from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.ticket import Ticket, PriorityLevel, ImpactLevel, UrgencyLevel, TicketStatus
from app.models.sla import SLAPolicy, SLATracking

def make_aware(dt: datetime) -> datetime:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt

# Impact & Urgency Priority Calculation Matrix
PRIORITY_MATRIX = {
    (ImpactLevel.CRITICAL, UrgencyLevel.CRITICAL): PriorityLevel.CRITICAL,
    (ImpactLevel.CRITICAL, UrgencyLevel.HIGH): PriorityLevel.CRITICAL,
    (ImpactLevel.CRITICAL, UrgencyLevel.MEDIUM): PriorityLevel.HIGH,
    (ImpactLevel.CRITICAL, UrgencyLevel.LOW): PriorityLevel.MEDIUM,
    
    (ImpactLevel.HIGH, UrgencyLevel.CRITICAL): PriorityLevel.CRITICAL,
    (ImpactLevel.HIGH, UrgencyLevel.HIGH): PriorityLevel.HIGH,
    (ImpactLevel.HIGH, UrgencyLevel.MEDIUM): PriorityLevel.HIGH,
    (ImpactLevel.HIGH, UrgencyLevel.LOW): PriorityLevel.MEDIUM,
    
    (ImpactLevel.MEDIUM, UrgencyLevel.CRITICAL): PriorityLevel.HIGH,
    (ImpactLevel.MEDIUM, UrgencyLevel.HIGH): PriorityLevel.MEDIUM,
    (ImpactLevel.MEDIUM, UrgencyLevel.MEDIUM): PriorityLevel.MEDIUM,
    (ImpactLevel.MEDIUM, UrgencyLevel.LOW): PriorityLevel.LOW,
    
    (ImpactLevel.LOW, UrgencyLevel.CRITICAL): PriorityLevel.MEDIUM,
    (ImpactLevel.LOW, UrgencyLevel.HIGH): PriorityLevel.MEDIUM,
    (ImpactLevel.LOW, UrgencyLevel.MEDIUM): PriorityLevel.LOW,
    (ImpactLevel.LOW, UrgencyLevel.LOW): PriorityLevel.LOW,
}

def calculate_priority(impact: str, urgency: str) -> PriorityLevel:
    try:
        imp = ImpactLevel(impact)
        urg = UrgencyLevel(urgency)
        return PRIORITY_MATRIX.get((imp, urg), PriorityLevel.MEDIUM)
    except Exception:
        return PriorityLevel.MEDIUM

def apply_sla_policy_to_ticket(db: Session, ticket: Ticket) -> SLATracking:
    policy = db.query(SLAPolicy).filter(
        SLAPolicy.priority == ticket.priority,
        SLAPolicy.is_active == True
    ).first()

    now = datetime.now(timezone.utc)
    
    if not policy:
        minutes_map = {
            PriorityLevel.CRITICAL.value: (15, 120),
            PriorityLevel.HIGH.value: (60, 480),
            PriorityLevel.MEDIUM.value: (240, 1440),
            PriorityLevel.LOW.value: (480, 4320)
        }
        resp_mins, resol_mins = minutes_map.get(ticket.priority, (240, 1440))
        policy = SLAPolicy(
            name=f"Standard {ticket.priority} SLA",
            description=f"Default SLA policy for {ticket.priority} priority tickets",
            priority=ticket.priority,
            target_response_mins=resp_mins,
            target_resolution_mins=resol_mins,
            business_hours_only=False,
            is_active=True
        )
        db.add(policy)
        db.flush()

    response_deadline = now + timedelta(minutes=policy.target_response_mins)
    resolution_deadline = now + timedelta(minutes=policy.target_resolution_mins)

    ticket.response_deadline = response_deadline
    ticket.resolution_deadline = resolution_deadline

    tracking = SLATracking(
        ticket_id=ticket.id,
        sla_policy_id=policy.id,
        response_deadline=response_deadline,
        resolution_deadline=resolution_deadline,
        response_met=None,
        resolution_met=None,
        paused_duration_minutes=0
    )
    db.add(tracking)
    return tracking

def handle_sla_status_change(db: Session, ticket: Ticket, old_status: str, new_status: str):
    tracking = ticket.sla_tracking
    if not tracking:
        return

    now = datetime.now(timezone.utc)

    # Pause SLA when ticket enters PENDING_USER
    if new_status == TicketStatus.PENDING_USER.value and old_status != TicketStatus.PENDING_USER.value:
        tracking.last_paused_at = now
    
    # Resume SLA when ticket leaves PENDING_USER
    elif old_status == TicketStatus.PENDING_USER.value and new_status != TicketStatus.PENDING_USER.value:
        if tracking.last_paused_at:
            paused_minutes = int((now - make_aware(tracking.last_paused_at)).total_seconds() / 60)
            if paused_minutes > 0:
                tracking.paused_duration_minutes += paused_minutes
                tracking.resolution_deadline += timedelta(minutes=paused_minutes)
                ticket.resolution_deadline = tracking.resolution_deadline
            tracking.last_paused_at = None

    # First response check
    if ticket.first_responded_at and tracking.response_met is None:
        tracking.response_met = make_aware(ticket.first_responded_at) <= make_aware(tracking.response_deadline)

    # Ticket resolved check
    if new_status in [TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]:
        if tracking.resolution_met is None:
            resolved_time = make_aware(ticket.resolved_at or now)
            tracking.resolution_met = resolved_time <= make_aware(tracking.resolution_deadline)
