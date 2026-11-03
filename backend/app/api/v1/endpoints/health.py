from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db

router = APIRouter(tags=["Health & Diagnostics"])

@router.get("/health")
def health_check():
    """Liveness probe: verifies that API process is alive and accepting requests"""
    return {
        "status": "HEALTHY",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "service": "enterprise-itsm-backend"
    }

@router.get("/ready")
def readiness_check(response: Response, db: Session = Depends(get_db)):
    """Readiness probe: validates database connectivity and core system dependencies"""
    checks = {"database": "UNKNOWN"}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "UP"
        return {
            "status": "READY",
            "dependencies": checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    except Exception as e:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        checks["database"] = f"DOWN: {str(e)}"
        return {
            "status": "UNAVAILABLE",
            "dependencies": checks,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
