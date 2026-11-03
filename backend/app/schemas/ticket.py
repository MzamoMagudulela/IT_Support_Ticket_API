from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from app.models.ticket import PriorityLevel, ImpactLevel, UrgencyLevel, TicketStatus, CommentType, LinkType

class TicketCommentBase(BaseModel):
    comment_type: CommentType = CommentType.PUBLIC
    content: str

class TicketCommentCreate(TicketCommentBase):
    pass

class TicketCommentRead(TicketCommentBase):
    id: int
    ticket_id: int
    author_id: int
    author_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TicketAttachmentRead(BaseModel):
    id: int
    ticket_id: int
    file_name: str
    file_path: str
    file_size_bytes: int
    content_type: str
    uploaded_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class TicketStatusHistoryRead(BaseModel):
    id: int
    ticket_id: int
    changed_by_id: int
    changed_by_name: Optional[str] = None
    old_status: str
    new_status: str
    comment: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TicketAssignmentRead(BaseModel):
    id: int
    ticket_id: int
    assigned_by_id: int
    assigned_by_name: Optional[str] = None
    previous_technician_name: Optional[str] = None
    new_technician_name: Optional[str] = None
    reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TicketBase(BaseModel):
    subject: str
    description: str
    category: str = "Hardware"
    impact: ImpactLevel = ImpactLevel.MEDIUM
    urgency: UrgencyLevel = UrgencyLevel.MEDIUM
    department_id: Optional[int] = None
    related_asset_id: Optional[int] = None

class TicketCreate(TicketBase):
    pass

class TicketUpdate(BaseModel):
    subject: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    impact: Optional[ImpactLevel] = None
    urgency: Optional[UrgencyLevel] = None
    department_id: Optional[int] = None
    related_asset_id: Optional[int] = None
    resolution_details: Optional[str] = None

class TicketAssignRequest(BaseModel):
    technician_id: int
    reason: Optional[str] = "Assigned for investigation and resolution"

class TicketStatusUpdateRequest(BaseModel):
    new_status: TicketStatus
    comment: Optional[str] = None
    resolution_details: Optional[str] = None

class TicketLinkRequest(BaseModel):
    target_ticket_id: int
    link_type: LinkType = LinkType.RELATES_TO

class TicketMergeRequest(BaseModel):
    target_ticket_id: int
    reason: Optional[str] = "Merged duplicate ticket into master ticket"

class TicketReopenRequest(BaseModel):
    reason: str

class TicketEscalateRequest(BaseModel):
    reason: str

class TicketRead(BaseModel):
    id: int
    reference_number: str
    subject: str
    description: str
    category: str
    priority: str
    impact: str
    urgency: str
    status: str
    escalation_level: int
    reopened_count: int
    
    requester_id: int
    requester_name: Optional[str] = None
    requester_email: Optional[str] = None
    
    assigned_technician_id: Optional[int] = None
    technician_name: Optional[str] = None
    
    department_id: Optional[int] = None
    department_name: Optional[str] = None
    
    related_asset_id: Optional[int] = None
    related_asset_tag: Optional[str] = None
    
    response_deadline: Optional[datetime] = None
    resolution_deadline: Optional[datetime] = None
    first_responded_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    resolution_details: Optional[str] = None
    
    is_deleted: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TicketDetailRead(TicketRead):
    comments: List[TicketCommentRead] = []
    attachments: List[TicketAttachmentRead] = []
    status_history: List[TicketStatusHistoryRead] = []
    assignments: List[TicketAssignmentRead] = []

class TicketListResponse(BaseModel):
    items: List[TicketRead]
    total: int
    page: int
    page_size: int
    total_pages: int
