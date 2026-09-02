"""
UIBench Backend Application

Enterprise-grade FastAPI service with middleware, health checks, and normalized core integration.
"""
from fastapi import FastAPI
from contextlib import asynccontextmanager

from .config import settings
from .middleware.cors import setup_cors
from .middleware.logging import LoggingMiddleware
from .middleware.tracing import TracingMiddleware
from .middleware.rate_limit import setup_rate_limit
from .routes import auth_router, projects_router, analysis_router, health_router, metrics_router
from .logging_config import configure_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(
        title="UIBench API",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Middleware
    setup_cors(app)
    setup_rate_limit(app)
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(TracingMiddleware)

    # Routes
    app.include_router(auth_router)
    app.include_router(projects_router)
    app.include_router(analysis_router)
    app.include_router(health_router)
    app.include_router(metrics_router)

    @app.get("/health")
    async def health():
        return {"status": "healthy"}

    return app


app = create_app()
