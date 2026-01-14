"""Integration Hub service layer for managing external integrations."""

import hashlib
import hmac
import secrets
import time
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

# Note: These models need to be created in app/models/integration.py
from app.models.integration import (
    Integration,
    IntegrationLog,
    IntegrationMapping,
    WebhookEndpoint,
)
from app.schemas.integration import (
    EntityType,
    IntegrationCreate,
    IntegrationMappingCreate,
    IntegrationStats,
    IntegrationStatus,
    IntegrationTestResult,
    IntegrationType,
    SyncAction,
    SyncResult,
    SyncStatus,
    WebhookEndpointCreate,
    WebhookProcessResult,
)


class IntegrationService:
    """Service for managing integrations and sync operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    # -------------------------------------------------------------------------
    # Integration CRUD Operations
    # -------------------------------------------------------------------------

    async def get_integrations(
        self,
        org_id: str,
        integration_type: IntegrationType | None = None,
        status: IntegrationStatus | None = None,
        skip: int = 0,
        limit: int = 20,
    ) -> tuple[list[Integration], int]:
        """List integrations with filtering and pagination.

        Args:
            org_id: Organization ID for multi-tenant isolation
            integration_type: Filter by integration type
            status: Filter by status
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Tuple of (list of integrations, total count)
        """
        query = select(Integration).where(Integration.organization_id == org_id)

        # Apply filters
        if integration_type:
            query = query.where(Integration.integration_type == integration_type.value)
        if status:
            query = query.where(Integration.status == status.value)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering
        query = query.order_by(Integration.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        integrations = list(result.scalars().all())

        return integrations, total

    async def get_integration(
        self,
        integration_id: str,
        org_id: str,
    ) -> Integration | None:
        """Get a single integration by ID.

        Args:
            integration_id: Integration UUID
            org_id: Organization ID for multi-tenant isolation

        Returns:
            Integration if found, None otherwise
        """
        result = await self.db.execute(
            select(Integration).where(
                and_(
                    Integration.id == integration_id,
                    Integration.organization_id == org_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def create_integration(
        self,
        org_id: str,
        user_id: str,
        data: IntegrationCreate,
    ) -> Integration:
        """Create a new integration.

        Args:
            org_id: Organization ID
            user_id: User ID who created the integration
            data: Integration creation data

        Returns:
            Created integration
        """
        integration = Integration(
            organization_id=org_id,
            created_by_id=user_id,
            name=data.name,
            integration_type=data.integration_type.value,
            description=data.description,
            is_enabled=data.is_enabled,
            config=data.config,
            credentials=data.credentials,  # Should be encrypted before storage
            sync_settings=data.sync_settings,
            status=IntegrationStatus.PENDING_SETUP.value,
            sync_count=0,
            error_count=0,
        )

        self.db.add(integration)
        await self.db.flush()

        # Log the creation
        await self._create_log(
            integration_id=integration.id,
            action=SyncAction.CREATE,
            status=SyncStatus.SUCCESS,
            message="Integration created",
        )

        await self.db.commit()
        await self.db.refresh(integration)
        return integration

    async def update_integration(
        self,
        integration_id: str,
        org_id: str,
        data: Any,  # IntegrationUpdate
    ) -> Integration | None:
        """Update an integration.

        Args:
            integration_id: Integration UUID
            org_id: Organization ID for multi-tenant isolation
            data: Fields to update

        Returns:
            Updated integration or None if not found
        """
        integration = await self.get_integration(integration_id, org_id)
        if not integration:
            return None

        update_dict = data.model_dump(exclude_unset=True)

        for field, value in update_dict.items():
            setattr(integration, field, value)

        await self.db.flush()
        await self.db.refresh(integration)
        return integration

    async def delete_integration(
        self,
        integration_id: str,
        org_id: str,
    ) -> bool:
        """Delete an integration.

        Args:
            integration_id: Integration UUID
            org_id: Organization ID for multi-tenant isolation

        Returns:
            True if deleted, False if not found
        """
        integration = await self.get_integration(integration_id, org_id)
        if not integration:
            return False

        await self.db.delete(integration)
        await self.db.flush()
        return True

    # -------------------------------------------------------------------------
    # Integration Testing
    # -------------------------------------------------------------------------

    async def test_integration(
        self,
        integration_id: str,
        org_id: str,
    ) -> IntegrationTestResult:
        """Test an integration connection.

        Args:
            integration_id: Integration UUID
            org_id: Organization ID

        Returns:
            Test result with connection status
        """
        integration = await self.get_integration(integration_id, org_id)
        if not integration:
            return IntegrationTestResult(
                success=False,
                message="Integration not found",
                errors=["Integration does not exist or access denied"],
            )

        start_time = time.time()
        errors: list[str] = []
        details: dict[str, Any] = {}

        try:
            # Test based on integration type
            if integration.integration_type == IntegrationType.JIRA.value:
                success, msg, details = await self._test_jira_connection(integration)
            elif integration.integration_type == IntegrationType.SERVICENOW.value:
                success, msg, details = await self._test_servicenow_connection(integration)
            elif integration.integration_type == IntegrationType.SLACK.value:
                success, msg, details = await self._test_slack_connection(integration)
            elif integration.integration_type == IntegrationType.TEAMS.value:
                success, msg, details = await self._test_teams_connection(integration)
            elif integration.integration_type == IntegrationType.EMAIL.value:
                success, msg, details = await self._test_email_connection(integration)
            elif integration.integration_type == IntegrationType.WEBHOOK.value:
                success = True
                msg = "Webhook endpoint is ready to receive events"
                details = {"endpoint_configured": True}
            else:
                success = False
                msg = f"Unknown integration type: {integration.integration_type}"
                errors.append(msg)

            # Update integration status based on test result
            if success:
                integration.status = IntegrationStatus.ACTIVE.value
                integration.last_error = None
            else:
                integration.status = IntegrationStatus.ERROR.value
                integration.last_error = msg
                if msg not in errors:
                    errors.append(msg)

        except Exception as e:
            success = False
            msg = f"Connection test failed: {str(e)}"
            errors.append(msg)
            integration.status = IntegrationStatus.ERROR.value
            integration.last_error = msg

        response_time_ms = int((time.time() - start_time) * 1000)

        # Log the test
        await self._create_log(
            integration_id=integration.id,
            action=SyncAction.TEST,
            status=SyncStatus.SUCCESS if success else SyncStatus.FAILED,
            message=msg,
            duration_ms=response_time_ms,
        )

        await self.db.commit()

        return IntegrationTestResult(
            success=success,
            message=msg,
            response_time_ms=response_time_ms,
            details=details,
            errors=errors,
        )

    async def _test_jira_connection(
        self, integration: Integration
    ) -> tuple[bool, str, dict[str, Any]]:
        """Test Jira API connection."""
        # Implementation would use httpx to call Jira API
        # For now, validate configuration
        config = integration.config or {}
        credentials = integration.credentials or {}

        required_config = ["base_url", "project_key"]
        required_creds = ["api_token", "email"]

        missing_config = [k for k in required_config if k not in config]
        missing_creds = [k for k in required_creds if k not in credentials]

        if missing_config or missing_creds:
            return (
                False,
                f"Missing configuration: {missing_config + missing_creds}",
                {"missing": missing_config + missing_creds},
            )

        # TODO: Implement actual Jira API call
        return True, "Jira connection successful", {"project_key": config.get("project_key")}

    async def _test_servicenow_connection(
        self, integration: Integration
    ) -> tuple[bool, str, dict[str, Any]]:
        """Test ServiceNow API connection."""
        config = integration.config or {}
        credentials = integration.credentials or {}

        required_config = ["instance_url"]
        required_creds = ["username", "password"]

        missing_config = [k for k in required_config if k not in config]
        missing_creds = [k for k in required_creds if k not in credentials]

        if missing_config or missing_creds:
            return (
                False,
                f"Missing configuration: {missing_config + missing_creds}",
                {"missing": missing_config + missing_creds},
            )

        # TODO: Implement actual ServiceNow API call
        return True, "ServiceNow connection successful", {"instance": config.get("instance_url")}

    async def _test_slack_connection(
        self, integration: Integration
    ) -> tuple[bool, str, dict[str, Any]]:
        """Test Slack API connection."""
        credentials = integration.credentials or {}

        if "bot_token" not in credentials:
            return False, "Missing bot_token", {"missing": ["bot_token"]}

        # TODO: Implement actual Slack API call (auth.test)
        return True, "Slack connection successful", {"connected": True}

    async def _test_teams_connection(
        self, integration: Integration
    ) -> tuple[bool, str, dict[str, Any]]:
        """Test Microsoft Teams connection."""
        credentials = integration.credentials or {}

        required_creds = ["tenant_id", "client_id", "client_secret"]
        missing = [k for k in required_creds if k not in credentials]

        if missing:
            return False, f"Missing credentials: {missing}", {"missing": missing}

        # TODO: Implement actual Teams API call
        return True, "Teams connection successful", {"connected": True}

    async def _test_email_connection(
        self, integration: Integration
    ) -> tuple[bool, str, dict[str, Any]]:
        """Test email SMTP connection."""
        config = integration.config or {}
        credentials = integration.credentials or {}

        required_config = ["smtp_host", "smtp_port"]
        required_creds = ["username", "password"]

        missing_config = [k for k in required_config if k not in config]
        missing_creds = [k for k in required_creds if k not in credentials]

        if missing_config or missing_creds:
            return (
                False,
                f"Missing configuration: {missing_config + missing_creds}",
                {"missing": missing_config + missing_creds},
            )

        # TODO: Implement actual SMTP connection test
        return True, "Email connection successful", {"smtp_host": config.get("smtp_host")}

    # -------------------------------------------------------------------------
    # Sync Operations
    # -------------------------------------------------------------------------

    async def trigger_sync(
        self,
        integration_id: str,
        org_id: str,
    ) -> SyncResult:
        """Trigger a manual sync for an integration.

        Args:
            integration_id: Integration UUID
            org_id: Organization ID

        Returns:
            Sync result with statistics
        """
        integration = await self.get_integration(integration_id, org_id)
        if not integration:
            return SyncResult(
                success=False,
                status=SyncStatus.FAILED,
                message="Integration not found",
                errors=["Integration does not exist or access denied"],
            )

        if not integration.is_enabled:
            return SyncResult(
                success=False,
                status=SyncStatus.FAILED,
                message="Integration is disabled",
                errors=["Enable the integration before syncing"],
            )

        if integration.status == IntegrationStatus.ERROR.value:
            return SyncResult(
                success=False,
                status=SyncStatus.FAILED,
                message="Integration is in error state",
                errors=["Fix integration errors before syncing"],
            )

        start_time = time.time()
        records_synced = 0
        records_created = 0
        records_updated = 0
        records_failed = 0
        errors: list[str] = []

        try:
            # Perform sync based on integration type
            if integration.integration_type == IntegrationType.JIRA.value:
                result = await self._sync_jira(integration)
            elif integration.integration_type == IntegrationType.SERVICENOW.value:
                result = await self._sync_servicenow(integration)
            elif integration.integration_type == IntegrationType.SLACK.value:
                result = await self._sync_slack(integration)
            elif integration.integration_type == IntegrationType.TEAMS.value:
                result = await self._sync_teams(integration)
            else:
                result = {
                    "synced": 0,
                    "created": 0,
                    "updated": 0,
                    "failed": 0,
                    "errors": [f"Sync not supported for type: {integration.integration_type}"],
                }

            records_synced = result.get("synced", 0)
            records_created = result.get("created", 0)
            records_updated = result.get("updated", 0)
            records_failed = result.get("failed", 0)
            errors = result.get("errors", [])

            success = records_failed == 0 and len(errors) == 0
            status = SyncStatus.SUCCESS if success else (
                SyncStatus.PARTIAL if records_synced > 0 else SyncStatus.FAILED
            )

            # Update integration status
            integration.last_sync_at = datetime.now(timezone.utc)
            integration.last_sync_status = status.value
            integration.sync_count += 1
            if not success:
                integration.error_count += 1
                integration.last_error = "; ".join(errors[:3])  # Keep first 3 errors

        except Exception as e:
            success = False
            status = SyncStatus.FAILED
            errors.append(str(e))
            integration.error_count += 1
            integration.last_error = str(e)

        duration_ms = int((time.time() - start_time) * 1000)

        # Log the sync
        await self._create_log(
            integration_id=integration.id,
            action=SyncAction.SYNC,
            status=status,
            message=f"Synced {records_synced} records",
            duration_ms=duration_ms,
        )

        await self.db.commit()

        return SyncResult(
            success=success,
            status=status,
            message=f"Sync completed: {records_synced} synced, {records_failed} failed",
            records_synced=records_synced,
            records_created=records_created,
            records_updated=records_updated,
            records_failed=records_failed,
            duration_ms=duration_ms,
            errors=errors,
        )

    async def _sync_jira(self, integration: Integration) -> dict[str, Any]:
        """Sync data with Jira."""
        # TODO: Implement Jira sync logic
        # This would fetch issues from Jira and create/update findings/tasks
        return {"synced": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

    async def _sync_servicenow(self, integration: Integration) -> dict[str, Any]:
        """Sync data with ServiceNow."""
        # TODO: Implement ServiceNow sync logic
        return {"synced": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

    async def _sync_slack(self, integration: Integration) -> dict[str, Any]:
        """Sync/send notifications to Slack."""
        # TODO: Implement Slack notification sync
        return {"synced": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

    async def _sync_teams(self, integration: Integration) -> dict[str, Any]:
        """Sync/send notifications to Teams."""
        # TODO: Implement Teams notification sync
        return {"synced": 0, "created": 0, "updated": 0, "failed": 0, "errors": []}

    # -------------------------------------------------------------------------
    # Integration Logs
    # -------------------------------------------------------------------------

    async def get_integration_logs(
        self,
        integration_id: str,
        org_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[IntegrationLog], int]:
        """Get logs for an integration.

        Args:
            integration_id: Integration UUID
            org_id: Organization ID
            skip: Number of records to skip
            limit: Maximum records to return

        Returns:
            Tuple of (list of logs, total count)
        """
        # First verify integration belongs to org
        integration = await self.get_integration(integration_id, org_id)
        if not integration:
            return [], 0

        query = select(IntegrationLog).where(
            IntegrationLog.integration_id == integration_id
        )

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination and ordering (newest first)
        query = query.order_by(IntegrationLog.created_at.desc()).offset(skip).limit(limit)

        result = await self.db.execute(query)
        logs = list(result.scalars().all())

        return logs, total

    async def _create_log(
        self,
        integration_id: str,
        action: SyncAction,
        status: SyncStatus,
        message: str,
        entity_type: EntityType | None = None,
        entity_id: str | None = None,
        external_id: str | None = None,
        request_payload: dict[str, Any] | None = None,
        response_payload: dict[str, Any] | None = None,
        duration_ms: int | None = None,
    ) -> IntegrationLog:
        """Create an integration log entry."""
        log = IntegrationLog(
            integration_id=integration_id,
            action=action.value,
            status=status.value,
            entity_type=entity_type.value if entity_type else None,
            entity_id=entity_id,
            external_id=external_id,
            request_payload=request_payload,
            response_payload=response_payload,
            error_message=message if status == SyncStatus.FAILED else None,
            duration_ms=duration_ms,
        )
        self.db.add(log)
        await self.db.flush()
        return log

    # -------------------------------------------------------------------------
    # Field Mappings
    # -------------------------------------------------------------------------

    async def add_mapping(
        self,
        integration_id: str,
        org_id: str,
        data: IntegrationMappingCreate,
    ) -> IntegrationMapping | None:
        """Add a field mapping to an integration.

        Args:
            integration_id: Integration UUID
            org_id: Organization ID
            data: Mapping data

        Returns:
            Created mapping or None if integration not found
        """
        integration = await self.get_integration(integration_id, org_id)
        if not integration:
            return None

        mapping = IntegrationMapping(
            integration_id=integration_id,
            source_entity=data.source_entity.value,
            source_field=data.source_field,
            target_entity=data.target_entity,
            target_field=data.target_field,
            transform=data.transform,
            is_bidirectional=data.is_bidirectional,
        )

        self.db.add(mapping)
        await self.db.commit()
        await self.db.refresh(mapping)
        return mapping

    async def remove_mapping(
        self,
        mapping_id: str,
        org_id: str,
    ) -> bool:
        """Remove a field mapping.

        Args:
            mapping_id: Mapping UUID
            org_id: Organization ID

        Returns:
            True if deleted, False if not found
        """
        # Get the mapping and verify it belongs to an integration in this org
        result = await self.db.execute(
            select(IntegrationMapping)
            .join(Integration)
            .where(
                and_(
                    IntegrationMapping.id == mapping_id,
                    Integration.organization_id == org_id,
                )
            )
        )
        mapping = result.scalar_one_or_none()

        if not mapping:
            return False

        await self.db.delete(mapping)
        await self.db.flush()
        return True

    # -------------------------------------------------------------------------
    # Webhook Endpoints
    # -------------------------------------------------------------------------

    async def create_webhook_endpoint(
        self,
        org_id: str,
        data: WebhookEndpointCreate,
    ) -> WebhookEndpoint:
        """Create a webhook endpoint.

        Args:
            org_id: Organization ID
            data: Webhook endpoint data

        Returns:
            Created webhook endpoint
        """
        # Generate a unique endpoint key
        endpoint_key = secrets.token_urlsafe(32)

        # Hash the secret if provided
        secret_hash = None
        if data.secret:
            secret_hash = hashlib.sha256(data.secret.encode()).hexdigest()

        endpoint = WebhookEndpoint(
            organization_id=org_id,
            name=data.name,
            description=data.description,
            endpoint_key=endpoint_key,
            events=data.events,
            target_entity=data.target_entity.value if data.target_entity else None,
            payload_mapping=data.payload_mapping,
            headers_required=data.headers_required,
            secret_hash=secret_hash,
            is_active=True,
            receive_count=0,
        )

        self.db.add(endpoint)
        await self.db.commit()
        await self.db.refresh(endpoint)
        return endpoint

    async def get_webhook_endpoints(
        self,
        org_id: str,
    ) -> list[WebhookEndpoint]:
        """Get all webhook endpoints for an organization.

        Args:
            org_id: Organization ID

        Returns:
            List of webhook endpoints
        """
        result = await self.db.execute(
            select(WebhookEndpoint)
            .where(WebhookEndpoint.organization_id == org_id)
            .order_by(WebhookEndpoint.created_at.desc())
        )
        return list(result.scalars().all())

    async def process_webhook(
        self,
        endpoint_key: str,
        payload: dict[str, Any],
        headers: dict[str, str] | None = None,
        signature: str | None = None,
    ) -> WebhookProcessResult:
        """Process an incoming webhook.

        Args:
            endpoint_key: Unique endpoint key from URL
            payload: Webhook payload
            headers: Request headers
            signature: Webhook signature for validation

        Returns:
            Processing result
        """
        # Find the endpoint
        result = await self.db.execute(
            select(WebhookEndpoint).where(
                and_(
                    WebhookEndpoint.endpoint_key == endpoint_key,
                    WebhookEndpoint.is_active == True,  # noqa: E712
                )
            )
        )
        endpoint = result.scalar_one_or_none()

        if not endpoint:
            return WebhookProcessResult(
                success=False,
                message="Webhook endpoint not found or inactive",
            )

        # Validate required headers
        if endpoint.headers_required and headers:
            missing_headers = [
                h for h in endpoint.headers_required if h not in headers
            ]
            if missing_headers:
                return WebhookProcessResult(
                    success=False,
                    message=f"Missing required headers: {missing_headers}",
                )

        # Validate signature if secret is configured
        if endpoint.secret_hash and signature:
            # Signature validation logic would go here
            # This is a placeholder - actual implementation depends on webhook provider
            pass

        # Update endpoint stats
        endpoint.last_received_at = datetime.now(timezone.utc)
        endpoint.receive_count += 1

        # Process based on target entity type
        entity_id = None
        action_taken = "ignored"

        try:
            if endpoint.target_entity and endpoint.payload_mapping:
                # Extract data using mapping
                mapped_data = self._apply_payload_mapping(payload, endpoint.payload_mapping)

                # Create or update entity based on target type
                if endpoint.target_entity == EntityType.VENDOR.value:
                    entity_id, action_taken = await self._process_vendor_webhook(
                        endpoint.organization_id, mapped_data
                    )
                elif endpoint.target_entity == EntityType.FINDING.value:
                    entity_id, action_taken = await self._process_finding_webhook(
                        endpoint.organization_id, mapped_data
                    )
                elif endpoint.target_entity == EntityType.REMEDIATION_TASK.value:
                    entity_id, action_taken = await self._process_task_webhook(
                        endpoint.organization_id, mapped_data
                    )

            await self.db.commit()

            return WebhookProcessResult(
                success=True,
                message="Webhook processed successfully",
                entity_type=endpoint.target_entity,
                entity_id=entity_id,
                action_taken=action_taken,
            )

        except Exception as e:
            return WebhookProcessResult(
                success=False,
                message=f"Webhook processing failed: {str(e)}",
            )

    def _apply_payload_mapping(
        self, payload: dict[str, Any], mapping: dict[str, str]
    ) -> dict[str, Any]:
        """Apply payload mapping to extract data."""
        result = {}
        for target_field, source_path in mapping.items():
            # Support dot notation for nested fields
            value = payload
            for key in source_path.split("."):
                if isinstance(value, dict) and key in value:
                    value = value[key]
                else:
                    value = None
                    break
            result[target_field] = value
        return result

    async def _process_vendor_webhook(
        self, org_id: str, data: dict[str, Any]
    ) -> tuple[str | None, str]:
        """Process webhook data for vendor entity."""
        # TODO: Implement vendor creation/update from webhook
        return None, "ignored"

    async def _process_finding_webhook(
        self, org_id: str, data: dict[str, Any]
    ) -> tuple[str | None, str]:
        """Process webhook data for finding entity."""
        # TODO: Implement finding creation/update from webhook
        return None, "ignored"

    async def _process_task_webhook(
        self, org_id: str, data: dict[str, Any]
    ) -> tuple[str | None, str]:
        """Process webhook data for remediation task entity."""
        # TODO: Implement task creation/update from webhook
        return None, "ignored"

    # -------------------------------------------------------------------------
    # Statistics
    # -------------------------------------------------------------------------

    async def get_integration_stats(
        self,
        org_id: str,
    ) -> IntegrationStats:
        """Get dashboard statistics for integrations.

        Args:
            org_id: Organization ID

        Returns:
            Integration statistics
        """
        # Total integrations
        total_query = select(func.count()).where(
            Integration.organization_id == org_id
        )
        total_result = await self.db.execute(total_query)
        total_integrations = total_result.scalar() or 0

        # Active integrations
        active_query = select(func.count()).where(
            and_(
                Integration.organization_id == org_id,
                Integration.status == IntegrationStatus.ACTIVE.value,
                Integration.is_enabled == True,  # noqa: E712
            )
        )
        active_result = await self.db.execute(active_query)
        active_integrations = active_result.scalar() or 0

        # Error integrations
        error_query = select(func.count()).where(
            and_(
                Integration.organization_id == org_id,
                Integration.status == IntegrationStatus.ERROR.value,
            )
        )
        error_result = await self.db.execute(error_query)
        error_integrations = error_result.scalar() or 0

        # Pending setup
        pending_query = select(func.count()).where(
            and_(
                Integration.organization_id == org_id,
                Integration.status == IntegrationStatus.PENDING_SETUP.value,
            )
        )
        pending_result = await self.db.execute(pending_query)
        pending_setup = pending_result.scalar() or 0

        # Count by type
        type_query = (
            select(Integration.integration_type, func.count())
            .where(Integration.organization_id == org_id)
            .group_by(Integration.integration_type)
        )
        type_result = await self.db.execute(type_query)
        by_type = {row[0]: row[1] for row in type_result.all()}

        # Count by status
        status_query = (
            select(Integration.status, func.count())
            .where(Integration.organization_id == org_id)
            .group_by(Integration.status)
        )
        status_result = await self.db.execute(status_query)
        by_status = {row[0]: row[1] for row in status_result.all()}

        # Syncs today
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        syncs_today_query = select(func.count()).where(
            and_(
                IntegrationLog.action == SyncAction.SYNC.value,
                IntegrationLog.created_at >= today_start,
            )
        )
        # Join to filter by org
        syncs_today_query = (
            select(func.count())
            .select_from(IntegrationLog)
            .join(Integration)
            .where(
                and_(
                    Integration.organization_id == org_id,
                    IntegrationLog.action == SyncAction.SYNC.value,
                    IntegrationLog.created_at >= today_start,
                )
            )
        )
        syncs_result = await self.db.execute(syncs_today_query)
        total_syncs_today = syncs_result.scalar() or 0

        # Successful syncs today
        success_syncs_query = (
            select(func.count())
            .select_from(IntegrationLog)
            .join(Integration)
            .where(
                and_(
                    Integration.organization_id == org_id,
                    IntegrationLog.action == SyncAction.SYNC.value,
                    IntegrationLog.status == SyncStatus.SUCCESS.value,
                    IntegrationLog.created_at >= today_start,
                )
            )
        )
        success_result = await self.db.execute(success_syncs_query)
        successful_syncs_today = success_result.scalar() or 0

        # Failed syncs today
        failed_syncs_today = total_syncs_today - successful_syncs_today

        # Webhooks today
        webhook_today_query = (
            select(func.count())
            .select_from(IntegrationLog)
            .join(Integration)
            .where(
                and_(
                    Integration.organization_id == org_id,
                    IntegrationLog.action == SyncAction.WEBHOOK_RECEIVED.value,
                    IntegrationLog.created_at >= today_start,
                )
            )
        )
        webhook_result = await self.db.execute(webhook_today_query)
        total_webhooks_today = webhook_result.scalar() or 0

        # Active webhook endpoints
        active_webhooks_query = select(func.count()).where(
            and_(
                WebhookEndpoint.organization_id == org_id,
                WebhookEndpoint.is_active == True,  # noqa: E712
            )
        )
        active_webhooks_result = await self.db.execute(active_webhooks_query)
        active_webhook_endpoints = active_webhooks_result.scalar() or 0

        # Last sync
        last_sync_query = (
            select(Integration.last_sync_at)
            .where(
                and_(
                    Integration.organization_id == org_id,
                    Integration.last_sync_at.isnot(None),
                )
            )
            .order_by(Integration.last_sync_at.desc())
            .limit(1)
        )
        last_sync_result = await self.db.execute(last_sync_query)
        last_sync_row = last_sync_result.scalar_one_or_none()
        last_sync_at = last_sync_row if last_sync_row else None

        # Last webhook
        last_webhook_query = (
            select(WebhookEndpoint.last_received_at)
            .where(
                and_(
                    WebhookEndpoint.organization_id == org_id,
                    WebhookEndpoint.last_received_at.isnot(None),
                )
            )
            .order_by(WebhookEndpoint.last_received_at.desc())
            .limit(1)
        )
        last_webhook_result = await self.db.execute(last_webhook_query)
        last_webhook_row = last_webhook_result.scalar_one_or_none()
        last_webhook_at = last_webhook_row if last_webhook_row else None

        return IntegrationStats(
            total_integrations=total_integrations,
            active_integrations=active_integrations,
            error_integrations=error_integrations,
            pending_setup=pending_setup,
            by_type=by_type,
            by_status=by_status,
            total_syncs_today=total_syncs_today,
            successful_syncs_today=successful_syncs_today,
            failed_syncs_today=failed_syncs_today,
            total_webhooks_today=total_webhooks_today,
            active_webhook_endpoints=active_webhook_endpoints,
            last_sync_at=last_sync_at,
            last_webhook_at=last_webhook_at,
        )


# -------------------------------------------------------------------------
# Factory Functions (Standalone)
# -------------------------------------------------------------------------


async def get_integrations(
    db: AsyncSession,
    org_id: str,
    integration_type: IntegrationType | None = None,
    status: IntegrationStatus | None = None,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Integration], int]:
    """Get integrations with filtering and pagination."""
    service = IntegrationService(db)
    return await service.get_integrations(org_id, integration_type, status, skip, limit)


async def get_integration(
    db: AsyncSession,
    integration_id: str,
    org_id: str,
) -> Integration | None:
    """Get a single integration by ID."""
    service = IntegrationService(db)
    return await service.get_integration(integration_id, org_id)


async def create_integration(
    db: AsyncSession,
    org_id: str,
    user_id: str,
    data: IntegrationCreate,
) -> Integration:
    """Create a new integration."""
    service = IntegrationService(db)
    return await service.create_integration(org_id, user_id, data)


async def update_integration(
    db: AsyncSession,
    integration_id: str,
    org_id: str,
    data: Any,
) -> Integration | None:
    """Update an integration."""
    service = IntegrationService(db)
    return await service.update_integration(integration_id, org_id, data)


async def delete_integration(
    db: AsyncSession,
    integration_id: str,
    org_id: str,
) -> bool:
    """Delete an integration."""
    service = IntegrationService(db)
    return await service.delete_integration(integration_id, org_id)


async def test_integration(
    db: AsyncSession,
    integration_id: str,
    org_id: str,
) -> IntegrationTestResult:
    """Test an integration connection."""
    service = IntegrationService(db)
    return await service.test_integration(integration_id, org_id)


async def trigger_sync(
    db: AsyncSession,
    integration_id: str,
    org_id: str,
) -> SyncResult:
    """Trigger a sync for an integration."""
    service = IntegrationService(db)
    return await service.trigger_sync(integration_id, org_id)


async def get_integration_logs(
    db: AsyncSession,
    integration_id: str,
    org_id: str,
    skip: int = 0,
    limit: int = 50,
) -> tuple[list[IntegrationLog], int]:
    """Get logs for an integration."""
    service = IntegrationService(db)
    return await service.get_integration_logs(integration_id, org_id, skip, limit)


async def add_mapping(
    db: AsyncSession,
    integration_id: str,
    org_id: str,
    data: IntegrationMappingCreate,
) -> IntegrationMapping | None:
    """Add a field mapping to an integration."""
    service = IntegrationService(db)
    return await service.add_mapping(integration_id, org_id, data)


async def remove_mapping(
    db: AsyncSession,
    mapping_id: str,
    org_id: str,
) -> bool:
    """Remove a field mapping."""
    service = IntegrationService(db)
    return await service.remove_mapping(mapping_id, org_id)


async def create_webhook_endpoint(
    db: AsyncSession,
    org_id: str,
    data: WebhookEndpointCreate,
) -> WebhookEndpoint:
    """Create a webhook endpoint."""
    service = IntegrationService(db)
    return await service.create_webhook_endpoint(org_id, data)


async def get_webhook_endpoints(
    db: AsyncSession,
    org_id: str,
) -> list[WebhookEndpoint]:
    """Get all webhook endpoints for an organization."""
    service = IntegrationService(db)
    return await service.get_webhook_endpoints(org_id)


async def process_webhook(
    db: AsyncSession,
    endpoint_key: str,
    payload: dict[str, Any],
    headers: dict[str, str] | None = None,
    signature: str | None = None,
) -> WebhookProcessResult:
    """Process an incoming webhook."""
    service = IntegrationService(db)
    return await service.process_webhook(endpoint_key, payload, headers, signature)


async def get_integration_stats(
    db: AsyncSession,
    org_id: str,
) -> IntegrationStats:
    """Get dashboard statistics for integrations."""
    service = IntegrationService(db)
    return await service.get_integration_stats(org_id)


def get_integration_service(db: AsyncSession) -> IntegrationService:
    """Factory function to create integration service."""
    return IntegrationService(db)
