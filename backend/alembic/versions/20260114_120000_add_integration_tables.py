"""Add integration hub tables.

Revision ID: 20260114_120000
Revises: 20260114_110000
Create Date: 2026-01-14
"""
from alembic import op
import sqlalchemy as sa

revision = "20260114_120000"
down_revision = "20260114_110000"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create integrations table
    op.create_table(
        "integrations",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_by_id", sa.String(36), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=False),
        sa.Column("integration_type", sa.String(50), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("config", sa.JSON, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="pending_setup"),
        sa.Column("last_sync_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text, nullable=True),
        sa.Column("error_count", sa.Integer, nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for integrations
    op.create_index("ix_integrations_organization_id", "integrations", ["organization_id"])
    op.create_index("ix_integrations_integration_type", "integrations", ["integration_type"])
    op.create_index("ix_integrations_status", "integrations", ["status"])

    # 2. Create integration_mappings table
    op.create_table(
        "integration_mappings",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("integration_id", sa.String(36), sa.ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=False),
        sa.Column("local_field", sa.String(255), nullable=False),
        sa.Column("remote_field", sa.String(255), nullable=False),
        sa.Column("transform", sa.String(255), nullable=True),
        sa.Column("is_bidirectional", sa.Boolean, nullable=False, default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for integration_mappings
    op.create_index("ix_integration_mappings_integration_id", "integration_mappings", ["integration_id"])
    op.create_index("ix_integration_mappings_entity_type", "integration_mappings", ["entity_type"])

    # 3. Create integration_logs table
    op.create_table(
        "integration_logs",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("integration_id", sa.String(36), sa.ForeignKey("integrations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(100), nullable=True),
        sa.Column("entity_id", sa.String(36), nullable=True),
        sa.Column("request_data", sa.JSON, nullable=True),
        sa.Column("response_data", sa.JSON, nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Create indexes for integration_logs
    op.create_index("ix_integration_logs_integration_id", "integration_logs", ["integration_id"])
    op.create_index("ix_integration_logs_action", "integration_logs", ["action"])
    op.create_index("ix_integration_logs_status", "integration_logs", ["status"])
    op.create_index("ix_integration_logs_created_at", "integration_logs", ["created_at"])

    # 4. Create webhook_endpoints table
    op.create_table(
        "webhook_endpoints",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("integration_id", sa.String(36), sa.ForeignKey("integrations.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("endpoint_key", sa.String(64), nullable=False, unique=True),
        sa.Column("secret", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, default=True),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("trigger_count", sa.Integer, nullable=False, default=0),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for webhook_endpoints
    op.create_index("ix_webhook_endpoints_organization_id", "webhook_endpoints", ["organization_id"])
    op.create_index("ix_webhook_endpoints_integration_id", "webhook_endpoints", ["integration_id"])
    op.create_index("ix_webhook_endpoints_endpoint_key", "webhook_endpoints", ["endpoint_key"])
    op.create_index("ix_webhook_endpoints_is_active", "webhook_endpoints", ["is_active"])


def downgrade():
    # Drop tables in reverse order (respecting foreign key dependencies)

    # Drop indexes for webhook_endpoints
    op.drop_index("ix_webhook_endpoints_is_active", table_name="webhook_endpoints")
    op.drop_index("ix_webhook_endpoints_endpoint_key", table_name="webhook_endpoints")
    op.drop_index("ix_webhook_endpoints_integration_id", table_name="webhook_endpoints")
    op.drop_index("ix_webhook_endpoints_organization_id", table_name="webhook_endpoints")
    op.drop_table("webhook_endpoints")

    # Drop indexes for integration_logs
    op.drop_index("ix_integration_logs_created_at", table_name="integration_logs")
    op.drop_index("ix_integration_logs_status", table_name="integration_logs")
    op.drop_index("ix_integration_logs_action", table_name="integration_logs")
    op.drop_index("ix_integration_logs_integration_id", table_name="integration_logs")
    op.drop_table("integration_logs")

    # Drop indexes for integration_mappings
    op.drop_index("ix_integration_mappings_entity_type", table_name="integration_mappings")
    op.drop_index("ix_integration_mappings_integration_id", table_name="integration_mappings")
    op.drop_table("integration_mappings")

    # Drop indexes for integrations
    op.drop_index("ix_integrations_status", table_name="integrations")
    op.drop_index("ix_integrations_integration_type", table_name="integrations")
    op.drop_index("ix_integrations_organization_id", table_name="integrations")
    op.drop_table("integrations")
