from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.change import ChangeType, ChangeRisk, ChangeStatus

class ChangeRequestBase(BaseModel):
    title: str
    description: str
    change_type: ChangeType = ChangeType.NORMAL
    business_justification: str
    affected_systems: str
    risk_level: ChangeRisk = ChangeRisk.MEDIUM
    risk_assessment: str
    implementation_plan: str
    test_procedure: str
    rollback_plan: str
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None

class ChangeRequestCreate(ChangeRequestBase):
    pass

class ChangeRequestUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    business_justification: Optional[str] = None
    affected_systems: Optional[str] = None
    risk_level: Optional[ChangeRisk] = None
    risk_assessment: Optional[str] = None
    implementation_plan: Optional[str] = None
    test_procedure: Optional[str] = None
    rollback_plan: Optional[str] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    status: Optional[ChangeStatus] = None
    implementation_outcome: Optional[str] = None

class ChangeApprovalRequest(BaseModel):
    decision: str # APPROVED, REJECTED
    comments: Optional[str] = None

class ChangeRequestRead(ChangeRequestBase):
    id: int
    change_number: str
    status: str
    requester_id: int
    requester_name: Optional[str] = None
    approved_by_name: Optional[str] = None
    approval_decision_at: Optional[datetime] = None
    approval_notes: Optional[str] = None
    implementation_outcome: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
