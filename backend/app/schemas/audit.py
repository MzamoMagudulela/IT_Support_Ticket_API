from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AuditLogRead(BaseModel):
    id: int
    user_id: Optional[int] = None
    username: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    old_values: Optional[str] = None
    new_values: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
