from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth, users, departments, tickets, incidents, assets,
    changes, security, knowledge, sla, automation, monitoring,
    integrations, reports, notifications, audit, health
)

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(departments.router)
api_router.include_router(tickets.router)
api_router.include_router(incidents.router)
api_router.include_router(assets.router)
api_router.include_router(changes.router)
api_router.include_router(security.router)
api_router.include_router(knowledge.router)
api_router.include_router(sla.router)
api_router.include_router(automation.router)
api_router.include_router(monitoring.router)
api_router.include_router(integrations.router)
api_router.include_router(reports.router)
api_router.include_router(notifications.router)
api_router.include_router(audit.router)
