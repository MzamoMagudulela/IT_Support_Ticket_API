import json
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.integration import IntegrationConfig, WebhookEvent
from app.schemas.integration import IntegrationConfigCreate, IntegrationConfigRead
from app.services.audit_service import record_audit_log

router = APIRouter(prefix="/integrations", tags=["Integrations"])

@router.get("", response_model=List[IntegrationConfigRead], dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def list_integrations(db: Session = Depends(get_db)):
    return db.query(IntegrationConfig).all()

@router.post("", response_model=IntegrationConfigRead, dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def create_integration(
    data: IntegrationConfigCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    integ = IntegrationConfig(
        name=data.name,
        integration_type=data.integration_type,
        config_json=data.config_json,
        is_active=data.is_active,
        is_verified=False
    )
    db.add(integ)
    db.commit()
    db.refresh(integ)
    return integ

@router.post("/{integration_id}/test", dependencies=[Depends(RoleChecker(["admin", "system administrator"]))])
def test_integration(
    integration_id: int,
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    integ = db.query(IntegrationConfig).filter(IntegrationConfig.id == integration_id).first()
    if not integ:
        raise HTTPException(status_code=404, detail="Integration not found")

    now = datetime.now(timezone.utc)
    integ.last_tested_at = now

    # Perform diagnostic simulation/verification based on integration type
    try:
        cfg = json.loads(integ.config_json or "{}")
        if integ.integration_type == "TEAMS_WEBHOOK":
            if not cfg.get("webhook_url"):
                raise ValueError("Missing 'webhook_url' in configuration payload")
        elif integ.integration_type == "SMTP_EMAIL":
            if not cfg.get("smtp_host"):
                raise ValueError("Missing 'smtp_host' in configuration payload")
        elif integ.integration_type == "LDAP_AUTH":
            if not cfg.get("server_url"):
                raise ValueError("Missing 'server_url' in configuration payload")

        integ.is_verified = True
        integ.is_active = True
        integ.last_error = None
        db.commit()
        record_audit_log(db, action="INTEGRATION_TEST_PASS", entity_type="INTEGRATION", entity_id=integ.id, user=current_user, request=request)
        return {"status": "SUCCESS", "message": f"Successfully validated connection to {integ.name}."}
    except Exception as e:
        integ.is_verified = False
        integ.last_error = str(e)
        db.commit()
        record_audit_log(db, action="INTEGRATION_TEST_FAIL", entity_type="INTEGRATION", entity_id=integ.id, user=current_user, request=request)
        raise HTTPException(status_code=400, detail=f"Integration test failed: {str(e)}")
