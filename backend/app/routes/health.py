"""
Health check routes.
"""
from fastapi import APIRouter, HTTPException
from ..database.connection import db_instance

router = APIRouter()


@router.get("/health")
def health():
    try:
        db_instance.client.admin.command("ping")
        db_status = "healthy"
    except Exception:
        db_status = "unhealthy"

    status = "healthy" if db_status == "healthy" else "degraded"
    return {
        "status": status,
        "checks": {
            "database": db_status,
        },
    }
