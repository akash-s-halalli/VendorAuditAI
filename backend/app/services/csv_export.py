"""CSV export service for generating CSV reports."""

import csv
import io

from app.models.finding import Finding
from app.models.remediation import RemediationTask
from app.models.vendor import Vendor


class VendorCSVExporter:
    """Generates CSV exports of vendor data."""

    COLUMNS = [
        "id",
        "name",
        "description",
        "website",
        "tier",
        "status",
        "category",
        "criticality_score",
        "data_classification",
        "contract_expiry",
        "last_assessed",
        "next_assessment_due",
        "created_at",
    ]

    def __init__(self, vendors: list[Vendor]):
        """Initialize the CSV exporter."""
        self.vendors = vendors

    def generate(self) -> bytes:
        """Generate CSV content from vendors."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Write header
        writer.writerow(self.COLUMNS)

        # Write data rows
        for vendor in self.vendors:
            writer.writerow(
                [
                    vendor.id,
                    vendor.name,
                    vendor.description or "",
                    vendor.website or "",
                    vendor.tier,
                    vendor.status,
                    vendor.category or "",
                    vendor.criticality_score or "",
                    vendor.data_classification or "",
                    vendor.contract_expiry.isoformat() if vendor.contract_expiry else "",
                    (
                        vendor.last_assessed.isoformat()
                        if vendor.last_assessed
                        else ""
                    ),
                    (
                        vendor.next_assessment_due.isoformat()
                        if vendor.next_assessment_due
                        else ""
                    ),
                    vendor.created_at.isoformat() if vendor.created_at else "",
                ]
            )

        return output.getvalue().encode("utf-8")


class FindingCSVExporter:
    """Generates CSV exports of finding data with extended fields."""

    COLUMNS = [
        "id",
        "title",
        "description",
        "severity",
        "status",
        "framework",
        "control",
        "evidence",
        "remediation",
        "impact",
        "page_number",
        "section",
        "confidence",
        "document_id",
        "created_at",
        "resolved_at",
    ]

    def __init__(self, findings: list[Finding]):
        """Initialize the CSV exporter."""
        self.findings = findings

    def generate(self) -> bytes:
        """Generate CSV content from findings."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Write header
        writer.writerow(self.COLUMNS)

        # Write data rows
        for finding in self.findings:
            writer.writerow(
                [
                    finding.id,
                    finding.title,
                    finding.description,
                    finding.severity,
                    finding.status,
                    finding.framework,
                    finding.framework_control or "",
                    finding.evidence or "",
                    finding.remediation or "",
                    finding.impact or "",
                    finding.page_number or "",
                    finding.section_header or "",
                    f"{finding.confidence_score:.2f}" if finding.confidence_score else "",
                    finding.document_id,
                    finding.created_at.isoformat() if finding.created_at else "",
                    finding.resolved_at.isoformat() if finding.resolved_at else "",
                ]
            )

        return output.getvalue().encode("utf-8")


class RemediationCSVExporter:
    """Generates CSV exports of remediation tasks."""

    COLUMNS = [
        "id",
        "title",
        "description",
        "status",
        "priority",
        "vendor_name",
        "assignee_email",
        "finding_id",
        "finding_title",
        "due_date",
        "sla_days",
        "sla_breached",
        "resolution_notes",
        "created_at",
        "resolved_at",
    ]

    def __init__(self, tasks: list[RemediationTask]):
        """Initialize the CSV exporter."""
        self.tasks = tasks

    def generate(self) -> bytes:
        """Generate CSV content from remediation tasks."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Write header
        writer.writerow(self.COLUMNS)

        # Write data rows
        for task in self.tasks:
            writer.writerow(
                [
                    task.id,
                    task.title,
                    task.description or "",
                    task.status,
                    task.priority,
                    task.vendor.name if task.vendor else "",
                    task.assignee.email if task.assignee else "",
                    task.finding_id,
                    task.finding.title if task.finding else "",
                    task.due_date.isoformat() if task.due_date else "",
                    task.sla_days or "",
                    "Yes" if task.sla_breached else "No",
                    task.resolution_notes or "",
                    task.created_at.isoformat() if task.created_at else "",
                    task.resolved_at.isoformat() if task.resolved_at else "",
                ]
            )

        return output.getvalue().encode("utf-8")
