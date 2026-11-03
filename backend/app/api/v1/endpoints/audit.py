from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.audit import AuditLog
from app.schemas.report import AuditLogRead

router = APIRouter(prefix="/audit", tags=["Audit Logs"])

@router.get("", response_model=List[AuditLogRead], dependencies=[Depends(RoleChecker(["admin", "system administrator", "auditor"]))])
def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action.upper())
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type.upper())
    return query.order_by(desc(AuditLog.created_at)).limit(limit).all()
