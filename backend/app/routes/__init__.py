"""
Backend routes package.
"""
from .auth import router as auth_router
from .projects import router as projects_router
from .analysis import router as analysis_router
from .health import router as health_router
from .metrics import router as metrics_router

__all__ = ["auth_router", "projects_router", "analysis_router", "health_router", "metrics_router"]
