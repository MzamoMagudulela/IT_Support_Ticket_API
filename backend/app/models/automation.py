from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
import enum
from app.models.base import TimeStampedModel

class TriggerEvent(str, enum.Enum):
    ON_TICKET_CREATED = "ON_TICKET_CREATED"
    ON_TICKET_UNASSIGNED = "ON_TICKET_UNASSIGNED"
    ON_SLA_WARNING = "ON_SLA_WARNING"
    ON_SECURITY_CRITICAL = "ON_SECURITY_CRITICAL"
    ON_WARRANTY_EXPIRING = "ON_WARRANTY_EXPIRING"
    ON_TICKET_RESOLVED = "ON_TICKET_RESOLVED"
    ON_MONITORING_ALERT = "ON_MONITORING_ALERT"

class AutomationRule(TimeStampedModel):
    __tablename__ = "automation_rules"

    name = Column(String(120), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    trigger_event = Column(String(50), nullable=False, index=True)
    
    conditions_json = Column(Text, default="{}", nullable=False) # JSON condition specification
    actions_json = Column(Text, default="[]", nullable=False) # JSON action list
    
    is_active = Column(Boolean, default=True, nullable=False)
    execution_count = Column(Integer, default=0, nullable=False)

    logs = relationship("AutomationExecutionLog", back_populates="rule", cascade="all, delete-orphan", order_by="AutomationExecutionLog.created_at.desc()")

class AutomationExecutionLog(TimeStampedModel):
    __tablename__ = "automation_execution_logs"

    rule_id = Column(Integer, ForeignKey("automation_rules.id", ondelete="CASCADE"), nullable=False, index=True)
    trigger_event = Column(String(50), nullable=False)
    status = Column(String(30), default="SUCCESS", nullable=False) # SUCCESS, FAILED, SKIPPED
    execution_details = Column(Text, nullable=False)

    rule = relationship("AutomationRule", back_populates="logs")
