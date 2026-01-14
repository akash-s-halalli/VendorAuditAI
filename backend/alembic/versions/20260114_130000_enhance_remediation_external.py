"""Enhance remediation tasks with external system integration fields.

Revision ID: 20260114_130000
Revises: 20260114_120000
Create Date: 2026-01-14
"""
from alembic import op
import sqlalchemy as sa

revision = "20260114_130000"
down_revision = "20260114_120000"
branch_labels = None
depends_on = None


def upgrade():
    # Add external system integration fields to remediation_tasks table
    op.add_column(
        "remediation_tasks",
        sa.Column("external_system", sa.String(50), nullable=True)
    )
    op.add_column(
        "remediation_tasks",
        sa.Column("external_id", sa.String(255), nullable=True)
    )
    op.add_column(
        "remediation_tasks",
        sa.Column("external_url", sa.String(500), nullable=True)
    )
    op.add_column(
        "remediation_tasks",
        sa.Column("external_status", sa.String(100), nullable=True)
    )
    op.add_column(
        "remediation_tasks",
        sa.Column("last_synced_at", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "remediation_tasks",
        sa.Column("sync_enabled", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column(
        "remediation_tasks",
        sa.Column("sync_direction", sa.String(20), nullable=True)
    )

    # Create indexes for efficient querying of external system data
    op.create_index(
        "ix_remediation_tasks_external_system",
        "remediation_tasks",
        ["external_system"]
    )
    op.create_index(
        "ix_remediation_tasks_external_id",
        "remediation_tasks",
        ["external_id"]
    )
    op.create_index(
        "ix_remediation_tasks_sync_enabled",
        "remediation_tasks",
        ["sync_enabled"]
    )
    # Composite index for external system lookups
    op.create_index(
        "ix_remediation_tasks_external_system_id",
        "remediation_tasks",
        ["external_system", "external_id"]
    )


def downgrade():
    # Drop indexes first
    op.drop_index("ix_remediation_tasks_external_system_id", table_name="remediation_tasks")
    op.drop_index("ix_remediation_tasks_sync_enabled", table_name="remediation_tasks")
    op.drop_index("ix_remediation_tasks_external_id", table_name="remediation_tasks")
    op.drop_index("ix_remediation_tasks_external_system", table_name="remediation_tasks")

    # Drop columns
    op.drop_column("remediation_tasks", "sync_direction")
    op.drop_column("remediation_tasks", "sync_enabled")
    op.drop_column("remediation_tasks", "last_synced_at")
    op.drop_column("remediation_tasks", "external_status")
    op.drop_column("remediation_tasks", "external_url")
    op.drop_column("remediation_tasks", "external_id")
    op.drop_column("remediation_tasks", "external_system")
