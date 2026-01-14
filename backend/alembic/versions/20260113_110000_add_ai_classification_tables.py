"""Add AI Tool Classification tables.

Revision ID: f8b3c4d5e6a7
Revises: e7a2b3c4d5f6
Create Date: 2026-01-13 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f8b3c4d5e6a7'
down_revision: Union[str, None] = 'e7a2b3c4d5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create AI Tool Classification tables."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create ai_tool_classifications table
    if 'ai_tool_classifications' not in existing_tables:
        op.create_table(
            'ai_tool_classifications',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('vendor_id', sa.String(36), sa.ForeignKey('vendors.id', ondelete='CASCADE'), nullable=False, unique=True, index=True),
            sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False, index=True),

            # AI Stack Type Classification
            sa.Column('stack_type', sa.String(50), nullable=False, default='not_ai_tool'),

            # Capability Flags
            sa.Column('has_credential_access', sa.Boolean(), default=False),
            sa.Column('has_autonomous_actions', sa.Boolean(), default=False),
            sa.Column('has_data_training', sa.Boolean(), default=False),
            sa.Column('has_external_integrations', sa.Boolean(), default=False),
            sa.Column('has_code_execution', sa.Boolean(), default=False),

            # Credential Details (JSON strings)
            sa.Column('credential_types', sa.Text(), nullable=True),
            sa.Column('credential_scope', sa.Text(), nullable=True),

            # Autonomous Action Details
            sa.Column('action_types', sa.Text(), nullable=True),
            sa.Column('requires_human_approval', sa.Boolean(), default=True),

            # Data Handling
            sa.Column('data_access_types', sa.Text(), nullable=True),
            sa.Column('data_retention_policy', sa.String(255), nullable=True),
            sa.Column('trains_on_customer_data', sa.Boolean(), default=False),
            sa.Column('data_sharing_third_parties', sa.Boolean(), default=False),

            # Risk Assessment (AI-specific)
            sa.Column('autonomy_level', sa.String(20), default='none'),
            sa.Column('blast_radius', sa.String(20), default='minimal'),
            sa.Column('ai_risk_score', sa.Integer(), nullable=True),

            # Classification Metadata
            sa.Column('classification_method', sa.String(20), default='manual'),
            sa.Column('classification_confidence', sa.Numeric(3, 2), nullable=True),
            sa.Column('classified_by_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('classified_at', sa.DateTime(), nullable=True),

            # Notes
            sa.Column('notes', sa.Text(), nullable=True),

            # Timestamps
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        )

        # Create indexes
        op.create_index('ix_ai_tool_classifications_stack_type', 'ai_tool_classifications', ['stack_type'])

    # Create ai_tool_capabilities table
    if 'ai_tool_capabilities' not in existing_tables:
        op.create_table(
            'ai_tool_capabilities',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('classification_id', sa.String(36), sa.ForeignKey('ai_tool_classifications.id', ondelete='CASCADE'), nullable=False, index=True),

            # Capability Details
            sa.Column('capability_category', sa.String(100), nullable=False),
            sa.Column('capability_name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('risk_level', sa.String(20), default='medium'),
            sa.Column('is_enabled', sa.Boolean(), default=True),

            # Evidence
            sa.Column('evidence', sa.Text(), nullable=True),
            sa.Column('documentation_url', sa.String(500), nullable=True),

            # Timestamps
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        )


def downgrade() -> None:
    """Drop AI Tool Classification tables."""
    op.drop_table('ai_tool_capabilities')
    op.drop_table('ai_tool_classifications')
