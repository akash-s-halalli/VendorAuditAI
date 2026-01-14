"""Integration Hub API endpoints.

Provides endpoints for managing third-party integrations, field mappings,
sync operations, webhooks, and integration statistics.

IMPORTANT: Route ordering matters in FastAPI! Static routes must come BEFORE
parameterized routes to prevent incorrect matching. E.g., /stats must come
before /{integration_id} or "stats" will be treated as an integration_id.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.integration import (
    IntegrationMappingCreate,
    IntegrationMappingResponse,
    IntegrationCreate,
    IntegrationDetailResponse,
    IntegrationListResponse,
    IntegrationResponse,
    IntegrationStats,
    IntegrationUpdate,
    IntegrationLogListResponse,
    IntegrationLogResponse,
    SyncResult,
    IntegrationTestResult,
    WebhookEndpointCreate,
    WebhookEndpointResponse,
    WebhookProcessResult,
)
from app.services import integration as integration_service

router = APIRouter(tags=["Integration Hub"])


# ============================================================================
# Helper Functions
# ============================================================================


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
# STATIC ROUTES - Must come BEFORE parameterized routes
# ============================================================================


@router.get("/", response_model=IntegrationListResponse)
async def list_integrations(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    integration_type: str | None = Query(None, description="Filter by integration type (e.g., 'erp', 'crm', 'grc')"),
    status: str | None = Query(None, description="Filter by status (e.g., 'active', 'inactive', 'error')"),
    search: str | None = Query(None, description="Search by name"),
) -> IntegrationListResponse:
    """
    List all integrations for the current user's organization.

    Supports pagination, filtering by type/status, and search by name.
    Returns basic integration information without detailed mappings.
    """
    skip = (page - 1) * limit
    integrations, total = await integration_service.get_integrations(
        db=db,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        integration_type=integration_type,
        status=status,
        search=search,
    )

    return IntegrationListResponse(
        data=[IntegrationResponse.model_validate(i) for i in integrations],
        total=total,
        page=page,
        limit=limit,
    )


@router.get("/stats", response_model=IntegrationStats)
async def get_integration_stats(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IntegrationStats:
    """
    Get integration statistics for the organization dashboard.

    Returns aggregated metrics including:
    - Total integrations by status
    - Sync success/failure rates
    - Records synchronized
    - Last sync times
    - Webhook delivery stats
    """
    stats = await integration_service.get_integration_stats(
        db=db,
        org_id=current_user.organization_id,
    )

    return IntegrationStats.model_validate(stats)


@router.post("/", response_model=IntegrationResponse, status_code=status.HTTP_201_CREATED)
async def create_integration(
    request: Request,
    integration_data: IntegrationCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IntegrationResponse:
    """
    Create a new integration for the current user's organization.

    Validates the integration configuration and credentials.
    Does not automatically test the connection - use the test endpoint.
    """
    try:
        integration = await integration_service.create_integration(
            db=db,
            org_id=current_user.organization_id,
            user_id=current_user.id,
            integration_data=integration_data,
        )

        return IntegrationResponse.model_validate(integration)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Webhook Endpoints (Static paths - must come before /{integration_id})
# ============================================================================


@router.get("/webhooks", response_model=list[WebhookEndpointResponse])
async def list_webhook_endpoints(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    integration_id: str | None = Query(None, description="Filter by integration ID"),
) -> list[WebhookEndpointResponse]:
    """
    List all webhook endpoints for the organization.

    Webhook endpoints allow external systems to push data
    to VendorAuditAI in real-time.
    """
    skip = (page - 1) * limit
    webhooks, total = await integration_service.get_webhook_endpoints(
        db=db,
        org_id=current_user.organization_id,
        skip=skip,
        limit=limit,
        integration_id=integration_id,
    )

    return [WebhookEndpointResponse.model_validate(w) for w in webhooks]


@router.post("/webhooks", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook_endpoint(
    webhook_data: WebhookEndpointCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> WebhookEndpointResponse:
    """
    Create a new webhook endpoint.

    Returns a unique endpoint URL and secret key for webhook
    verification. The secret should be stored securely by the
    external system for signing webhook payloads.
    """
    try:
        webhook = await integration_service.create_webhook_endpoint(
            db=db,
            org_id=current_user.organization_id,
            user_id=current_user.id,
            webhook_data=webhook_data,
        )

        return WebhookEndpointResponse.model_validate(webhook)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_endpoint(
    webhook_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete a webhook endpoint.

    External systems will no longer be able to send data to
    this endpoint. Any pending webhook deliveries will fail.
    """
    webhook = await integration_service.get_webhook_endpoint_by_id(
        db=db,
        webhook_id=webhook_id,
        org_id=current_user.organization_id,
    )

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found",
        )

    await integration_service.delete_webhook_endpoint(
        db=db,
        webhook=webhook,
    )


