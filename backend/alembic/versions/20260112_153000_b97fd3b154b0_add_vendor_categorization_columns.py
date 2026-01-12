"""Add vendor categorization columns.

Revision ID: b97fd3b154b0
Revises:
Create Date: 2026-01-12 15:30:00.000000

Adds columns for the 25-category DoorDash-style vendor taxonomy:
- category: Vendor category classification (e.g., 'cloud_infrastructure')
- recommended_frameworks: JSON array of compliance frameworks
- data_types: JSON array of data types handled by vendor
- categorization_confidence: AI confidence score (0.0-1.0)
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b97fd3b154b0"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    """Add vendor categorization columns to vendors table."""
    op.add_column(
        "vendors",
        sa.Column("category", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "vendors",
        sa.Column("recommended_frameworks", sa.Text(), nullable=True),
    )
    op.add_column(
        "vendors",
        sa.Column("data_types", sa.Text(), nullable=True),
    )
    op.add_column(
        "vendors",
        sa.Column("categorization_confidence", sa.Float(), nullable=True),
    )


def downgrade() -> None:
    """Remove vendor categorization columns from vendors table."""
    op.drop_column("vendors", "categorization_confidence")
    op.drop_column("vendors", "data_types")
    op.drop_column("vendors", "recommended_frameworks")
    op.drop_column("vendors", "category")
