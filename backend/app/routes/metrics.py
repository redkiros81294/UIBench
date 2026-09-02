"""
Prometheus metrics endpoint.
"""
from fastapi import APIRouter
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

router = APIRouter()


@router.get("/metrics")
async def metrics():
    return generate_latest(), {"Content-Type": CONTENT_TYPE_LATEST}
