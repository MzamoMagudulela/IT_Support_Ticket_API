from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class AuditLog(TimeStampedModel):
    __tablename__ = "audit_logs"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    username = Column(String(60), nullable=True, index=True)
    action = Column(String(80), nullable=False, index=True) # CREATE, UPDATE, DELETE, LOGIN, LOGOUT, REASSIGN, ESCALATE, APPROVE, REJECT
    entity_type = Column(String(60), nullable=False, index=True) # TICKET, INCIDENT, ASSET, CHANGE, SECURITY, USER, SYSTEM
    entity_id = Column(String(60), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(255), nullable=True)
    old_values = Column(Text, nullable=True) # JSON string
    new_values = Column(Text, nullable=True) # JSON string

    user = relationship("User")
