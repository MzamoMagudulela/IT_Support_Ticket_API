import os
import shutil
from datetime import datetime, timezone
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Request, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.core.database import get_db
from app.core.config import settings
from app.core.permissions import get_current_active_user, check_ticket_access, RoleChecker
from app.models.user import User
from app.models.ticket import (
    Ticket, TicketComment, TicketAttachment, TicketAssignment,
    TicketStatusHistory, TicketLink, PriorityLevel, ImpactLevel,
    UrgencyLevel, TicketStatus, CommentType, LinkType
)
from app.models.asset import Asset
from app.models.automation import TriggerEvent
from app.schemas.ticket import (
    TicketCreate, TicketUpdate, TicketRead, TicketDetailRead,
    TicketCommentCreate, TicketCommentRead, TicketAttachmentRead,
    TicketAssignmentRead, TicketStatusHistoryRead,
    TicketAssignRequest, TicketStatusUpdateRequest, TicketLinkRequest,
    TicketMergeRequest, TicketReopenRequest, TicketEscalateRequest,
    TicketListResponse
)
from app.services.sla_service import calculate_priority, apply_sla_policy_to_ticket, handle_sla_status_change
from app.services.automation_engine import trigger_automation
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/tickets", tags=["Tickets"])

def format_ticket_read(t: Ticket) -> TicketRead:
    return TicketRead(
        id=t.id,
        reference_number=t.reference_number,
        subject=t.subject,
        description=t.description,
        category=t.category,
        priority=t.priority,
        impact=t.impact,
        urgency=t.urgency,
        status=t.status,
        escalation_level=t.escalation_level,
        reopened_count=t.reopened_count,
        requester_id=t.requester_id,
        requester_name=t.requester.full_name if t.requester else None,
        requester_email=t.requester.email if t.requester else None,
        assigned_technician_id=t.assigned_technician_id,
        technician_name=t.assigned_technician.full_name if t.assigned_technician else None,
        department_id=t.department_id,
        department_name=t.department.name if t.department else None,
        related_asset_id=t.related_asset_id,
        related_asset_tag=t.related_asset.asset_tag if t.related_asset else None,
        response_deadline=t.response_deadline,
        resolution_deadline=t.resolution_deadline,
        first_responded_at=t.first_responded_at,
        resolved_at=t.resolved_at,
        resolution_details=t.resolution_details,
        is_deleted=t.is_deleted,
        created_at=t.created_at,
        updated_at=t.updated_at
    )