@router.post("/webhooks/{endpoint_key}/receive")
async def receive_webhook(
    endpoint_key: str,
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict:
    """
    Receive webhook payload from external system.

    This endpoint does NOT require authentication as it is called
    by external systems. Instead, it validates the webhook signature
    using the shared secret.

    The endpoint_key is a unique identifier for the webhook endpoint,
    not the webhook ID. This provides an additional layer of security.
    """
    # Get webhook endpoint by key (not authenticated)
    webhook = await integration_service.get_webhook_endpoint_by_key(
        db=db,
        endpoint_key=endpoint_key,
    )

    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found",
        )

    if not webhook.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Webhook endpoint is not active",
        )

    # Get raw body for signature verification
    body = await request.body()

    # Verify webhook signature if required
    signature = request.headers.get("X-Webhook-Signature")
    timestamp = request.headers.get("X-Webhook-Timestamp")

    try:
        # Validate signature if provided
        if signature:
            is_valid = await integration_service.verify_webhook_signature(
                webhook=webhook,
                payload=body,
                signature=signature,
                timestamp=timestamp,
            )

            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid webhook signature",
                )

        # Parse and process the payload
        payload = await request.json()

        result = await integration_service.process_webhook_payload(
            db=db,
            webhook=webhook,
            payload=payload,
            headers=dict(request.headers),
            source_ip=_get_client_ip(request),
        )

        return {
            "status": "accepted",
            "message": "Webhook payload received and queued for processing",
            "webhook_id": webhook.id,
            "processing_id": result.processing_id,
        }

    except HTTPException:
        raise
    except Exception as e:
        # Log the error but return a generic message
        await integration_service.log_webhook_error(
            db=db,
            webhook_id=webhook.id,
            error=str(e),
            payload=body.decode("utf-8") if body else None,
        )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to process webhook payload",
        ) from e


# ============================================================================
# Mapping Delete (Static path with /mappings/ prefix)
# ============================================================================


