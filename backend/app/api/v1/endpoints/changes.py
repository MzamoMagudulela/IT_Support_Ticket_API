from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.change import (
    ChangeRequest, ChangeApproval, ChangeHistory,
    ChangeType, ChangeRisk, ChangeStatus
)
from app.schemas.change import (
    ChangeRequestCreate, ChangeRequestUpdate, ChangeRequestRead, ChangeApprovalRequest
)
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/changes", tags=["Change Management"])

def format_change_read(c: ChangeRequest) -> ChangeRequestRead:
    return ChangeRequestRead(
        id=c.id,
        change_number=c.change_number,
        title=c.title,
        description=c.description,
        change_type=ChangeType(c.change_type),
        business_justification=c.business_justification,
        affected_systems=c.affected_systems,
        risk_level=ChangeRisk(c.risk_level),
        risk_assessment=c.risk_assessment,
        implementation_plan=c.implementation_plan,
        test_procedure=c.test_procedure,
        rollback_plan=c.rollback_plan,
        scheduled_start=c.scheduled_start,
        scheduled_end=c.scheduled_end,
        status=c.status,
        requester_id=c.requester_id,
        requester_name=c.requester.full_name if c.requester else None,
        approved_by_name=c.approved_by.full_name if c.approved_by else None,
        approval_decision_at=c.approval_decision_at,
        approval_notes=c.approval_notes,
        implementation_outcome=c.implementation_outcome,
        created_at=c.created_at,
        updated_at=c.updated_at
    )

@router.get("", response_model=List[ChangeRequestRead])
def get_change_requests(
    status: Optional[str] = None,
    change_type: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    query = db.query(ChangeRequest)
    if status:
        query = query.filter(ChangeRequest.status == status.upper())
    if change_type:
        query = query.filter(ChangeRequest.change_type == change_type.upper())
    changes = query.order_by(desc(ChangeRequest.created_at)).all()
    return [format_change_read(c) for c in changes]

@router.get("/{change_id}", response_model=ChangeRequestRead)
def get_change_by_id(
    change_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    c = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Change request not found")
    return format_change_read(c)

@router.post("", response_model=ChangeRequestRead)
def create_change_request(
    data: ChangeRequestCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    count = db.query(ChangeRequest).count() + 1
    num = f"CHG-{datetime.now(timezone.utc).year}-{count:04d}"

    c = ChangeRequest(
        change_number=num,
        title=data.title,
        description=data.description,
        change_type=data.change_type.value,
        business_justification=data.business_justification,
        affected_systems=data.affected_systems,
        risk_level=data.risk_level.value,
        risk_assessment=data.risk_assessment,
        implementation_plan=data.implementation_plan,
        test_procedure=data.test_procedure,
        rollback_plan=data.rollback_plan,
        scheduled_start=data.scheduled_start,
        scheduled_end=data.scheduled_end,
        status=ChangeStatus.SUBMITTED_FOR_APPROVAL.value,
        requester_id=current_user.id
    )
    db.add(c)
    db.flush()

    history = ChangeHistory(
        change_request_id=c.id,
        changed_by_id=current_user.id,
        action="SUBMITTED",
        details="Submitted change request for CAB / Manager approval"
    )
    db.add(history)
    db.commit()
    db.refresh(c)

    record_audit_log(db, action="CREATE", entity_type="CHANGE", entity_id=c.id, user=current_user, request=request)
    return format_change_read(c)

@router.post("/{change_id}/approval", response_model=ChangeRequestRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager"]))])
def decide_change_approval(
    change_id: int,
    data: ChangeApprovalRequest,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    c = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Change request not found")

    decision = data.decision.upper()
    if decision not in ["APPROVED", "REJECTED"]:
        raise HTTPException(status_code=400, detail="Decision must be APPROVED or REJECTED")

    now = datetime.now(timezone.utc)
    c.approved_by_id = current_user.id
    c.approval_decision_at = now
    c.approval_notes = data.comments
    c.status = ChangeStatus.APPROVED.value if decision == "APPROVED" else ChangeStatus.REJECTED.value

    approval_entry = ChangeApproval(
        change_request_id=c.id,
        approver_id=current_user.id,
        decision=decision,
        comments=data.comments,
        decided_at=now
    )
    db.add(approval_entry)

    history = ChangeHistory(
        change_request_id=c.id,
        changed_by_id=current_user.id,
        action=decision,
        details=f"Change {decision} by {current_user.full_name}. Notes: {data.comments or 'None'}"
    )
    db.add(history)
    db.commit()
    db.refresh(c)

    record_audit_log(db, action=decision, entity_type="CHANGE", entity_id=c.id, user=current_user, request=request)
    return format_change_read(c)

@router.patch("/{change_id}", response_model=ChangeRequestRead, dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "technician"]))])
def update_change_execution(
    change_id: int,
    data: ChangeRequestUpdate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    c = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Change request not found")

    if data.status is not None:
        c.status = data.status.value
    if data.implementation_outcome is not None:
        c.implementation_outcome = data.implementation_outcome
    if data.scheduled_start is not None:
        c.scheduled_start = data.scheduled_start
    if data.scheduled_end is not None:
        c.scheduled_end = data.scheduled_end

    history = ChangeHistory(
        change_request_id=c.id,
        changed_by_id=current_user.id,
        action="UPDATE",
        details=f"Status set to {c.status}"
    )
    db.add(history)
    db.commit()
    db.refresh(c)
    return format_change_read(c)
