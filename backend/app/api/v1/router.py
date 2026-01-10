"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    analysis,
    auth,
    compliance,
    dashboard,
    documents,
    query,
    search,
    vendors,
)

api_router = APIRouter()

# Include auth router
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Include vendors router
api_router.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])

# Include documents router
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

# Include search router
api_router.include_router(search.router, prefix="/search", tags=["Search"])

# Include analysis router
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])

# Include query router
api_router.include_router(query.router, prefix="/query", tags=["Query"])

# Include dashboard router
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])

# Include compliance frameworks router
api_router.include_router(
    compliance.router, prefix="/frameworks", tags=["Compliance Frameworks"]
)


@api_router.get("/status", tags=["Status"])
async def api_status() -> dict:
    """Get API v1 status."""
    return {
        "api_version": "v1",
        "status": "operational",
        "endpoints": {
            "auth": "/api/v1/auth",
            "users": "/api/v1/users",
            "vendors": "/api/v1/vendors",
            "documents": "/api/v1/documents",
            "analysis": "/api/v1/analysis",
            "findings": "/api/v1/findings",
            "frameworks": "/api/v1/frameworks",
            "query": "/api/v1/query",
            "dashboard": "/api/v1/dashboard",
        },
    }
