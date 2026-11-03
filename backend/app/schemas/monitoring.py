from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class MonitoringDeviceBase(BaseModel):
    name: str
    device_type: str = "SERVER"
    ip_address: str
    hostname: Optional[str] = None
    is_active: bool = True

class MonitoringDeviceCreate(MonitoringDeviceBase):
    pass

class MonitoringMetricRead(BaseModel):
    id: int
    device_id: int
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    ping_ms: float
    service_health: str
    created_at: datetime

    class Config:
        from_attributes = True

class MonitoringAlertRead(BaseModel):
    id: int
    device_id: int
    device_name: Optional[str] = None
    alert_name: str
    severity: str
    message: str
    threshold_value: Optional[float] = None
    actual_value: Optional[float] = None
    status: str
    incident_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MonitoringDeviceRead(MonitoringDeviceBase):
    id: int
    last_heartbeat: Optional[datetime] = None
    latest_cpu: Optional[float] = None
    latest_memory: Optional[float] = None
    latest_disk: Optional[float] = None
    latest_health: Optional[str] = "HEALTHY"
    active_alerts_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True

class ExternalWebhookAlert(BaseModel):
    receiver: Optional[str] = None
    status: str = "firing"
    alerts: List[dict] = []
