from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.database import get_db
from app.core.permissions import get_current_active_user, RoleChecker
from app.models.user import User
from app.models.monitoring import MonitoringDevice, MonitoringMetric, MonitoringAlert
from app.schemas.monitoring import (
    MonitoringDeviceCreate, MonitoringDeviceRead, MonitoringAlertRead,
    MonitoringMetricRead, ExternalWebhookAlert
)
from app.services.monitoring_service import (
    generate_simulated_metrics_for_all_devices,
    create_or_escalate_alert
)

router = APIRouter(prefix="/monitoring", tags=["Infrastructure Monitoring"])

@router.get("/devices", response_model=List[MonitoringDeviceRead])
def get_monitoring_devices(db: Session = Depends(get_db)):
    devices = db.query(MonitoringDevice).all()
    results = []
    for d in devices:
        latest = db.query(MonitoringMetric).filter(MonitoringMetric.device_id == d.id).order_by(desc(MonitoringMetric.created_at)).first()
        active_alerts = db.query(MonitoringAlert).filter(MonitoringAlert.device_id == d.id, MonitoringAlert.status == "ACTIVE").count()
        results.append(
            MonitoringDeviceRead(
                id=d.id,
                name=d.name,
                device_type=d.device_type,
                ip_address=d.ip_address,
                hostname=d.hostname,
                is_active=d.is_active,
                last_heartbeat=d.last_heartbeat,
                latest_cpu=latest.cpu_percent if latest else 0.0,
                latest_memory=latest.memory_percent if latest else 0.0,
                latest_disk=latest.disk_percent if latest else 0.0,
                latest_health=latest.service_health if latest else "HEALTHY",
                active_alerts_count=active_alerts,
                created_at=d.created_at
            )
        )
    return results

@router.post("/devices", response_model=MonitoringDeviceRead, dependencies=[Depends(RoleChecker(["admin", "it_manager"]))])
def create_monitoring_device(data: MonitoringDeviceCreate, db: Session = Depends(get_db)):
    dev = MonitoringDevice(
        name=data.name,
        device_type=data.device_type,
        ip_address=data.ip_address,
        hostname=data.hostname,
        is_active=data.is_active
    )
    db.add(dev)
    db.commit()
    db.refresh(dev)
    return MonitoringDeviceRead(
        id=dev.id,
        name=dev.name,
        device_type=dev.device_type,
        ip_address=dev.ip_address,
        hostname=dev.hostname,
        is_active=dev.is_active,
        created_at=dev.created_at
    )

@router.get("/devices/{device_id}/metrics", response_model=List[MonitoringMetricRead])
def get_device_metrics_history(device_id: int, limit: int = 30, db: Session = Depends(get_db)):
    return db.query(MonitoringMetric).filter(MonitoringMetric.device_id == device_id).order_by(desc(MonitoringMetric.created_at)).limit(limit).all()

@router.get("/alerts", response_model=List[MonitoringAlertRead])
def get_monitoring_alerts(status: Optional[str] = "ACTIVE", db: Session = Depends(get_db)):
    query = db.query(MonitoringAlert)
    if status:
        query = query.filter(MonitoringAlert.status == status.upper())
    alerts = query.order_by(desc(MonitoringAlert.created_at)).all()
    return [
        MonitoringAlertRead(
            id=a.id,
            device_id=a.device_id,
            device_name=a.device.name if a.device else f"Device #{a.device_id}",
            alert_name=a.alert_name,
            severity=a.severity,
            message=a.message,
            threshold_value=a.threshold_value,
            actual_value=a.actual_value,
            status=a.status,
            incident_id=a.incident_id,
            created_at=a.created_at
        ) for a in alerts
    ]

@router.post("/pulse")
def trigger_telemetry_pulse(db: Session = Depends(get_db)):
    """Simulates real-time telemetry pulse across infrastructure"""
    metrics = generate_simulated_metrics_for_all_devices(db)
    return {"message": f"Generated telemetry update for {len(metrics)} devices"}

@router.post("/webhook/prometheus")
def prometheus_alertmanager_webhook(payload: ExternalWebhookAlert, db: Session = Depends(get_db)):
    """Receives Prometheus Alertmanager webhook payloads and translates alerts into monitoring records and incidents"""
    processed = 0
    # Find or use fallback device
    device = db.query(MonitoringDevice).filter(MonitoringDevice.is_active == True).first()
    if not device:
        device = MonitoringDevice(name="Prometheus-Collector", ip_address="127.0.0.1", device_type="SERVER")
        db.add(device)
        db.commit()
        db.refresh(device)

    for alert_data in payload.alerts:
        labels = alert_data.get("labels", {})
        annotations = alert_data.get("annotations", {})
        alert_name = labels.get("alertname", "PrometheusAlert")
        severity = labels.get("severity", "WARNING").upper()
        if severity not in ["INFO", "WARNING", "CRITICAL"]:
            severity = "CRITICAL" if "crit" in severity.lower() else "WARNING"
        summary = annotations.get("summary") or annotations.get("description") or f"Prometheus alert: {alert_name}"
        create_or_escalate_alert(db, device, alert_name, severity, summary, threshold=100.0, actual=100.0)
        processed += 1

    return {"status": "success", "processed_alerts": processed}

@router.post("/webhook/zabbix")
def zabbix_monitoring_webhook(payload: dict, db: Session = Depends(get_db)):
    """Receives Zabbix webhook notification payload"""
    device_name = payload.get("host", "Zabbix-Monitored-Host")
    device = db.query(MonitoringDevice).filter(MonitoringDevice.name.ilike(device_name)).first()
    if not device:
        device = MonitoringDevice(name=device_name, ip_address=payload.get("ip", "10.0.0.50"), device_type="SERVER")
        db.add(device)
        db.commit()
        db.refresh(device)

    alert_name = payload.get("trigger_name", "Zabbix Problem")
    severity = payload.get("severity", "CRITICAL").upper()
    create_or_escalate_alert(db, device, alert_name, severity, payload.get("details", alert_name), threshold=0.0, actual=1.0)
    return {"status": "success", "device": device_name}
