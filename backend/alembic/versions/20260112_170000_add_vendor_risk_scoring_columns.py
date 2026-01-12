"""Add vendor risk scoring columns.

Revision ID: e4f7a91d2b5c
Revises: d958a47cf3c8
Create Date: 2026-01-12 17:00:00.000000

Adds columns for vendor risk scoring:
- risk_score: Calculated risk score (0-100)
- risk_calculated_at: Timestamp of last risk calculation
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e4f7a91d2b5c"
down_revision: str | None = "d958a47cf3c8"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Add risk scoring columns to vendors table."""
    # Check if columns already exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col["name"] for col in inspector.get_columns("vendors")]

    if "risk_score" not in existing_columns:
        op.add_column(
            "vendors",
            sa.Column("risk_score", sa.Float(), nullable=True),
        )

    if "risk_calculated_at" not in existing_columns:
        op.add_column(
            "vendors",
            sa.Column("risk_calculated_at", sa.DateTime(timezone=True), nullable=True),
        )


def downgrade() -> None:
    """Remove risk scoring columns from vendors table."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = [col["name"] for col in inspector.get_columns("vendors")]

    if "risk_calculated_at" in existing_columns:
        op.drop_column("vendors", "risk_calculated_at")
    if "risk_score" in existing_columns:
        op.drop_column("vendors", "risk_score")
