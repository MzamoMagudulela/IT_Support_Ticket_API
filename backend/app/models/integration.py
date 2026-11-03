from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from app.models.base import TimeStampedModel

class IntegrationConfig(TimeStampedModel):
    __tablename__ = "integration_configurations"

    name = Column(String(100), unique=True, index=True, nullable=False)
    integration_type = Column(String(50), nullable=False, index=True) # TEAMS_WEBHOOK, SMTP_EMAIL, GITHUB_ISSUES, PROMETHEUS_ALERTMANAGER, ZABBIX_MONITORING, LDAP_AUTH
    config_json = Column(Text, default="{}", nullable=False)
    is_active = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_tested_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)

class WebhookEvent(TimeStampedModel):
    __tablename__ = "webhook_events"

    source = Column(String(50), nullable=False, index=True) # Prometheus, Zabbix, GitHub, Custom
    event_type = Column(String(80), nullable=False)
    payload_json = Column(Text, nullable=False)
    signature_verified = Column(Boolean, default=False, nullable=False)
    status = Column(String(30), default="PROCESSED", nullable=False) # PROCESSED, FAILED, IGNORED
