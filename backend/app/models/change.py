from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.models.base import TimeStampedModel

class ChangeType(str, enum.Enum):
    STANDARD = "STANDARD"
    NORMAL = "NORMAL"
    EMERGENCY = "EMERGENCY"

class ChangeRisk(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ChangeStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED_FOR_APPROVAL = "SUBMITTED_FOR_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    SCHEDULED = "SCHEDULED"
    IMPLEMENTING = "IMPLEMENTING"
    COMPLETED = "COMPLETED"
    ROLLED_BACK = "ROLLED_BACK"

class ChangeRequest(TimeStampedModel):
    __tablename__ = "change_requests"

    change_number = Column(String(30), unique=True, index=True, nullable=False)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    change_type = Column(String(30), default=ChangeType.NORMAL.value, nullable=False)
    
    business_justification = Column(Text, nullable=False)
    affected_systems = Column(Text, nullable=False)
    risk_level = Column(String(20), default=ChangeRisk.MEDIUM.value, nullable=False)
    risk_assessment = Column(Text, nullable=False)
    
    implementation_plan = Column(Text, nullable=False)
    test_procedure = Column(Text, nullable=False)
    rollback_plan = Column(Text, nullable=False)
    
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    actual_start = Column(DateTime, nullable=True)
    actual_end = Column(DateTime, nullable=True)
    
    status = Column(String(30), default=ChangeStatus.DRAFT.value, nullable=False, index=True)
    implementation_outcome = Column(Text, nullable=True)
    
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    approved_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    approval_decision_at = Column(DateTime, nullable=True)
    approval_notes = Column(Text, nullable=True)

    requester = relationship("User", foreign_keys=[requester_id])
    approved_by = relationship("User", foreign_keys=[approved_by_id])
    approvals = relationship("ChangeApproval", back_populates="change_request", cascade="all, delete-orphan")
    history_logs = relationship("ChangeHistory", back_populates="change_request", cascade="all, delete-orphan", order_by="ChangeHistory.created_at.desc()")

class ChangeApproval(TimeStampedModel):
    __tablename__ = "change_approvals"

    change_request_id = Column(Integer, ForeignKey("change_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    approver_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    decision = Column(String(20), nullable=False) # APPROVED, REJECTED, PENDING
    comments = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)

    change_request = relationship("ChangeRequest", back_populates="approvals")
    approver = relationship("User")

class ChangeHistory(TimeStampedModel):
    __tablename__ = "change_history"

    change_request_id = Column(Integer, ForeignKey("change_requests.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)

    change_request = relationship("ChangeRequest", back_populates="history_logs")
    changed_by = relationship("User")
