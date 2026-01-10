"""Export service for generating CSV and PDF reports from findings."""

import csv
import io
from datetime import datetime, timezone
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.models.finding import Finding
from app.models.vendor import Vendor


async def get_findings_for_export(
    db: AsyncSession,
    org_id: str,
    document_id: str | None = None,
    vendor_id: str | None = None,
    severity: str | None = None,
    framework_id: str | None = None,
) -> tuple[list[Finding], Vendor | None, Document | None]:
    """Fetch findings with filters for export.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        document_id: Optional filter by document
        vendor_id: Optional filter by vendor
        severity: Optional filter by severity
        framework_id: Optional filter by framework

    Returns:
        Tuple of (list of findings, vendor if filtered, document if filtered)
    """
    query = (
        select(Finding)
        .options(selectinload(Finding.document))
        .where(Finding.organization_id == org_id)
    )

    if document_id:
        query = query.where(Finding.document_id == document_id)
    if severity:
        query = query.where(Finding.severity == severity)
    if framework_id:
        query = query.where(Finding.framework == framework_id)

    # If vendor_id is provided, filter findings by documents associated with that vendor
    if vendor_id:
        query = query.join(Document).where(Document.vendor_id == vendor_id)

    query = query.order_by(Finding.created_at.desc())
    result = await db.execute(query)
    findings = list(result.scalars().all())

    # Get vendor and document info if filtering by those
    vendor = None
    document = None

    if vendor_id:
        vendor_result = await db.execute(
            select(Vendor).where(
                Vendor.id == vendor_id,
                Vendor.organization_id == org_id,
            )
        )
        vendor = vendor_result.scalar_one_or_none()

    if document_id:
        doc_result = await db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.organization_id == org_id,
            )
        )
        document = doc_result.scalar_one_or_none()

    return findings, vendor, document


class CSVExporter:
    """Generates CSV exports of findings data."""

    COLUMNS = [
        "id",
        "title",
        "description",
        "severity",
        "framework",
        "control",
        "page",
        "confidence",
    ]

    def __init__(self, findings: list[Finding]):
        """Initialize the CSV exporter.

        Args:
            findings: List of Finding objects to export
        """
        self.findings = findings

    def generate(self) -> bytes:
        """Generate CSV content from findings.

        Returns:
            CSV content as bytes
        """
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
                    finding.framework,
                    finding.framework_control or "",
                    finding.page_number or "",
                    f"{finding.confidence_score:.2f}" if finding.confidence_score else "",
                ]
            )

        return output.getvalue().encode("utf-8")


