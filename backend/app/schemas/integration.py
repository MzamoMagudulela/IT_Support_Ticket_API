from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class IntegrationConfigBase(BaseModel):
    name: str
    integration_type: str
    config_json: str = "{}"
    is_active: bool = False

class IntegrationConfigCreate(IntegrationConfigBase):
    pass

class IntegrationConfigRead(IntegrationConfigBase):
    id: int
    is_verified: bool
    last_tested_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
