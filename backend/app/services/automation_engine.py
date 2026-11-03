import json
from datetime import datetime, timezone
from typing import Any, Dict
from sqlalchemy.orm import Session
from app.models.automation import AutomationRule, AutomationExecutionLog, TriggerEvent
from app.models.notification import Notification
from app.models.user import User, Role

def match_conditions(conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
    """Safely evaluates condition dictionary against context without eval/exec"""
    for key, expected_value in conditions.items():
        if key not in context:
            return False
        actual_value = context[key]
        if isinstance(expected_value, list):
            if actual_value not in expected_value:
                return False
        elif str(actual_value).lower() != str(expected_value).lower():
            return False
    return True

def execute_actions(db: Session, actions: list, context: Dict[str, Any]) -> list[str]:
    """Execute supported declarative actions safely"""
    executed_results = []
    
    for action in actions:
        action_type = action.get("type") or action.get("action")
        
        if action_type == "NOTIFY_ROLE":
            role_name = action.get("role", "it_manager")
            title = action.get("title", f"Automated Alert: {context.get('subject', 'ITSM Event')}")
            message = action.get("message", f"Event triggered for {context.get('reference_number', 'record')}")
            
            # Find users with this role
            target_role = db.query(Role).filter(Role.name.ilike(f"%{role_name}%")).first()
            if target_role:
                for target_user in target_role.users:
                    notif = Notification(
                        user_id=target_user.id,
                        title=title,
                        message=message,
                        link=action.get("link", f"/tickets/{context.get('id', '')}"),
                        notification_type="ALERT"
                    )
                    db.add(notif)
                executed_results.append(f"Notified {len(target_role.users)} users with role {role_name}")

        elif action_type == "NOTIFY_USER":
            user_id = action.get("user_id") or context.get("assigned_technician_id") or context.get("requester_id")
            if user_id:
                notif = Notification(
                    user_id=user_id,
                    title=action.get("title", "Automated ITSM Notification"),
                    message=action.get("message", "An automated rule has processed your item."),
                    link=action.get("link", f"/tickets/{context.get('id', '')}"),
                    notification_type="INFO"
                )
                db.add(notif)
                executed_results.append(f"Notified user {user_id}")

        elif action_type == "ESCALATE_TICKET":
            ticket_id = context.get("id")
            from app.models.ticket import Ticket
            t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
            if t:
                t.escalation_level += 1
                executed_results.append(f"Escalated ticket {t.reference_number} to level {t.escalation_level}")

        elif action_type == "LOG_MESSAGE":
            executed_results.append(f"Log: {action.get('message', 'Rule matched')}")

    db.commit()
    return executed_results

def trigger_automation(db: Session, event: TriggerEvent, context: Dict[str, Any]):
    """Entry point for triggering rules matching an event type"""
    rules = db.query(AutomationRule).filter(
        AutomationRule.trigger_event == event.value,
        AutomationRule.is_active == True
    ).all()

    for rule in rules:
        try:
            conditions = json.loads(rule.conditions_json or "{}")
            actions = json.loads(rule.actions_json or "[]")
        except Exception as err:
            log = AutomationExecutionLog(
                rule_id=rule.id,
                trigger_event=event.value,
                status="FAILED",
                execution_details=f"Invalid JSON configuration: {str(err)}"
            )
            db.add(log)
            db.commit()
            continue

        if match_conditions(conditions, context):
            try:
                results = execute_actions(db, actions, context)
                rule.execution_count += 1
                log = AutomationExecutionLog(
                    rule_id=rule.id,
                    trigger_event=event.value,
                    status="SUCCESS",
                    execution_details=json.dumps({"executed": results, "context": context}, default=str)
                )
                db.add(log)
                db.commit()
            except Exception as err:
                log = AutomationExecutionLog(
                    rule_id=rule.id,
                    trigger_event=event.value,
                    status="FAILED",
                    execution_details=f"Execution error: {str(err)}"
                )
                db.add(log)
                db.commit()
        else:
            # Did not match conditions
            log = AutomationExecutionLog(
                rule_id=rule.id,
                trigger_event=event.value,
                status="SKIPPED",
                execution_details="Conditions did not match current context"
            )
            db.add(log)
            db.commit()
