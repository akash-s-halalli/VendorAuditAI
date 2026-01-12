"""API v1 router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import (
    agents,
    analysis,
    audit,
    auth,
    categorization,
    compliance,
    dashboard,
    documents,
    export,
    monitoring,
    query,
    remediation,
    search,
    sso,
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

# Include categorization router
api_router.include_router(
    categorization.router, prefix="/categorization", tags=["Vendor Categorization"]
)

# Include export router
api_router.include_router(export.router, prefix="/export", tags=["Export"])

# Include remediation router
api_router.include_router(
    remediation.router, prefix="/remediation", tags=["Remediation"]
)

# Include monitoring router
api_router.include_router(
    monitoring.router, prefix="/monitoring", tags=["Monitoring"]
)

# Include audit router
api_router.include_router(audit.router, prefix="/audit", tags=["Audit"])

# Include SSO router
api_router.include_router(sso.router, prefix="/sso", tags=["SSO"])

# Include agents router
api_router.include_router(agents.router, prefix="/agents", tags=["AI Agents"])


@api_router.get("/status", tags=["Status"])
async def api_status() -> dict:
    """Get API v1 status."""
    return {
        "api_version": "v1",
        "status": "operational",
        "endpoints": {
            "agents": "/api/v1/agents",
            "analysis": "/api/v1/analysis",
            "audit": "/api/v1/audit",
            "auth": "/api/v1/auth",
            "categorization": "/api/v1/categorization",
            "dashboard": "/api/v1/dashboard",
            "documents": "/api/v1/documents",
            "export": "/api/v1/export",
            "findings": "/api/v1/findings",
            "frameworks": "/api/v1/frameworks",
            "monitoring": "/api/v1/monitoring",
            "query": "/api/v1/query",
            "remediation": "/api/v1/remediation",
            "sso": "/api/v1/sso",
            "users": "/api/v1/users",
            "vendors": "/api/v1/vendors",
        },
    }