@router.get("", response_model=TicketListResponse)
def get_tickets(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    department_id: Optional[int] = None,
    assigned_to_me: Optional[bool] = False,
    sort_by: str = Query("created_at"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(Ticket).filter(Ticket.is_deleted == False)

    # Resource-level authorization: Employees only see their own tickets
    user_roles = [r.name.lower() for r in current_user.roles]
    is_employee_only = "employee" in user_roles and not any(
        r in user_roles for r in ["admin", "system administrator", "system_admin", "it_manager", "it operations manager", "technician", "it support technician", "auditor"]
    )
    if is_employee_only:
        query = query.filter(Ticket.requester_id == current_user.id)
    elif assigned_to_me:
        query = query.filter(Ticket.assigned_technician_id == current_user.id)

    # Filters
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            or_(
                Ticket.subject.ilike(search_filter),
                Ticket.description.ilike(search_filter),
                Ticket.reference_number.ilike(search_filter)
            )
        )
    if status:
        query = query.filter(Ticket.status == status.upper())
    if priority:
        query = query.filter(Ticket.priority == priority.upper())
    if category:
        query = query.filter(Ticket.category.ilike(category))
    if department_id:
        query = query.filter(Ticket.department_id == department_id)

    # Sorting
    sort_col = getattr(Ticket, sort_by, Ticket.created_at)
    query = query.order_by(desc(sort_col) if sort_desc else asc(sort_col))

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1

    return TicketListResponse(
        items=[format_ticket_read(t) for t in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

@router.post("", response_model=TicketRead)
def create_ticket(
    data: TicketCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Unique reference number format TIK-YYYY-XXXXX
    count = db.query(Ticket).count() + 1
    ref_num = f"TIK-{datetime.now(timezone.utc).year}-{count:04d}"

    # Priority calculation from configurable matrix
    calculated_priority = calculate_priority(data.impact, data.urgency)

    ticket = Ticket(
        reference_number=ref_num,
        subject=data.subject,
        description=data.description,
        requester_id=current_user.id,
        department_id=data.department_id or current_user.department_id,
        related_asset_id=data.related_asset_id,
        category=data.category,
        impact=data.impact.value,
        urgency=data.urgency.value,
        priority=calculated_priority.value,
        status=TicketStatus.NEW.value
    )
    db.add(ticket)
    db.flush()

    # Apply SLA policy
    apply_sla_policy_to_ticket(db, ticket)

    # Record Initial Status History
    status_log = TicketStatusHistory(
        ticket_id=ticket.id,
        changed_by_id=current_user.id,
        old_status="NONE",
        new_status=TicketStatus.NEW.value,
        comment="Ticket submitted by requester"
    )
    db.add(status_log)
    db.commit()
    db.refresh(ticket)

    record_audit_log(
        db, action="CREATE", entity_type="TICKET", entity_id=ticket.id,
        user=current_user, request=request,
        new_values={"ref": ticket.reference_number, "priority": ticket.priority}
    )

    # Automation trigger
    trigger_automation(
        db, TriggerEvent.ON_TICKET_CREATED,
        {
            "id": ticket.id,
            "reference_number": ticket.reference_number,
            "subject": ticket.subject,
            "priority": ticket.priority,
            "category": ticket.category,
            "requester_id": ticket.requester_id
        }
    )

    return format_ticket_read(ticket)

@router.get("/{ticket_id}", response_model=TicketDetailRead)
def get_ticket_detail(
    ticket_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    check_ticket_access(ticket, current_user)

    user_roles = [r.name.lower() for r in current_user.roles]
    is_employee = "employee" in user_roles and not any(
        r in user_roles for r in ["admin", "system administrator", "it_manager", "technician", "auditor"]
    )

    # Filter comments: Employees do NOT see internal notes
    comments = []
    for c in ticket.comments:
        if is_employee and c.comment_type == CommentType.INTERNAL_NOTE.value:
            continue
        comments.append(
            TicketCommentRead(
                id=c.id,
                ticket_id=c.ticket_id,
                author_id=c.author_id,
                author_name=c.author.full_name if c.author else "Support Staff",
                comment_type=CommentType(c.comment_type),
                content=c.content,
                created_at=c.created_at
            )
        )

    attachments = [
        TicketAttachmentRead(
            id=a.id,
            ticket_id=a.ticket_id,
            file_name=a.file_name,
            file_path=a.file_path,
            file_size_bytes=a.file_size_bytes,
            content_type=a.content_type,
            uploaded_by_id=a.uploaded_by_id,
            created_at=a.created_at
        ) for a in ticket.attachments
    ]

    history = [
        TicketStatusHistoryRead(
            id=h.id,
            ticket_id=h.ticket_id,
            changed_by_id=h.changed_by_id,
            changed_by_name=h.changed_by.full_name if h.changed_by else "System",
            old_status=h.old_status,
            new_status=h.new_status,
            comment=h.comment,
            created_at=h.created_at
        ) for h in ticket.status_history
    ]

    assignments = [
        TicketAssignmentRead(
            id=a.id,
            ticket_id=a.ticket_id,
            assigned_by_id=a.assigned_by_id,
            assigned_by_name=a.assigned_by.full_name if a.assigned_by else "System",
            previous_technician_name=a.previous_technician.full_name if a.previous_technician else None,
            new_technician_name=a.new_technician.full_name if a.new_technician else "Unassigned",
            reason=a.reason,
            created_at=a.created_at
        ) for a in ticket.assignments
    ]

    base = format_ticket_read(ticket)
    return TicketDetailRead(
        **base.model_dump(),
        comments=comments,
        attachments=attachments,
        status_history=history,
        assignments=assignments
    )

@router.post("/{ticket_id}/comments", response_model=TicketCommentRead)
def add_ticket_comment(
    ticket_id: int,
    data: TicketCommentCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    check_ticket_access(ticket, current_user)

    user_roles = [r.name.lower() for r in current_user.roles]
    is_employee = "employee" in user_roles and not any(
        r in user_roles for r in ["admin", "system administrator", "it_manager", "technician"]
    )
    # Employees cannot write internal notes
    if is_employee and data.comment_type == CommentType.INTERNAL_NOTE:
        raise HTTPException(status_code=403, detail="Employees cannot create internal technician notes")

    # If first technician response
    if not ticket.first_responded_at and not is_employee:
        ticket.first_responded_at = datetime.now(timezone.utc)
        if ticket.sla_tracking and ticket.sla_tracking.response_met is None:
            ticket.sla_tracking.response_met = ticket.first_responded_at <= ticket.sla_tracking.response_deadline

    comment = TicketComment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        comment_type=data.comment_type.value,
        content=data.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    record_audit_log(
        db, action="COMMENT_ADDED", entity_type="TICKET", entity_id=ticket.id,
        user=current_user, request=request, new_values={"type": data.comment_type.value}
    )

    return TicketCommentRead(
        id=comment.id,
        ticket_id=comment.ticket_id,
        author_id=comment.author_id,
        author_name=current_user.full_name,
        comment_type=CommentType(comment.comment_type),
        content=comment.content,
        created_at=comment.created_at
    )

@router.post("/{ticket_id}/assign", response_model=TicketRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def assign_ticket(
    ticket_id: int,
    data: TicketAssignRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    technician = db.query(User).filter(User.id == data.technician_id, User.is_active == True).first()
    if not technician:
        raise HTTPException(status_code=400, detail="Invalid technician ID")

    prev_tech_id = ticket.assigned_technician_id
    ticket.assigned_technician_id = technician.id
    if ticket.status == TicketStatus.NEW.value:
        ticket.status = TicketStatus.ASSIGNED.value

    assignment = TicketAssignment(
        ticket_id=ticket.id,
        assigned_by_id=current_user.id,
        previous_technician_id=prev_tech_id,
        new_technician_id=technician.id,
        reason=data.reason
    )
    db.add(assignment)
    db.commit()
    db.refresh(ticket)

    record_audit_log(
        db, action="REASSIGN", entity_type="TICKET", entity_id=ticket.id,
        user=current_user, request=request,
        new_values={"assigned_to": technician.username, "reason": data.reason}
    )

    return format_ticket_read(ticket)

@router.post("/{ticket_id}/status", response_model=TicketRead)
def update_ticket_status(
    ticket_id: int,
    data: TicketStatusUpdateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    check_ticket_access(ticket, current_user)

    old_status = ticket.status
    new_status = data.new_status.value
    ticket.status = new_status

    now = datetime.now(timezone.utc)
    if new_status == TicketStatus.RESOLVED.value:
        ticket.resolved_at = now
        ticket.resolution_details = data.resolution_details or ticket.resolution_details or "Resolved by technician"

    handle_sla_status_change(db, ticket, old_status, new_status)

    status_log = TicketStatusHistory(
        ticket_id=ticket.id,
        changed_by_id=current_user.id,
        old_status=old_status,
        new_status=new_status,
        comment=data.comment or f"Status transitioned to {new_status}"
    )
    db.add(status_log)
    db.commit()
    db.refresh(ticket)

    record_audit_log(
        db, action="STATUS_CHANGE", entity_type="TICKET", entity_id=ticket.id,
        user=current_user, request=request,
        old_values={"status": old_status}, new_values={"status": new_status}
    )

    if new_status == TicketStatus.RESOLVED.value:
        trigger_automation(
            db, TriggerEvent.ON_TICKET_RESOLVED,
            {"id": ticket.id, "reference_number": ticket.reference_number, "requester_id": ticket.requester_id}
        )

    return format_ticket_read(ticket)

@router.post("/{ticket_id}/escalate", response_model=TicketRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def escalate_ticket(
    ticket_id: int,
    data: TicketEscalateRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    ticket.escalation_level += 1
    # Increase priority if not already critical
    if ticket.priority != PriorityLevel.CRITICAL.value:
        ticket.priority = PriorityLevel.CRITICAL.value

    comment = TicketComment(
        ticket_id=ticket.id,
        author_id=current_user.id,
        comment_type=CommentType.INTERNAL_NOTE.value,
        content=f"ESCALATION LEVEL {ticket.escalation_level}: {data.reason}"
    )
    db.add(comment)
    db.commit()
    db.refresh(ticket)

    record_audit_log(
        db, action="ESCALATE", entity_type="TICKET", entity_id=ticket.id,
        user=current_user, request=request, new_values={"escalation_level": ticket.escalation_level, "reason": data.reason}
    )
    return format_ticket_read(ticket)

@router.post("/{ticket_id}/reopen", response_model=TicketRead)
def reopen_ticket(
    ticket_id: int,
    data: TicketReopenRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    check_ticket_access(ticket, current_user)

    if ticket.status not in [TicketStatus.RESOLVED.value, TicketStatus.CLOSED.value]:
        raise HTTPException(status_code=400, detail="Only resolved or closed tickets can be reopened")

    old_status = ticket.status
    ticket.status = TicketStatus.IN_PROGRESS.value
    ticket.reopened_count += 1
    ticket.resolved_at = None

    history = TicketStatusHistory(
        ticket_id=ticket.id,
        changed_by_id=current_user.id,
        old_status=old_status,
        new_status=TicketStatus.IN_PROGRESS.value,
        comment=f"Ticket Reopened #{ticket.reopened_count}: {data.reason}"
    )
    db.add(history)
    db.commit()
    db.refresh(ticket)

    record_audit_log(
        db, action="REOPEN", entity_type="TICKET", entity_id=ticket.id,
        user=current_user, request=request, new_values={"reopened_count": ticket.reopened_count}
    )
    return format_ticket_read(ticket)

@router.post("/{ticket_id}/link", response_model=dict)
def link_tickets(
    ticket_id: int,
    data: TicketLinkRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    source = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    target = db.query(Ticket).filter(Ticket.id == data.target_ticket_id).first()
    if not source or not target:
        raise HTTPException(status_code=404, detail="One or both tickets not found")

    link = TicketLink(
        source_ticket_id=source.id,
        target_ticket_id=target.id,
        link_type=data.link_type.value
    )
    db.add(link)
    db.commit()
    return {"message": f"Linked ticket {source.reference_number} to {target.reference_number} as {data.link_type.value}"}

@router.post("/{ticket_id}/merge", response_model=dict, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def merge_tickets(
    ticket_id: int,
    data: TicketMergeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    source = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    target = db.query(Ticket).filter(Ticket.id == data.target_ticket_id).first()
    if not source or not target:
        raise HTTPException(status_code=404, detail="One or both tickets not found")

    source.status = TicketStatus.CANCELLED.value
    source.resolution_details = f"Merged into {target.reference_number}: {data.reason}"

    link = TicketLink(
        source_ticket_id=source.id,
        target_ticket_id=target.id,
        link_type=LinkType.MERGED_INTO.value
    )
    comment = TicketComment(
        ticket_id=target.id,
        author_id=current_user.id,
        comment_type=CommentType.INTERNAL_NOTE.value,
        content=f"Merged duplicate ticket {source.reference_number} ('{source.subject}') into this ticket. Reason: {data.reason}"
    )
    db.add(link)
    db.add(comment)
    db.commit()
    return {"message": f"Successfully merged {source.reference_number} into {target.reference_number}"}

@router.post("/{ticket_id}/attachments", response_model=dict)
def upload_ticket_attachment(
    ticket_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id, Ticket.is_deleted == False).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    check_ticket_access(ticket, current_user)

    # Validate file extension
    _, ext = os.path.splitext(file.filename)
    if ext.lower() not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type {ext} not permitted. Allowed: {settings.ALLOWED_EXTENSIONS}")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    safe_filename = f"ticket_{ticket_id}_{int(datetime.now(timezone.utc).timestamp())}_{file.filename}"
    file_path = os.path.join(settings.UPLOAD_DIR, safe_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(file_path)
    attachment = TicketAttachment(
        ticket_id=ticket.id,
        file_name=file.filename,
        file_path=file_path,
        file_size_bytes=file_size,
        content_type=file.content_type or "application/octet-stream",
        uploaded_by_id=current_user.id
    )
    db.add(attachment)
    db.commit()

    return {"message": "Attachment uploaded successfully", "filename": file.filename, "size": file_size}
