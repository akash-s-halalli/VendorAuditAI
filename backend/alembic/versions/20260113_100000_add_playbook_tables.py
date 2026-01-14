"""Add AI Governance Playbook tables.

Revision ID: e7a2b3c4d5f6
Revises: e4f7a91d2b5c
Create Date: 2026-01-13 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7a2b3c4d5f6'
down_revision: Union[str, None] = 'e4f7a91d2b5c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create AI Governance Playbook tables."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create ai_playbooks table
    if 'ai_playbooks' not in existing_tables:
        op.create_table(
            'ai_playbooks',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_by_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('name', sa.String(255), nullable=False),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('phase', sa.String(50), nullable=False, server_default='tool_selection'),
            sa.Column('target_audience', sa.String(50), nullable=False, server_default='all'),
            sa.Column('department', sa.String(50), nullable=False, server_default='all'),
            sa.Column('version', sa.String(20), nullable=False, server_default='1.0'),
            sa.Column('is_active', sa.Boolean, nullable=False, server_default='1'),
            sa.Column('is_default', sa.Boolean, nullable=False, server_default='0'),
            sa.Column('estimated_duration_minutes', sa.Integer, nullable=True),
            sa.Column('icon', sa.String(50), nullable=True),
            sa.Column('color', sa.String(20), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_ai_playbooks_organization_id', 'ai_playbooks', ['organization_id'])
        op.create_index('ix_ai_playbooks_phase', 'ai_playbooks', ['phase'])
        op.create_index('ix_ai_playbooks_department', 'ai_playbooks', ['department'])

    # Create playbook_steps table
    if 'playbook_steps' not in existing_tables:
        op.create_table(
            'playbook_steps',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('playbook_id', sa.String(36), sa.ForeignKey('ai_playbooks.id', ondelete='CASCADE'), nullable=False),
            sa.Column('step_number', sa.Integer, nullable=False),
            sa.Column('title', sa.String(255), nullable=False),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('instructions', sa.Text, nullable=False),
            sa.Column('checklist', sa.Text, nullable=True),
            sa.Column('required_approvals', sa.Text, nullable=True),
            sa.Column('estimated_time_minutes', sa.Integer, nullable=True),
            sa.Column('resources', sa.Text, nullable=True),
            sa.Column('tips', sa.Text, nullable=True),
            sa.Column('warning', sa.Text, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_playbook_steps_playbook_id', 'playbook_steps', ['playbook_id'])

    # Create playbook_progress table
    if 'playbook_progress' not in existing_tables:
        op.create_table(
            'playbook_progress',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
            sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('playbook_id', sa.String(36), sa.ForeignKey('ai_playbooks.id', ondelete='CASCADE'), nullable=False),
            sa.Column('vendor_id', sa.String(36), sa.ForeignKey('vendors.id', ondelete='SET NULL'), nullable=True),
            sa.Column('current_step', sa.Integer, nullable=False, server_default='1'),
            sa.Column('status', sa.String(50), nullable=False, server_default='not_started'),
            sa.Column('step_completions', sa.Text, nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('progress_percentage', sa.Float, nullable=False, server_default='0.0'),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_playbook_progress_organization_id', 'playbook_progress', ['organization_id'])
        op.create_index('ix_playbook_progress_user_id', 'playbook_progress', ['user_id'])
        op.create_index('ix_playbook_progress_playbook_id', 'playbook_progress', ['playbook_id'])
        op.create_index('ix_playbook_progress_vendor_id', 'playbook_progress', ['vendor_id'])
        op.create_index('ix_playbook_progress_status', 'playbook_progress', ['status'])

    # Create playbook_approvals table
    if 'playbook_approvals' not in existing_tables:
        op.create_table(
            'playbook_approvals',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('progress_id', sa.String(36), sa.ForeignKey('playbook_progress.id', ondelete='CASCADE'), nullable=False),
            sa.Column('step_id', sa.String(36), sa.ForeignKey('playbook_steps.id', ondelete='CASCADE'), nullable=False),
            sa.Column('requested_by_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
            sa.Column('approver_id', sa.String(36), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
            sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
            sa.Column('comments', sa.Text, nullable=True),
            sa.Column('required_role', sa.String(100), nullable=True),
            sa.Column('requested_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_playbook_approvals_progress_id', 'playbook_approvals', ['progress_id'])
        op.create_index('ix_playbook_approvals_step_id', 'playbook_approvals', ['step_id'])
        op.create_index('ix_playbook_approvals_status', 'playbook_approvals', ['status'])


def downgrade() -> None:
    """Remove AI Governance Playbook tables."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'playbook_approvals' in existing_tables:
        op.drop_table('playbook_approvals')
    if 'playbook_progress' in existing_tables:
        op.drop_table('playbook_progress')
    if 'playbook_steps' in existing_tables:
        op.drop_table('playbook_steps')
    if 'ai_playbooks' in existing_tables:
        op.drop_table('ai_playbooks')
