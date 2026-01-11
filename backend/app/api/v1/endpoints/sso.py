"""SSO/SAML 2.0 API endpoints.

Provides endpoints for:
- SP metadata exposure
- SSO login initiation
- SAML Assertion Consumer Service (ACS)
- SSO configuration management
"""

import logging

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin_user
from app.db import get_db
from app.models import User
from app.models.audit_log import AuditAction
from app.schemas.sso import (
    SSOCallbackResponse,
    SSOConfigCreate,
    SSOConfigResponse,
    SSOConfigUpdate,
    SSOErrorResponse,
    SSOLoginRequest,
    SSOLoginResponse,
    SSOMetadataResponse,
    SSOStatusResponse,
)
from app.services.audit import get_audit_service
from app.services.sso import SAMLValidationError, get_sso_service

logger = logging.getLogger(__name__)

router = APIRouter(tags=["SSO"])


def _get_client_ip(request: Request) -> str | None:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return None


def _get_user_agent(request: Request) -> str | None:
    """Extract user agent from request."""
    return request.headers.get("User-Agent")


# ============================================================================
# Public Endpoints (No Authentication Required)
# ============================================================================


@router.get(
    "/metadata/{org_id}",
    response_class=Response,
    responses={
        200: {
            "content": {"application/xml": {}},
            "description": "SAML SP metadata XML",
        },
        404: {"description": "SSO not configured"},
    },
)
async def get_sp_metadata(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Get SAML Service Provider metadata for an organization.

    This endpoint is public and returns the SP metadata XML that needs to be
    configured in the Identity Provider.

    Args:
        org_id: Organization ID

    Returns:
        XML metadata document
    """
    sso_service = get_sso_service(db)
    sso_config = await sso_service.get_sso_config(org_id)

    if not sso_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO is not configured for this organization",
        )

    metadata_xml = sso_service.generate_sp_metadata(sso_config)

    return Response(
        content=metadata_xml,
        media_type="application/xml",
        headers={"Content-Disposition": f'attachment; filename="sp-metadata-{org_id}.xml"'},
    )


@router.get("/login/{org_id}", response_model=SSOLoginResponse)
async def initiate_sso_login(
    org_id: str,
    relay_state: str | None = Query(
        default=None,
        description="URL to redirect to after successful authentication",
    ),
    db: AsyncSession = Depends(get_db),
) -> SSOLoginResponse:
    """Initiate SSO login by redirecting to the Identity Provider.

    This endpoint generates a SAML AuthnRequest and returns the IdP redirect URL.
    The client should redirect the user to this URL.

    Args:
        org_id: Organization ID
        relay_state: Optional URL to redirect to after login

    Returns:
        SSO login response with redirect URL
    """
    sso_service = get_sso_service(db)
    sso_config = await sso_service.get_sso_config(org_id)

    if not sso_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO is not configured for this organization",
        )

    if not sso_config.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSO is not enabled for this organization",
        )

    redirect_url, saml_request = sso_service.generate_authn_request(
        sso_config, relay_state
    )

    return SSOLoginResponse(
        redirect_url=redirect_url,
        saml_request=saml_request,
    )


@router.get("/login/{org_id}/redirect")
async def sso_login_redirect(
    org_id: str,
    relay_state: str | None = Query(default=None),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Redirect to Identity Provider for SSO login.

    This is a convenience endpoint that directly redirects the user to the IdP
    instead of returning a JSON response.

    Args:
        org_id: Organization ID
        relay_state: Optional URL to redirect to after login

    Returns:
        Redirect to Identity Provider
    """
    sso_service = get_sso_service(db)
    sso_config = await sso_service.get_sso_config(org_id)

    if not sso_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO is not configured for this organization",
        )

    if not sso_config.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="SSO is not enabled for this organization",
        )

    redirect_url, _ = sso_service.generate_authn_request(sso_config, relay_state)

    return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)


