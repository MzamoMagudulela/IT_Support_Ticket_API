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

class OperationalKPIs(BaseModel):
    total_tickets: int
    open_tickets: int
    resolved_tickets: int
    critical_tickets: int
    escalated_tickets: int
    avg_resolution_hours: float
    sla_compliance_percent: float
    
    total_incidents: int
    major_incidents: int
    open_incidents: int
    
    total_assets: int
    active_assets: int
    assets_maintenance: int
    expiring_warranties_30d: int
    
    total_security_incidents: int
    critical_security_alerts: int
    
    daily_ticket_trends: list = []
    category_distribution: list = []
    priority_distribution: list = []
    department_comparison: list = []
    technician_workload: list = []
