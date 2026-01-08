"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.v1.router import api_router

API_VERSION = "0.1.0"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Initialize and cleanup application resources.

    This context manager handles:
    - Database connection pool initialization
    - Storage backend setup
    - AI client initialization
    - Cleanup on shutdown
    """
    from app.db import init_db, close_db

    settings = get_settings()

    # Startup: Initialize resources
    if settings.is_development:
        # Auto-create tables in development (use Alembic in production)
        await init_db()

    yield

    # Shutdown: Cleanup resources
    await close_db()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="VendorAuditAI API",
        description=(
            "AI-Powered Vendor Security Report Analyzer. "
            "Transform manual SOC 2, SIG, HECVAT reviews from hours to minutes."
        ),
        version=API_VERSION,
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_allow_methods,
        allow_headers=settings.cors_allow_headers,
    )

    # Health check endpoint (outside of API router for load balancer checks)
    @app.get("/health", tags=["Health"])
    async def health_check() -> dict:
        """Check API health status.

        Returns basic health information for load balancers and monitoring.
        """
        return {
            "status": "healthy",
            "version": API_VERSION,
            "environment": settings.app_env,
        }

    @app.get("/", tags=["Root"])
    async def root() -> dict:
        """Root endpoint with API information."""
        return {
            "name": settings.app_name,
            "version": API_VERSION,
            "docs": "/docs" if settings.debug else None,
            "health": "/health",
        }

    # Include API router
    app.include_router(api_router, prefix="/api/v1")

    return app


# Create the application instance
app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
    )