@router.post("/acs/{org_id}", response_model=SSOCallbackResponse)
async def assertion_consumer_service(
    request: Request,
    org_id: str,
    SAMLResponse: str = Form(...),  # noqa: N803
    RelayState: str | None = Form(default=None),  # noqa: N803
    db: AsyncSession = Depends(get_db),
) -> SSOCallbackResponse:
    """SAML Assertion Consumer Service (ACS) endpoint.

    This endpoint receives the SAML response from the Identity Provider
    after successful authentication.

    Args:
        org_id: Organization ID
        SAMLResponse: Base64-encoded SAML response
        RelayState: Optional relay state

    Returns:
        SSO callback response with tokens
    """
    sso_service = get_sso_service(db)
    audit_service = get_audit_service(db)

    try:
        result = await sso_service.process_sso_callback(org_id, SAMLResponse)

        # Log successful SSO login
        await audit_service.log_action(
            organization_id=org_id,
            user_id=result.user_id,
            action=AuditAction.LOGIN,
            resource_type="session",
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"SSO login - {'new user created' if result.is_new_user else 'existing user'}",
        )
        await db.commit()

        return result

    except SAMLValidationError as e:
        logger.error(f"SAML validation failed for org {org_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"SAML validation failed: {e}",
        ) from e
    except ValueError as e:
        logger.error(f"SSO error for org {org_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/acs/{org_id}/redirect", response_class=HTMLResponse)
async def assertion_consumer_service_redirect(
    request: Request,
    org_id: str,
    SAMLResponse: str = Form(...),  # noqa: N803
    RelayState: str | None = Form(default=None),  # noqa: N803
    db: AsyncSession = Depends(get_db),
) -> HTMLResponse:
    """SAML ACS endpoint with HTML redirect response.

    This alternative ACS endpoint returns an HTML page that posts the tokens
    to the frontend application. Useful for browser-based SSO flows.

    Args:
        org_id: Organization ID
        SAMLResponse: Base64-encoded SAML response
        RelayState: URL to redirect to after login

    Returns:
        HTML page with JavaScript redirect
    """
    sso_service = get_sso_service(db)
    audit_service = get_audit_service(db)

    try:
        result = await sso_service.process_sso_callback(org_id, SAMLResponse)

        # Log successful SSO login
        await audit_service.log_action(
            organization_id=org_id,
            user_id=result.user_id,
            action=AuditAction.LOGIN,
            resource_type="session",
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"SSO login - {'new user created' if result.is_new_user else 'existing user'}",
        )
        await db.commit()

        # Default redirect URL
        redirect_url = RelayState or "/"

        # Return HTML that posts tokens to the frontend
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>SSO Authentication Successful</title>
    <script>
        // Store tokens in localStorage
        localStorage.setItem('access_token', '{result.access_token}');
        localStorage.setItem('refresh_token', '{result.refresh_token}');

        // Redirect to application
        window.location.href = '{redirect_url}';
    </script>
</head>
<body>
    <p>Authentication successful. Redirecting...</p>
    <noscript>
        <p>JavaScript is required for SSO login. Please enable JavaScript and try again.</p>
    </noscript>
</body>
</html>
"""
        return HTMLResponse(content=html_content)

    except SAMLValidationError as e:
        logger.error(f"SAML validation failed for org {org_id}: {e}")
        error_html = f"""
<!DOCTYPE html>
<html>
<head><title>SSO Error</title></head>
<body>
    <h1>SSO Authentication Failed</h1>
    <p>Error: {e}</p>
    <p><a href="/">Return to login</a></p>
</body>
</html>
"""
        return HTMLResponse(content=error_html, status_code=400)
    except ValueError as e:
        error_html = f"""
<!DOCTYPE html>
<html>
<head><title>SSO Error</title></head>
<body>
    <h1>SSO Configuration Error</h1>
    <p>Error: {e}</p>
    <p><a href="/">Return to login</a></p>
