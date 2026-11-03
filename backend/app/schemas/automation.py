from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.automation import TriggerEvent

class AutomationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_event: TriggerEvent
    conditions_json: str = "{}"
    actions_json: str = "[]"
    is_active: bool = True

class AutomationRuleCreate(AutomationRuleBase):
    pass

class AutomationRuleRead(AutomationRuleBase):
    id: int
    execution_count: int
    created_at: datetime

    class Config:
        from_attributes = True

class AutomationExecutionLogRead(BaseModel):
    id: int
    rule_id: int
    trigger_event: str
    status: str
    execution_details: str
    created_at: datetime

    class Config:
        from_attributes = True
