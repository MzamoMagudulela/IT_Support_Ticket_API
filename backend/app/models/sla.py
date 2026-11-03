from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class SLAPolicy(TimeStampedModel):
    __tablename__ = "sla_policies"

    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    priority = Column(String(20), nullable=False, index=True) # LOW, MEDIUM, HIGH, CRITICAL
    service_category = Column(String(60), nullable=True, index=True)
    
    target_response_mins = Column(Integer, nullable=False) # e.g. 15 mins for Critical
    target_resolution_mins = Column(Integer, nullable=False) # e.g. 120 mins for Critical
    business_hours_only = Column(Boolean, default=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    trackings = relationship("SLATracking", back_populates="policy")

class SLATracking(TimeStampedModel):
    __tablename__ = "sla_tracking"

    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    sla_policy_id = Column(Integer, ForeignKey("sla_policies.id", ondelete="RESTRICT"), nullable=False)
    
    response_deadline = Column(DateTime, nullable=False)
    resolution_deadline = Column(DateTime, nullable=False)
    
    response_met = Column(Boolean, nullable=True) # None=pending, True=met, False=breached
    resolution_met = Column(Boolean, nullable=True)
    
    paused_duration_minutes = Column(Integer, default=0, nullable=False)
    last_paused_at = Column(DateTime, nullable=True)

    ticket = relationship("Ticket", back_populates="sla_tracking")
    policy = relationship("SLAPolicy", back_populates="trackings")