@router.delete("/mappings/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_field_mapping(
    mapping_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Remove a field mapping.

    Future syncs will no longer include this field mapping.
    Does not affect previously synchronized data.
    """
    mapping = await integration_service.get_field_mapping_by_id(
        db=db,
        mapping_id=mapping_id,
        org_id=current_user.organization_id,
    )

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field mapping not found",
        )

    await integration_service.delete_field_mapping(
        db=db,
        mapping=mapping,
    )


# ============================================================================
# PARAMETERIZED ROUTES - Must come AFTER all static routes
# ============================================================================


@router.get("/{integration_id}", response_model=IntegrationDetailResponse)
async def get_integration(
    integration_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IntegrationDetailResponse:
    """
    Get a specific integration by ID with all field mappings.

    Returns complete integration details including configuration,
    credentials (masked), and all associated field mappings.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
        include_mappings=True,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    return IntegrationDetailResponse.model_validate(integration)


@router.put("/{integration_id}", response_model=IntegrationResponse)
async def update_integration(
    request: Request,
    integration_id: str,
    integration_data: IntegrationUpdate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IntegrationResponse:
    """
    Update an existing integration's configuration.

    Only provided fields will be updated. Credentials can be
    updated separately to avoid accidental overwrites.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    try:
        updated = await integration_service.update_integration(
            db=db,
            integration=integration,
            integration_data=integration_data,
            user_id=current_user.id,
        )

        return IntegrationResponse.model_validate(updated)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.delete("/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_integration(
    request: Request,
    integration_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> None:
    """
    Delete an integration and all associated data.

    This will also delete all field mappings, sync logs, and
    webhook endpoints associated with this integration.
    Warning: This action cannot be undone.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    await integration_service.delete_integration(
        db=db,
        integration=integration,
        user_id=current_user.id,
    )


# ============================================================================
# Integration Action Endpoints (Parameterized)
# ============================================================================


@router.post("/{integration_id}/test", response_model=IntegrationTestResult)
async def test_integration_connection(
    integration_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IntegrationTestResult:
    """
    Test the connection to an external integration.

    Validates credentials and connectivity without performing
    any data synchronization. Updates the integration status
    based on the test result.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    try:
        result = await integration_service.test_connection(
            db=db,
            integration=integration,
        )

        return IntegrationTestResult(
            success=result.success,
            message=result.message,
            response_time_ms=result.response_time_ms if hasattr(result, "response_time_ms") else None,
            details=result.details if hasattr(result, "details") else {},
            tested_at=result.tested_at if hasattr(result, "tested_at") else None,
        )
    except Exception as e:
        return IntegrationTestResult(
            success=False,
            message=f"Connection test failed: {str(e)}",
            response_time_ms=None,
            details={"error": str(e)},
        )


@router.post("/{integration_id}/sync", response_model=SyncResult)
async def trigger_manual_sync(
    integration_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    full_sync: bool = Query(False, description="Perform full sync instead of incremental"),
) -> SyncResult:
    """
    Trigger a manual data synchronization for an integration.

    By default performs an incremental sync (only changed data).
    Set full_sync=true to synchronize all data from scratch.

    Returns immediately with a sync job ID. Use the logs endpoint
    to monitor sync progress.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    if integration.status != "active":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Integration is not active (current status: {integration.status})",
        )

    try:
        result = await integration_service.trigger_sync(
            db=db,
            integration=integration,
            user_id=current_user.id,
            full_sync=full_sync,
        )

        # Service returns a SyncResult-compatible object
        return SyncResult.model_validate(result) if hasattr(result, "model_validate") else result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Field Mapping Endpoints (Parameterized)
# ============================================================================


@router.get("/{integration_id}/mappings", response_model=list[IntegrationMappingResponse])
async def list_field_mappings(
    integration_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(50, ge=1, le=200, description="Items per page"),
) -> list[IntegrationMappingResponse]:
    """
    List all field mappings for an integration.

    Field mappings define how external system fields map to
    VendorAuditAI fields for data synchronization.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    skip = (page - 1) * limit
    mappings, total = await integration_service.get_field_mappings(
        db=db,
        integration_id=integration_id,
        skip=skip,
        limit=limit,
    )

    return [IntegrationMappingResponse.model_validate(m) for m in mappings]


@router.post("/{integration_id}/mappings", response_model=IntegrationMappingResponse, status_code=status.HTTP_201_CREATED)
async def create_field_mapping(
    integration_id: str,
    mapping_data: IntegrationMappingCreate,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IntegrationMappingResponse:
    """
    Add a new field mapping to an integration.

    Defines how a field from the external system maps to a
    VendorAuditAI field. Supports transformation rules and
    default values.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    try:
        mapping = await integration_service.create_field_mapping(
            db=db,
            integration_id=integration_id,
            mapping_data=mapping_data,
        )

        return IntegrationMappingResponse.model_validate(mapping)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


# ============================================================================
# Sync Log Endpoints (Parameterized)
# ============================================================================


@router.get("/{integration_id}/logs", response_model=IntegrationLogListResponse)
async def get_sync_logs(
    integration_id: str,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    status: str | None = Query(None, description="Filter by status (e.g., 'completed', 'failed', 'running')"),
) -> IntegrationLogListResponse:
    """
    Get paginated sync logs for an integration.

    Shows history of all synchronization operations including
    status, records processed, errors, and timing information.
    """
    integration = await integration_service.get_integration_by_id(
        db=db,
        integration_id=integration_id,
        org_id=current_user.organization_id,
    )

    if not integration:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Integration not found",
        )

    skip = (page - 1) * limit
    logs, total = await integration_service.get_sync_logs(
        db=db,
        integration_id=integration_id,
        skip=skip,
        limit=limit,
        status=status,
    )

    return IntegrationLogListResponse(
        data=[IntegrationLogResponse.model_validate(log) for log in logs],
        total=total,
        page=page,
        limit=limit,
    )
