"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import analysis, auth, documents, search, vendors

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
        },
    }


# TODO: Import and include route modules as they are created
# from app.api.v1.endpoints import users, vendors, documents, analysis
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(vendors.router, prefix="/vendors", tags=["Vendors"])
# api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
# api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
