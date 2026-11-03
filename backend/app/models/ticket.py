from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
import enum
from app.models.base import TimeStampedModel

class PriorityLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class ImpactLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class UrgencyLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class TicketStatus(str, enum.Enum):
    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_USER = "PENDING_USER"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"

class CommentType(str, enum.Enum):
    PUBLIC = "PUBLIC"
    INTERNAL_NOTE = "INTERNAL_NOTE"

class LinkType(str, enum.Enum):
    RELATES_TO = "RELATES_TO"
    DUPLICATE_OF = "DUPLICATE_OF"
    BLOCKS = "BLOCKS"
    BLOCKED_BY = "BLOCKED_BY"
    MERGED_INTO = "MERGED_INTO"

class Ticket(TimeStampedModel):
    __tablename__ = "tickets"

    reference_number = Column(String(30), unique=True, index=True, nullable=False)
    subject = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=False)
    
    requester_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    assigned_technician_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    department_id = Column(Integer, ForeignKey("departments.id", ondelete="SET NULL"), nullable=True, index=True)
    related_asset_id = Column(Integer, ForeignKey("assets.id", ondelete="SET NULL"), nullable=True)

    category = Column(String(60), default="Hardware", nullable=False, index=True)
    priority = Column(String(20), default=PriorityLevel.MEDIUM.value, nullable=False, index=True)
    impact = Column(String(20), default=ImpactLevel.MEDIUM.value, nullable=False)
    urgency = Column(String(20), default=UrgencyLevel.MEDIUM.value, nullable=False)
    status = Column(String(20), default=TicketStatus.NEW.value, nullable=False, index=True)
    
    response_deadline = Column(DateTime, nullable=True)
    resolution_deadline = Column(DateTime, nullable=True)
    first_responded_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    resolution_details = Column(Text, nullable=True)
    
    reopened_count = Column(Integer, default=0, nullable=False)
    escalation_level = Column(Integer, default=0, nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False, index=True)

    # Relationships
    requester = relationship("User", foreign_keys=[requester_id], back_populates="requested_tickets")
    assigned_technician = relationship("User", foreign_keys=[assigned_technician_id], back_populates="assigned_tickets")
    department = relationship("Department", back_populates="tickets")
    related_asset = relationship("Asset", back_populates="tickets")
    
    comments = relationship("TicketComment", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketComment.created_at.asc()")
    attachments = relationship("TicketAttachment", back_populates="ticket", cascade="all, delete-orphan")
    assignments = relationship("TicketAssignment", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketAssignment.created_at.desc()")
    status_history = relationship("TicketStatusHistory", back_populates="ticket", cascade="all, delete-orphan", order_by="TicketStatusHistory.created_at.desc()")
    
    sla_tracking = relationship("SLATracking", back_populates="ticket", uselist=False, cascade="all, delete-orphan")
    source_links = relationship("TicketLink", foreign_keys="TicketLink.source_ticket_id", back_populates="source_ticket")
    target_links = relationship("TicketLink", foreign_keys="TicketLink.target_ticket_id", back_populates="target_ticket")

class TicketComment(TimeStampedModel):
    __tablename__ = "ticket_comments"

    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    author_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    comment_type = Column(String(20), default=CommentType.PUBLIC.value, nullable=False) # PUBLIC vs INTERNAL_NOTE
    content = Column(Text, nullable=False)

    ticket = relationship("Ticket", back_populates="comments")
    author = relationship("User")

class TicketAttachment(TimeStampedModel):
    __tablename__ = "ticket_attachments"

    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    content_type = Column(String(100), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    ticket = relationship("Ticket", back_populates="attachments")
    uploaded_by = relationship("User")

class TicketAssignment(TimeStampedModel):
    __tablename__ = "ticket_assignments"

    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    assigned_by_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    previous_technician_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    new_technician_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    reason = Column(String(255), nullable=True)

    ticket = relationship("Ticket", back_populates="assignments")
    assigned_by = relationship("User", foreign_keys=[assigned_by_id])
    previous_technician = relationship("User", foreign_keys=[previous_technician_id])
    new_technician = relationship("User", foreign_keys=[new_technician_id])

class TicketStatusHistory(TimeStampedModel):
    __tablename__ = "ticket_status_history"

    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    changed_by_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    old_status = Column(String(30), nullable=False)
    new_status = Column(String(30), nullable=False)
    comment = Column(String(255), nullable=True)

    ticket = relationship("Ticket", back_populates="status_history")
    changed_by = relationship("User")

class TicketLink(TimeStampedModel):
    __tablename__ = "ticket_links"

    source_ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    target_ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False, index=True)
    link_type = Column(String(30), default=LinkType.RELATES_TO.value, nullable=False)

    source_ticket = relationship("Ticket", foreign_keys=[source_ticket_id], back_populates="source_links")
    target_ticket = relationship("Ticket", foreign_keys=[target_ticket_id], back_populates="target_links")