class PDFExporter:
    """Generates PDF reports from findings data."""

    def __init__(
        self,
        findings: list[Finding],
        vendor: Vendor | None = None,
        document: Document | None = None,
    ):
        """Initialize the PDF exporter.

        Args:
            findings: List of Finding objects to export
            vendor: Optional vendor for header
            document: Optional document for header
        """
        self.findings = findings
        self.vendor = vendor
        self.document = document
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self) -> None:
        """Set up custom paragraph styles for the PDF."""
        self.styles.add(
            ParagraphStyle(
                "ReportTitle",
                parent=self.styles["Heading1"],
                fontSize=18,
                spaceAfter=20,
                textColor=colors.HexColor("#1a365d"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                "SectionHeader",
                parent=self.styles["Heading2"],
                fontSize=14,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.HexColor("#2c5282"),
            )
        )
        self.styles.add(
            ParagraphStyle(
                "SubHeader",
                parent=self.styles["Heading3"],
                fontSize=12,
                spaceBefore=10,
                spaceAfter=6,
            )
        )
        self.styles.add(
            ParagraphStyle(
                "Footer",
                parent=self.styles["Normal"],
                fontSize=8,
                textColor=colors.gray,
            )
        )

    def _get_severity_counts(self) -> dict[str, int]:
        """Count findings by severity level.

        Returns:
            Dictionary mapping severity to count
        """
        counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0,
        }
        for finding in self.findings:
            severity = finding.severity.lower()
            if severity in counts:
                counts[severity] += 1
        return counts

    def _get_severity_color(self, severity: str) -> colors.Color:
        """Get color for severity level.

        Args:
            severity: Severity level string

        Returns:
            ReportLab color object
        """
        severity_colors = {
            "critical": colors.HexColor("#c53030"),
            "high": colors.HexColor("#dd6b20"),
            "medium": colors.HexColor("#d69e2e"),
            "low": colors.HexColor("#38a169"),
            "info": colors.HexColor("#3182ce"),
        }
        return severity_colors.get(severity.lower(), colors.black)

    def _build_header(self) -> list[Any]:
        """Build the report header section.

        Returns:
            List of flowable elements for the header
        """
        elements = []

        # Title
        title = "Compliance Findings Report"
        elements.append(Paragraph(title, self.styles["ReportTitle"]))

        # Vendor and document info
        if self.vendor:
            elements.append(
                Paragraph(f"Vendor: {self.vendor.name}", self.styles["Normal"])
            )
        if self.document:
            elements.append(
                Paragraph(f"Document: {self.document.filename}", self.styles["Normal"])
            )

        elements.append(Spacer(1, 20))
        return elements

    def _build_executive_summary(self) -> list[Any]:
        """Build the executive summary section.

        Returns:
            List of flowable elements for the summary
        """
        elements = []
        elements.append(Paragraph("Executive Summary", self.styles["SectionHeader"]))

        severity_counts = self._get_severity_counts()
        total = len(self.findings)

        # Summary text
        summary_text = f"Total Findings: {total}"
        elements.append(Paragraph(summary_text, self.styles["Normal"]))
        elements.append(Spacer(1, 10))

        # Severity breakdown table
        severity_data = [
            ["Severity", "Count"],
            ["Critical", str(severity_counts["critical"])],
            ["High", str(severity_counts["high"])],
            ["Medium", str(severity_counts["medium"])],
            ["Low", str(severity_counts["low"])],
            ["Info", str(severity_counts["info"])],
        ]

        severity_table = Table(severity_data, colWidths=[2 * inch, 1 * inch])
        severity_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 10),
                    ("TOPPADDING", (0, 0), (-1, 0), 10),
                    ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f7fafc")),
                    ("GRID", (0, 0), (-1, -1), 1, colors.HexColor("#e2e8f0")),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("TOPPADDING", (0, 1), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
                ]
            )
        )
        elements.append(severity_table)
        elements.append(Spacer(1, 20))
        return elements

    def _build_findings_table(self) -> list[Any]:
        """Build the detailed findings table.

        Returns:
            List of flowable elements for findings
        """
        elements = []
        elements.append(Paragraph("Detailed Findings", self.styles["SectionHeader"]))

        if not self.findings:
            elements.append(Paragraph("No findings to display.", self.styles["Normal"]))
            return elements

        # Table headers
        table_data = [["ID", "Title", "Severity", "Framework", "Control", "Page"]]

        # Add finding rows
        for finding in self.findings:
            # Truncate long titles for table display
            title = finding.title[:50] + "..." if len(finding.title) > 50 else finding.title
            table_data.append(
                [
                    finding.id[:8] + "...",
                    title,
                    finding.severity.upper(),
                    finding.framework,
                    finding.framework_control or "N/A",
                    str(finding.page_number) if finding.page_number else "N/A",
                ]
            )

        # Create table with appropriate column widths
        col_widths = [0.8 * inch, 2.2 * inch, 0.8 * inch, 1 * inch, 1 * inch, 0.6 * inch]
        findings_table = Table(table_data, colWidths=col_widths, repeatRows=1)

        # Style the table
        table_style = [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c5282")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("FONTSIZE", (0, 1), (-1, -1), 8),
            ("TOPPADDING", (0, 1), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (2, 1), (2, -1), "CENTER"),  # Severity column
            ("ALIGN", (5, 1), (5, -1), "CENTER"),  # Page column
        ]

        # Add alternating row colors
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                table_style.append(
                    ("BACKGROUND", (0, i), (-1, i), colors.HexColor("#f7fafc"))
                )
            else:
                table_style.append(
                    ("BACKGROUND", (0, i), (-1, i), colors.white)
                )

        findings_table.setStyle(TableStyle(table_style))
        elements.append(findings_table)
        elements.append(Spacer(1, 20))
        return elements

    def _build_footer(self) -> list[Any]:
        """Build the report footer section.

        Returns:
            List of flowable elements for the footer
        """
        elements = []
        elements.append(Spacer(1, 30))

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        footer_text = f"Report generated on {timestamp} by VendorAuditAI"
        elements.append(Paragraph(footer_text, self.styles["Footer"]))

        return elements

    def generate(self) -> bytes:
        """Generate PDF content from findings.

        Returns:
            PDF content as bytes
        """
        buffer = io.BytesIO()

        # Create the PDF document
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.75 * inch,
            leftMargin=0.75 * inch,
            topMargin=0.75 * inch,
            bottomMargin=0.75 * inch,
        )

        # Build document elements
        elements = []
        elements.extend(self._build_header())
        elements.extend(self._build_executive_summary())
        elements.extend(self._build_findings_table())
        elements.extend(self._build_footer())

        # Build the PDF
        doc.build(elements)

        return buffer.getvalue()
