import json
from typing import Any, Optional
from fastapi import Request
from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from app.models.user import User

def record_audit_log(
    db: Session,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    user: Optional[User] = None,
    old_values: Optional[dict] = None,
    new_values: Optional[dict] = None,
    request: Optional[Request] = None
) -> AuditLog:
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    log_entry = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else "System",
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        ip_address=ip_address,
        user_agent=user_agent,
        old_values=json.dumps(old_values, default=str) if old_values else None,
        new_values=json.dumps(new_values, default=str) if new_values else None
    )
    db.add(log_entry)
    db.commit()
    return log_entry