</body>
</html>
"""
        return HTMLResponse(content=error_html, status_code=400)


@router.get("/status/{org_id}", response_model=SSOStatusResponse)
async def get_sso_status(
    org_id: str,
    db: AsyncSession = Depends(get_db),
) -> SSOStatusResponse:
    """Check SSO status for an organization (public endpoint).

    Args:
        org_id: Organization ID

    Returns:
        SSO status information
    """
    sso_service = get_sso_service(db)
    sso_config = await sso_service.get_sso_config(org_id)

    if not sso_config:
        return SSOStatusResponse(sso_enabled=False)

    return SSOStatusResponse(
        sso_enabled=sso_config.enabled,
        provider=sso_config.provider if sso_config.enabled else None,
        idp_entity_id=sso_config.idp_entity_id if sso_config.enabled else None,
        login_url=f"/api/v1/sso/login/{org_id}" if sso_config.enabled else None,
    )


# ============================================================================
# Admin Endpoints (Authentication Required)
# ============================================================================


@router.post("/configure", response_model=SSOConfigResponse, status_code=status.HTTP_201_CREATED)
async def configure_sso(
    request: Request,
    config_data: SSOConfigCreate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> SSOConfigResponse:
    """Configure SSO for the organization.

    Requires admin privileges. Creates a new SSO configuration for the
    admin's organization.

    Args:
        config_data: SSO configuration data

    Returns:
        Created SSO configuration
    """
    sso_service = get_sso_service(db)
    audit_service = get_audit_service(db)

    try:
        sso_config = await sso_service.create_sso_config(
            current_user.organization_id,
            config_data,
        )

        # Log SSO configuration
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.CONFIG_CHANGE,
            resource_type="sso_config",
            resource_id=sso_config.id,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details=f"SSO configured with provider: {config_data.provider.value}",
        )
        await db.commit()

        return SSOConfigResponse.model_validate(sso_config)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.get("/config", response_model=SSOConfigResponse)
async def get_sso_config(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> SSOConfigResponse:
    """Get SSO configuration for the organization.

    Requires admin privileges.

    Returns:
        SSO configuration
    """
    sso_service = get_sso_service(db)
    sso_config = await sso_service.get_sso_config(current_user.organization_id)

    if not sso_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO is not configured for this organization",
        )

    return SSOConfigResponse.model_validate(sso_config)


@router.put("/config", response_model=SSOConfigResponse)
async def update_sso_config(
    request: Request,
    config_data: SSOConfigUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> SSOConfigResponse:
    """Update SSO configuration.

    Requires admin privileges.

    Args:
        config_data: Updated SSO configuration data

    Returns:
        Updated SSO configuration
    """
    sso_service = get_sso_service(db)
    audit_service = get_audit_service(db)

    try:
        sso_config = await sso_service.update_sso_config(
            current_user.organization_id,
            config_data,
        )

        # Log SSO configuration update
        await audit_service.log_action(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            action=AuditAction.CONFIG_CHANGE,
            resource_type="sso_config",
            resource_id=sso_config.id,
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details="SSO configuration updated",
        )
        await db.commit()

        return SSOConfigResponse.model_validate(sso_config)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        ) from e


@router.delete("/config", status_code=status.HTTP_204_NO_CONTENT)
async def delete_sso_config(
    request: Request,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete (disable) SSO configuration.

    Requires admin privileges. This removes the SSO configuration entirely.
    Users will need to use password-based authentication after this.

    Returns:
        204 No Content on success
    """
    sso_service = get_sso_service(db)
    audit_service = get_audit_service(db)

    deleted = await sso_service.delete_sso_config(current_user.organization_id)

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO is not configured for this organization",
        )

    # Log SSO configuration deletion
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.CONFIG_CHANGE,
        resource_type="sso_config",
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details="SSO configuration deleted",
    )
    await db.commit()


@router.get("/metadata", response_model=SSOMetadataResponse)
async def get_sp_metadata_info(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> SSOMetadataResponse:
    """Get SP metadata information for configuration.

    Requires admin privileges. Returns the SP metadata XML and key
    identifiers needed to configure the Identity Provider.

    Returns:
        SP metadata information
    """
    sso_service = get_sso_service(db)
    sso_config = await sso_service.get_sso_config(current_user.organization_id)

    if not sso_config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="SSO is not configured for this organization",
        )

    metadata_xml = sso_service.generate_sp_metadata(sso_config)

    return SSOMetadataResponse(
        metadata_xml=metadata_xml,
        entity_id=sso_config.sp_entity_id,
        acs_url=sso_config.sp_acs_url,
    )
