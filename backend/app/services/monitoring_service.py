import random
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.models.monitoring import MonitoringDevice, MonitoringMetric, MonitoringAlert
from app.models.incident import Incident, IncidentSeverity, IncidentStatus

def record_device_metric(
    db: Session,
    device_id: int,
    cpu_percent: float,
    memory_percent: float,
    disk_percent: float,
    ping_ms: float,
    service_health: str = "HEALTHY"
) -> MonitoringMetric:
    device = db.query(MonitoringDevice).filter(MonitoringDevice.id == device_id).first()
    if device:
        device.last_heartbeat = datetime.now(timezone.utc)
    
    metric = MonitoringMetric(
        device_id=device_id,
        cpu_percent=round(cpu_percent, 1),
        memory_percent=round(memory_percent, 1),
        disk_percent=round(disk_percent, 1),
        ping_ms=round(ping_ms, 1),
        service_health=service_health
    )
    db.add(metric)

    # Threshold checks: CPU > 90% or Disk > 90% or Health == DOWN triggers an alert
    if cpu_percent >= 90.0:
        create_or_escalate_alert(
            db, device, "HIGH_CPU_LOAD", "CRITICAL",
            f"Device {device.name if device else device_id} CPU usage reached {cpu_percent}%",
            threshold=90.0, actual=cpu_percent
        )
    elif memory_percent >= 92.0:
        create_or_escalate_alert(
            db, device, "HIGH_MEMORY_PRESSURE", "WARNING",
            f"Device {device.name if device else device_id} memory usage reached {memory_percent}%",
            threshold=92.0, actual=memory_percent
        )
    elif service_health == "DOWN":
        create_or_escalate_alert(
            db, device, "SERVICE_OUTAGE", "CRITICAL",
            f"Device {device.name if device else device_id} heartbeat failure or service DOWN",
            threshold=1.0, actual=0.0
        )

    db.commit()
    return metric

def create_or_escalate_alert(
    db: Session,
    device: MonitoringDevice,
    alert_name: str,
    severity: str,
    message: str,
    threshold: float,
    actual: float
) -> MonitoringAlert:
    # Check if there is already an active alert for this device & alert_name
    existing_alert = db.query(MonitoringAlert).filter(
        MonitoringAlert.device_id == device.id,
        MonitoringAlert.alert_name == alert_name,
        MonitoringAlert.status == "ACTIVE"
    ).first()

    if existing_alert:
        existing_alert.actual_value = actual
        existing_alert.message = message
        return existing_alert

    alert = MonitoringAlert(
        device_id=device.id,
        alert_name=alert_name,
        severity=severity,
        message=message,
        threshold_value=threshold,
        actual_value=actual,
        status="ACTIVE"
    )
    db.add(alert)
    db.flush()

    # Automatically create an IT Incident if severity is CRITICAL
    if severity == "CRITICAL":
        import uuid
        unique_suffix = uuid.uuid4().hex[:6].upper()
        incident_number = f"INC-MON-{datetime.now(timezone.utc).strftime('%m%d%H%M')}-{unique_suffix}"
        incident = Incident(
            incident_number=incident_number,
            title=f"Monitoring Alert: {alert_name} on {device.name}",
            description=f"Automated incident triggered by infrastructure monitor.\nDetails: {message}\nHost IP: {device.ip_address}",
            is_major=True if alert_name == "SERVICE_OUTAGE" else False,
            affected_service=device.device_type,
            severity=IncidentSeverity.SEV1_CRITICAL.value if alert_name == "SERVICE_OUTAGE" else IncidentSeverity.SEV2_HIGH.value,
            status=IncidentStatus.DETECTED.value,
            reporter_id=1 # System/Admin user
        )
        db.add(incident)
        db.flush()
        alert.incident_id = incident.id

    db.commit()
    db.refresh(alert)
    return alert

def generate_simulated_metrics_for_all_devices(db: Session):
    """Generates realistic telemetry pulses for all registered active devices"""
    devices = db.query(MonitoringDevice).filter(MonitoringDevice.is_active == True).all()
    metrics = []
    for d in devices:
        cpu = random.uniform(15.0, 78.0)
        # Spike one occasionally for demo
        if "DB" in d.name and random.random() < 0.15:
            cpu = random.uniform(91.0, 96.5)
        mem = random.uniform(30.0, 82.0)
        disk = random.uniform(40.0, 75.0)
        ping = random.uniform(2.0, 24.0)
        health = "HEALTHY" if cpu < 90 else "DEGRADED"
        m = record_device_metric(db, d.id, cpu, mem, disk, ping, health)
        metrics.append(m)
    return metrics
