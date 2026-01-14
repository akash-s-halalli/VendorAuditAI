"""Add missing columns to integrations table.

Revision ID: 20260114_140000
Revises: 20260114_130000
Create Date: 2026-01-14
"""
from alembic import op
import sqlalchemy as sa

revision = "20260114_140000"
down_revision = "20260114_130000"
branch_labels = None
depends_on = None


def upgrade():
    # Get connection to check existing columns
    conn = op.get_bind()
    inspector = sa.inspect(conn)

    if "integrations" in inspector.get_table_names():
        existing_columns = [col["name"] for col in inspector.get_columns("integrations")]

        # Add is_enabled column
        if "is_enabled" not in existing_columns:
            op.add_column(
                "integrations",
                sa.Column("is_enabled", sa.Boolean, nullable=False, server_default="true")
            )

        # Add credentials column
        if "credentials" not in existing_columns:
            op.add_column(
                "integrations",
                sa.Column("credentials", sa.JSON, nullable=True)
            )

        # Add sync_settings column
        if "sync_settings" not in existing_columns:
            op.add_column(
                "integrations",
                sa.Column("sync_settings", sa.JSON, nullable=True)
            )

        # Add sync_count column
        if "sync_count" not in existing_columns:
            op.add_column(
                "integrations",
                sa.Column("sync_count", sa.Integer, nullable=False, server_default="0")
            )


def downgrade():
    op.drop_column("integrations", "sync_count")
    op.drop_column("integrations", "sync_settings")
    op.drop_column("integrations", "credentials")
    op.drop_column("integrations", "is_enabled")
