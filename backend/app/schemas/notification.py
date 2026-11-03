from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class NotificationRead(BaseModel):
    id: int
    title: str
    message: str
    link: Optional[str] = None
    notification_type: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True
