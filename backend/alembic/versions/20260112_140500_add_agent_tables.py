"""Add AI Agent tables.

Revision ID: d958a47cf3c8
Revises: b97fd3b154b0
Create Date: 2026-01-12 14:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd958a47cf3c8'
down_revision: Union[str, None] = 'b97fd3b154b0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create AI Agent tables."""
    # Get connection to check if tables exist
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    # Create agents table if not exists
    if 'agents' not in existing_tables:
        op.create_table(
            'agents',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('name', sa.String(100), nullable=False),
            sa.Column('agent_type', sa.String(50), nullable=False),
            sa.Column('role', sa.String(100), nullable=False),
            sa.Column('description', sa.Text, nullable=True),
            sa.Column('status', sa.String(20), nullable=False, server_default='idle'),
            sa.Column('uptime_percentage', sa.Float, nullable=False, server_default='100.0'),
            sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('error_message', sa.Text, nullable=True),
            sa.Column('configuration', sa.JSON, nullable=False, server_default='{}'),
            sa.Column('organization_id', sa.String(36), sa.ForeignKey('organizations.id', ondelete='CASCADE'), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        )
        op.create_index('ix_agents_organization_id', 'agents', ['organization_id'])
        op.create_index('ix_agents_agent_type', 'agents', ['agent_type'])
        op.create_index('ix_agents_status', 'agents', ['status'])

    # Create agent_tasks table if not exists
    if 'agent_tasks' not in existing_tables:
        op.create_table(
            'agent_tasks',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('agent_id', sa.String(36), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
            sa.Column('task_type', sa.String(20), nullable=False),
            sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
            sa.Column('input_data', sa.JSON, nullable=False, server_default='{}'),
            sa.Column('output_data', sa.JSON, nullable=True),
            sa.Column('error_message', sa.Text, nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('items_processed', sa.Integer, nullable=True),
            sa.Column('findings_count', sa.Integer, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_agent_tasks_agent_id', 'agent_tasks', ['agent_id'])
        op.create_index('ix_agent_tasks_status', 'agent_tasks', ['status'])
        op.create_index('ix_agent_tasks_task_type', 'agent_tasks', ['task_type'])

    # Create agent_logs table if not exists
    if 'agent_logs' not in existing_tables:
        op.create_table(
            'agent_logs',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('agent_id', sa.String(36), sa.ForeignKey('agents.id', ondelete='CASCADE'), nullable=False),
            sa.Column('task_id', sa.String(36), sa.ForeignKey('agent_tasks.id', ondelete='SET NULL'), nullable=True),
            sa.Column('level', sa.String(20), nullable=False, server_default='info'),
            sa.Column('message', sa.Text, nullable=False),
            sa.Column('details', sa.JSON, nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        )
        op.create_index('ix_agent_logs_agent_id', 'agent_logs', ['agent_id'])
        op.create_index('ix_agent_logs_level', 'agent_logs', ['level'])
        op.create_index('ix_agent_logs_task_id', 'agent_logs', ['task_id'])


def downgrade() -> None:
    """Remove AI Agent tables."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_tables = inspector.get_table_names()

    if 'agent_logs' in existing_tables:
        op.drop_table('agent_logs')
    if 'agent_tasks' in existing_tables:
        op.drop_table('agent_tasks')
    if 'agents' in existing_tables:
        op.drop_table('agents')
