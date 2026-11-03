from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class SLAPolicyBase(BaseModel):
    name: str
    description: Optional[str] = None
    priority: str
    service_category: Optional[str] = None
    target_response_mins: int
    target_resolution_mins: int
    business_hours_only: bool = True
    is_active: bool = True

class SLAPolicyCreate(SLAPolicyBase):
    pass

class SLAPolicyRead(SLAPolicyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class SLAPerformanceMetrics(BaseModel):
    compliance_percentage: float
    total_evaluated_tickets: int
    met_sla_count: int
    breached_sla_count: int
    avg_first_response_hours: float
    avg_resolution_hours: float
    currently_overdue_tickets: int
