"""Add approved vendor registry tables.

Revision ID: 20260114_100000
Revises: 20260113_110000
Create Date: 2026-01-14
"""
from alembic import op
import sqlalchemy as sa

revision = "20260114_100000"
down_revision = "20260113_110000"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create approved_ai_vendors table
    op.create_table(
        "approved_ai_vendors",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("vendor_id", sa.String(36), sa.ForeignKey("vendors.id"), unique=True, nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("approval_status", sa.String(50), nullable=False),
        sa.Column("approval_date", sa.DateTime, nullable=True),
        sa.Column("expiration_date", sa.DateTime, nullable=True),
        sa.Column("approved_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_departments", sa.JSON, nullable=True),
        sa.Column("approved_use_cases", sa.JSON, nullable=True),
        sa.Column("prohibited_uses", sa.JSON, nullable=True),
        sa.Column("data_classification_limit", sa.String(50), nullable=False),
        sa.Column("conditions", sa.Text, nullable=True),
        sa.Column("required_settings", sa.JSON, nullable=True),
        sa.Column("required_training", sa.Boolean, nullable=False, default=False),
        sa.Column("training_url", sa.String(500), nullable=True),
        sa.Column("review_notes", sa.Text, nullable=True),
        sa.Column("risk_score", sa.Integer, nullable=True),
        sa.Column("max_deployment_count", sa.Integer, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for approved_ai_vendors
    op.create_index("ix_approved_ai_vendors_organization_id", "approved_ai_vendors", ["organization_id"])
    op.create_index("ix_approved_ai_vendors_approval_status", "approved_ai_vendors", ["approval_status"])
    op.create_index("ix_approved_ai_vendors_vendor_id", "approved_ai_vendors", ["vendor_id"])

    # 2. Create approved_use_cases table
    op.create_table(
        "approved_use_cases",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("approved_vendor_id", sa.String(36), sa.ForeignKey("approved_ai_vendors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("use_case_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("data_types_allowed", sa.JSON, nullable=True),
        sa.Column("restrictions", sa.Text, nullable=True),
        sa.Column("example_prompts", sa.JSON, nullable=True),
        sa.Column("prohibited_actions", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for approved_use_cases
    op.create_index("ix_approved_use_cases_approved_vendor_id", "approved_use_cases", ["approved_vendor_id"])

    # 3. Create vendor_deployments table
    op.create_table(
        "vendor_deployments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("approved_vendor_id", sa.String(36), sa.ForeignKey("approved_ai_vendors.id", ondelete="CASCADE"), nullable=False),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("deployed_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("team", sa.String(255), nullable=True),
        sa.Column("use_case", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("configuration", sa.JSON, nullable=True),
        sa.Column("data_classification", sa.String(50), nullable=False),
        sa.Column("activated_at", sa.DateTime, nullable=True),
        sa.Column("deactivated_at", sa.DateTime, nullable=True),
        sa.Column("last_used_at", sa.DateTime, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for vendor_deployments
    op.create_index("ix_vendor_deployments_approved_vendor_id", "vendor_deployments", ["approved_vendor_id"])
    op.create_index("ix_vendor_deployments_organization_id", "vendor_deployments", ["organization_id"])
    op.create_index("ix_vendor_deployments_deployed_by_id", "vendor_deployments", ["deployed_by_id"])
    op.create_index("ix_vendor_deployments_status", "vendor_deployments", ["status"])

    # 4. Create ai_tool_requests table
    op.create_table(
        "ai_tool_requests",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("organization_id", sa.String(36), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("requested_by_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("vendor_name", sa.String(255), nullable=False),
        sa.Column("vendor_website", sa.String(500), nullable=True),
        sa.Column("tool_description", sa.Text, nullable=True),
        sa.Column("use_case_description", sa.Text, nullable=True),
        sa.Column("department", sa.String(255), nullable=True),
        sa.Column("business_justification", sa.Text, nullable=True),
        sa.Column("expected_data_types", sa.JSON, nullable=True),
        sa.Column("urgency", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False),
        sa.Column("assigned_reviewer_id", sa.String(36), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("review_notes", sa.Text, nullable=True),
        sa.Column("decision_date", sa.DateTime, nullable=True),
        sa.Column("created_vendor_id", sa.String(36), sa.ForeignKey("vendors.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    # Create indexes for ai_tool_requests
    op.create_index("ix_ai_tool_requests_organization_id", "ai_tool_requests", ["organization_id"])
    op.create_index("ix_ai_tool_requests_requested_by_id", "ai_tool_requests", ["requested_by_id"])
    op.create_index("ix_ai_tool_requests_status", "ai_tool_requests", ["status"])
    op.create_index("ix_ai_tool_requests_assigned_reviewer_id", "ai_tool_requests", ["assigned_reviewer_id"])


def downgrade():
    # Drop tables in reverse order (respecting foreign key dependencies)

    # Drop indexes for ai_tool_requests
    op.drop_index("ix_ai_tool_requests_assigned_reviewer_id", table_name="ai_tool_requests")
    op.drop_index("ix_ai_tool_requests_status", table_name="ai_tool_requests")
    op.drop_index("ix_ai_tool_requests_requested_by_id", table_name="ai_tool_requests")
    op.drop_index("ix_ai_tool_requests_organization_id", table_name="ai_tool_requests")
    op.drop_table("ai_tool_requests")

    # Drop indexes for vendor_deployments
    op.drop_index("ix_vendor_deployments_status", table_name="vendor_deployments")
    op.drop_index("ix_vendor_deployments_deployed_by_id", table_name="vendor_deployments")
    op.drop_index("ix_vendor_deployments_organization_id", table_name="vendor_deployments")
    op.drop_index("ix_vendor_deployments_approved_vendor_id", table_name="vendor_deployments")
    op.drop_table("vendor_deployments")

    # Drop indexes for approved_use_cases
    op.drop_index("ix_approved_use_cases_approved_vendor_id", table_name="approved_use_cases")
    op.drop_table("approved_use_cases")

    # Drop indexes for approved_ai_vendors
    op.drop_index("ix_approved_ai_vendors_vendor_id", table_name="approved_ai_vendors")
    op.drop_index("ix_approved_ai_vendors_approval_status", table_name="approved_ai_vendors")
    op.drop_index("ix_approved_ai_vendors_organization_id", table_name="approved_ai_vendors")
    op.drop_table("approved_ai_vendors")
