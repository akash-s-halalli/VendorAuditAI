"""FastAPI application entry point."""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.v1.router import api_router
from app.config import get_settings
from app.middleware.rate_limit import limiter, rate_limit_exceeded_handler

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
    from app.db import close_db, init_db

    settings = get_settings()

    # Startup: Initialize resources
    # Always init_db to create tables if they don't exist
    # TODO: Replace with Alembic migrations for proper production schema management
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

    # Configure rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

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

    # Root endpoint - returns API info when no static files, otherwise SPA handles it
    static_dir_env = os.getenv("STATIC_FILES_DIR")
    if not static_dir_env or not Path(static_dir_env).exists():

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

    # Serve React SPA from unified container (when STATIC_FILES_DIR is set)
    static_dir = os.getenv("STATIC_FILES_DIR")
    if static_dir and Path(static_dir).exists():
        static_path = Path(static_dir)

        # Serve static assets (JS, CSS, images) from /assets
        assets_dir = static_path / "assets"
        if assets_dir.exists():
            app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

        # Serve other static files (favicon, etc.)
        for static_file in static_path.iterdir():
            if static_file.is_file() and static_file.name != "index.html":
                # Create route for each static file at root level

                @app.get(f"/{static_file.name}", include_in_schema=False)
                async def serve_static_file(
                    file_path: str = str(static_file),
                ) -> FileResponse:
                    return FileResponse(file_path)

        # Catch-all route for SPA client-side routing (must be last)
        @app.get("/{full_path:path}", include_in_schema=False)
        async def serve_spa(full_path: str) -> FileResponse:
            """Serve React SPA for all non-API routes."""
            # Don't intercept API or special routes
            if full_path.startswith(
                ("api/", "docs", "redoc", "openapi.json", "health", "assets/")
            ):
                raise HTTPException(status_code=404, detail="Not found")

            index_file = static_path / "index.html"
            if index_file.exists():
                return FileResponse(str(index_file))
            raise HTTPException(status_code=404, detail="Frontend not found")

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
