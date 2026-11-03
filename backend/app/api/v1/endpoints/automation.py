from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.automation import AutomationRule, AutomationExecutionLog, TriggerEvent
from app.schemas.automation import (
    AutomationRuleCreate, AutomationRuleRead, AutomationExecutionLogRead
)
from app.services.automation_engine import trigger_automation
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/automation", tags=["Workflow Automation"])

@router.get("/rules", response_model=List[AutomationRuleRead], dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager"]))])
def get_rules(db: Session = Depends(get_db)):
    return db.query(AutomationRule).all()

@router.post("/rules", response_model=AutomationRuleRead, dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def create_rule(
    data: AutomationRuleCreate,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    rule = AutomationRule(
        name=data.name,
        description=data.description,
        trigger_event=data.trigger_event.value,
        conditions_json=data.conditions_json,
        actions_json=data.actions_json,
        is_active=data.is_active
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    record_audit_log(db, action="CREATE", entity_type="AUTOMATION_RULE", entity_id=rule.id, user=current_user, request=request)
    return rule

@router.get("/logs", response_model=List[AutomationExecutionLogRead], dependencies=[Depends(RoleChecker(["admin", "system administrator", "it_manager", "auditor"]))])
def get_execution_logs(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(AutomationExecutionLog).order_by(desc(AutomationExecutionLog.created_at)).limit(limit).all()

@router.post("/rules/{rule_id}/test", dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def test_automation_rule(
    rule_id: int,
    db: Session = Depends(get_db)
):
    rule = db.query(AutomationRule).filter(AutomationRule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")

    # Simulate triggering with sample context
    sample_context = {
        "id": 999,
        "reference_number": "TIK-TEST-9999",
        "subject": "Automated Rule Diagnostic Test",
        "priority": "CRITICAL",
        "category": "Server"
    }
    trigger_automation(db, TriggerEvent(rule.trigger_event), sample_context)
    return {"message": f"Dispatched test evaluation for rule: '{rule.name}'"}
