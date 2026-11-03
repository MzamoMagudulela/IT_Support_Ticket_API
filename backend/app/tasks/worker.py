import logging
from app.tasks.celery_app import celery_app
from app.core.database import SessionLocal
from app.services.monitoring_service import generate_simulated_metrics_for_all_devices
from app.services.automation_engine import trigger_automation, TriggerEvent

logger = logging.getLogger(__name__)

@celery_app.task(name="poll_infrastructure_telemetry")
def poll_infrastructure_telemetry():
    db = SessionLocal()
    try:
        metrics = generate_simulated_metrics_for_all_devices(db)
        logger.info(f"Recorded {len(metrics)} telemetry pulses across infrastructure.")
        return len(metrics)
    finally:
        db.close()

@celery_app.task(name="execute_automation_event")
def execute_automation_event(event_name: str, context: dict):
    db = SessionLocal()
    try:
        event = TriggerEvent(event_name)
        trigger_automation(db, event, context)
        logger.info(f"Executed automation event {event_name}")
    except Exception as e:
        logger.error(f"Failed automation trigger {event_name}: {e}")
    finally:
        db.close()
