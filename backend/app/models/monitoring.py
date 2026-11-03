from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.models.base import TimeStampedModel

class MonitoringDevice(TimeStampedModel):
    __tablename__ = "monitoring_devices"

    name = Column(String(100), unique=True, index=True, nullable=False)
    device_type = Column(String(50), default="SERVER", nullable=False) # SERVER, ROUTER, DATABASE, FIREWALL
    ip_address = Column(String(45), nullable=False)
    hostname = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    last_heartbeat = Column(DateTime, nullable=True)

    metrics = relationship("MonitoringMetric", back_populates="device", cascade="all, delete-orphan", order_by="MonitoringMetric.created_at.desc()")
    alerts = relationship("MonitoringAlert", back_populates="device", cascade="all, delete-orphan", order_by="MonitoringAlert.created_at.desc()")

class MonitoringMetric(TimeStampedModel):
    __tablename__ = "monitoring_metrics"

    device_id = Column(Integer, ForeignKey("monitoring_devices.id", ondelete="CASCADE"), nullable=False, index=True)
    cpu_percent = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    disk_percent = Column(Float, nullable=False)
    ping_ms = Column(Float, nullable=False)
    service_health = Column(String(30), default="HEALTHY", nullable=False) # HEALTHY, DEGRADED, DOWN

    device = relationship("MonitoringDevice", back_populates="metrics")

class MonitoringAlert(TimeStampedModel):
    __tablename__ = "monitoring_alerts"

    device_id = Column(Integer, ForeignKey("monitoring_devices.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_name = Column(String(100), nullable=False)
    severity = Column(String(20), default="WARNING", nullable=False, index=True) # INFO, WARNING, CRITICAL
    message = Column(Text, nullable=False)
    threshold_value = Column(Float, nullable=True)
    actual_value = Column(Float, nullable=True)
    status = Column(String(30), default="ACTIVE", nullable=False, index=True) # ACTIVE, ACKNOWLEDGED, RESOLVED
    incident_id = Column(Integer, ForeignKey("incidents.id", ondelete="SET NULL"), nullable=True)

    device = relationship("MonitoringDevice", back_populates="alerts")
    incident = relationship("Incident")
