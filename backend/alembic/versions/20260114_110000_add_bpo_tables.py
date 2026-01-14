"""Add BPO Risk Management tables.

Revision ID: 20260114_110000
Revises: 20260114_100000
Create Date: 2026-01-14
"""
from alembic import op
import sqlalchemy as sa

revision = "20260114_110000"
down_revision = "20260114_100000"
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create bpo_providers table
    op.create_table(
        "bpo_providers",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "vendor_id",
            sa.String(36),
            sa.ForeignKey("vendors.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("service_type", sa.String(50), nullable=False, default="other"),
        sa.Column("process_category", sa.String(50), nullable=False, default="other"),
        sa.Column("geographic_locations", sa.Text, nullable=True),  # JSON list
        sa.Column("data_access_level", sa.String(50), nullable=False, default="none"),
        sa.Column("employee_count", sa.Integer, nullable=True),
        sa.Column("contract_value", sa.Float, nullable=True),
        sa.Column("sla_requirements", sa.Text, nullable=True),  # JSON object
        sa.Column("primary_contact_name", sa.String(255), nullable=True),
        sa.Column("primary_contact_email", sa.String(255), nullable=True),
        sa.Column("contract_start_date", sa.Date, nullable=True),
        sa.Column("contract_end_date", sa.Date, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Create indexes for bpo_providers
    op.create_index("ix_bpo_providers_vendor_id", "bpo_providers", ["vendor_id"])
    op.create_index(
        "ix_bpo_providers_organization_id", "bpo_providers", ["organization_id"]
    )
    op.create_index("ix_bpo_providers_service_type", "bpo_providers", ["service_type"])
    op.create_index(
        "ix_bpo_providers_data_access_level", "bpo_providers", ["data_access_level"]
    )

    # 2. Create bpo_processes table
    op.create_table(
        "bpo_processes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "provider_id",
            sa.String(36),
            sa.ForeignKey("bpo_providers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("process_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("criticality", sa.String(50), nullable=False, default="medium"),
        sa.Column("data_types", sa.Text, nullable=True),  # JSON list
        sa.Column("controls_required", sa.Text, nullable=True),  # JSON list
        sa.Column("volume_per_month", sa.Integer, nullable=True),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Create indexes for bpo_processes
    op.create_index("ix_bpo_processes_provider_id", "bpo_processes", ["provider_id"])
    op.create_index("ix_bpo_processes_criticality", "bpo_processes", ["criticality"])

    # 3. Create bpo_assessments table
    op.create_table(
        "bpo_assessments",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "provider_id",
            sa.String(36),
            sa.ForeignKey("bpo_providers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.String(36),
            sa.ForeignKey("organizations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "assessor_id",
            sa.String(36),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("assessment_date", sa.DateTime, nullable=True),
        sa.Column(
            "assessment_type", sa.String(50), nullable=False, default="periodic"
        ),
        sa.Column("overall_score", sa.Integer, nullable=True),  # 0-100
        sa.Column("findings", sa.Text, nullable=True),  # JSON list
        sa.Column("recommendations", sa.Text, nullable=True),
        sa.Column("next_review_date", sa.Date, nullable=True),
        sa.Column("status", sa.String(50), nullable=False, default="scheduled"),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Create indexes for bpo_assessments
    op.create_index(
        "ix_bpo_assessments_provider_id", "bpo_assessments", ["provider_id"]
    )
    op.create_index(
        "ix_bpo_assessments_organization_id", "bpo_assessments", ["organization_id"]
    )
    op.create_index(
        "ix_bpo_assessments_assessor_id", "bpo_assessments", ["assessor_id"]
    )
    op.create_index("ix_bpo_assessments_status", "bpo_assessments", ["status"])
    op.create_index(
        "ix_bpo_assessments_assessment_type", "bpo_assessments", ["assessment_type"]
    )

    # 4. Create bpo_controls table
    op.create_table(
        "bpo_controls",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "process_id",
            sa.String(36),
            sa.ForeignKey("bpo_processes.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("control_name", sa.String(255), nullable=False),
        sa.Column("control_description", sa.Text, nullable=True),
        sa.Column("control_type", sa.String(50), nullable=False, default="preventive"),
        sa.Column(
            "control_category", sa.String(50), nullable=False, default="operational"
        ),
        sa.Column(
            "status", sa.String(50), nullable=False, default="not_implemented"
        ),
        sa.Column("evidence", sa.Text, nullable=True),
        sa.Column("last_tested_date", sa.Date, nullable=True),
        sa.Column("test_result", sa.String(50), nullable=False, default="not_tested"),
        sa.Column(
            "created_at", sa.DateTime, nullable=False, server_default=sa.func.now()
        ),
        sa.Column(
            "updated_at",
            sa.DateTime,
            nullable=False,
            server_default=sa.func.now(),
            onupdate=sa.func.now(),
        ),
    )

    # Create indexes for bpo_controls
    op.create_index("ix_bpo_controls_process_id", "bpo_controls", ["process_id"])
    op.create_index("ix_bpo_controls_control_type", "bpo_controls", ["control_type"])
    op.create_index(
        "ix_bpo_controls_control_category", "bpo_controls", ["control_category"]
    )
    op.create_index("ix_bpo_controls_status", "bpo_controls", ["status"])
    op.create_index("ix_bpo_controls_test_result", "bpo_controls", ["test_result"])


def downgrade():
    # Drop tables in reverse order (respecting foreign key dependencies)

    # Drop indexes and table for bpo_controls
    op.drop_index("ix_bpo_controls_test_result", table_name="bpo_controls")
    op.drop_index("ix_bpo_controls_status", table_name="bpo_controls")
    op.drop_index("ix_bpo_controls_control_category", table_name="bpo_controls")
    op.drop_index("ix_bpo_controls_control_type", table_name="bpo_controls")
    op.drop_index("ix_bpo_controls_process_id", table_name="bpo_controls")
    op.drop_table("bpo_controls")

    # Drop indexes and table for bpo_assessments
    op.drop_index("ix_bpo_assessments_assessment_type", table_name="bpo_assessments")
    op.drop_index("ix_bpo_assessments_status", table_name="bpo_assessments")
    op.drop_index("ix_bpo_assessments_assessor_id", table_name="bpo_assessments")
    op.drop_index("ix_bpo_assessments_organization_id", table_name="bpo_assessments")
    op.drop_index("ix_bpo_assessments_provider_id", table_name="bpo_assessments")
    op.drop_table("bpo_assessments")

    # Drop indexes and table for bpo_processes
    op.drop_index("ix_bpo_processes_criticality", table_name="bpo_processes")
    op.drop_index("ix_bpo_processes_provider_id", table_name="bpo_processes")
    op.drop_table("bpo_processes")

    # Drop indexes and table for bpo_providers
    op.drop_index("ix_bpo_providers_data_access_level", table_name="bpo_providers")
    op.drop_index("ix_bpo_providers_service_type", table_name="bpo_providers")
    op.drop_index("ix_bpo_providers_organization_id", table_name="bpo_providers")
    op.drop_index("ix_bpo_providers_vendor_id", table_name="bpo_providers")
    op.drop_table("bpo_providers")
