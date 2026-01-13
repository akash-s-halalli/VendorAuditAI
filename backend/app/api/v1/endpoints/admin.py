"""Admin endpoints for demo data management."""

import json
import random
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.chunk import DocumentChunk
from app.models.document import Document, DocumentStatus, DocumentType, ProcessingStage
from app.models.finding import AnalysisRun, Finding, FindingSeverity, FindingStatus
from app.models.user import User, UserRole
from app.models.vendor import Vendor, VendorStatus, VendorTier
from app.scripts.sample_content import get_document_content

router = APIRouter()


class SeedResponse(BaseModel):
    """Response for seed operation."""
    success: bool
    message: str
    vendors_created: int
    documents_created: int
    chunks_created: int
    analysis_runs_created: int
    findings_created: int


# Demo data definitions
DEMO_VENDORS = [
    {"name": "Amazon Web Services (AWS)", "description": "Cloud infrastructure provider", "website": "https://aws.amazon.com", "tier": "critical", "category": "cloud_infrastructure", "criticality_score": 95},
    {"name": "Stripe", "description": "Payment processing platform", "website": "https://stripe.com", "tier": "critical", "category": "payment_processing", "criticality_score": 98},
    {"name": "Okta", "description": "Identity and access management", "website": "https://okta.com", "tier": "high", "category": "identity_access", "criticality_score": 88},
    {"name": "Snowflake", "description": "Cloud data warehouse", "website": "https://snowflake.com", "tier": "high", "category": "data_warehouse", "criticality_score": 85},
    {"name": "OpenAI", "description": "AI/ML platform", "website": "https://openai.com", "tier": "high", "category": "ai_ml", "criticality_score": 82},
    {"name": "Zendesk", "description": "Customer support platform", "website": "https://zendesk.com", "tier": "medium", "category": "customer_support", "criticality_score": 65},
    {"name": "Slack", "description": "Team collaboration", "website": "https://slack.com", "tier": "medium", "category": "communication", "criticality_score": 60},
    {"name": "GitHub", "description": "Source code repository", "website": "https://github.com", "tier": "medium", "category": "devops", "criticality_score": 70},
    {"name": "Datadog", "description": "Infrastructure monitoring", "website": "https://datadoghq.com", "tier": "medium", "category": "monitoring", "criticality_score": 55},
    {"name": "Notion", "description": "Team wiki and docs", "website": "https://notion.so", "tier": "low", "category": "collaboration", "criticality_score": 35},
    {"name": "Calendly", "description": "Scheduling platform", "website": "https://calendly.com", "tier": "low", "category": "productivity", "criticality_score": 25},
    {"name": "DocuSign", "description": "E-signatures", "website": "https://docusign.com", "tier": "low", "category": "legal", "criticality_score": 40},
]

DEMO_DOCUMENTS = [
    {"vendor": "Amazon Web Services (AWS)", "filename": "AWS_SOC2_Type_II_2025.pdf", "doc_type": "soc2", "pages": 156, "size": 4500000},
    {"vendor": "Amazon Web Services (AWS)", "filename": "AWS_ISO27001_Certificate.pdf", "doc_type": "iso27001", "pages": 12, "size": 850000},
    {"vendor": "Stripe", "filename": "Stripe_SOC2_Report_2025.pdf", "doc_type": "soc2", "pages": 89, "size": 3200000},
    {"vendor": "Stripe", "filename": "Stripe_PCI_DSS_AOC.pdf", "doc_type": "other", "pages": 24, "size": 1100000},
    {"vendor": "Okta", "filename": "Okta_SOC2_Report_2025.pdf", "doc_type": "soc2", "pages": 134, "size": 3800000},
    {"vendor": "Okta", "filename": "Okta_Pentest_Report_Q4.pdf", "doc_type": "pentest", "pages": 45, "size": 2100000},
    {"vendor": "Snowflake", "filename": "Snowflake_SOC2_Type_II.pdf", "doc_type": "soc2", "pages": 112, "size": 3400000},
    {"vendor": "Snowflake", "filename": "Snowflake_ISO27001_Cert.pdf", "doc_type": "iso27001", "pages": 8, "size": 650000},
    {"vendor": "OpenAI", "filename": "OpenAI_SOC2_Report.pdf", "doc_type": "soc2", "pages": 78, "size": 2900000},
    {"vendor": "OpenAI", "filename": "OpenAI_SIG_Core_2025.pdf", "doc_type": "sig_core", "pages": 245, "size": 1800000},
    {"vendor": "Zendesk", "filename": "Zendesk_SIG_Lite.pdf", "doc_type": "sig_lite", "pages": 32, "size": 980000},
    {"vendor": "Slack", "filename": "Slack_SOC2_Report.pdf", "doc_type": "soc2", "pages": 95, "size": 3100000},
    {"vendor": "GitHub", "filename": "GitHub_SOC2_Type_II.pdf", "doc_type": "soc2", "pages": 102, "size": 3500000},
    {"vendor": "GitHub", "filename": "GitHub_Pentest_Summary.pdf", "doc_type": "pentest", "pages": 28, "size": 1400000},
    {"vendor": "Datadog", "filename": "Datadog_ISO27001_Cert.pdf", "doc_type": "iso27001", "pages": 6, "size": 520000},
    {"vendor": "Notion", "filename": "Notion_SIG_Lite.pdf", "doc_type": "sig_lite", "pages": 28, "size": 890000},
    {"vendor": "DocuSign", "filename": "DocuSign_SIG_Core.pdf", "doc_type": "sig_core", "pages": 198, "size": 1650000},
]

DEMO_FINDINGS = [
    # CRITICAL
    {"title": "Missing MFA for Admin Access", "severity": "critical", "framework": "soc2", "control": "CC6.1", "desc": "Administrative access lacks multi-factor authentication."},
    {"title": "Encryption at Rest Not Implemented", "severity": "critical", "framework": "pci_dss", "control": "3.4", "desc": "Customer data not encrypted at rest."},
    {"title": "No Incident Response Plan", "severity": "critical", "framework": "iso27001", "control": "A.16.1", "desc": "Missing documented incident response procedures."},
    # HIGH
    {"title": "Outdated TLS Version", "severity": "high", "framework": "soc2", "control": "CC6.7", "desc": "TLS 1.0/1.1 still enabled on API endpoints."},
    {"title": "Insufficient Access Logging", "severity": "high", "framework": "soc2", "control": "CC7.2", "desc": "Access logs missing source IP and user agent."},
    {"title": "Undisclosed Subprocessor", "severity": "high", "framework": "iso27001", "control": "A.15.1", "desc": "Third-party data processor not disclosed."},
    {"title": "Weak Password Policy", "severity": "high", "framework": "soc2", "control": "CC6.1", "desc": "6-character minimum without complexity."},
    {"title": "No Data Retention Policy", "severity": "high", "framework": "iso27001", "control": "A.8.3", "desc": "No documented data retention schedule."},
    {"title": "Missing BCP/DR Plan", "severity": "high", "framework": "soc2", "control": "A1.2", "desc": "No business continuity plan available."},
    {"title": "Unpatched Vulnerabilities", "severity": "high", "framework": "soc2", "control": "CC7.1", "desc": "3 high-severity CVEs unpatched 90+ days."},
    # MEDIUM
    {"title": "Session Timeout Too Long", "severity": "medium", "framework": "soc2", "control": "CC6.1", "desc": "24-hour session timeout without re-auth."},
    {"title": "No Security Training", "severity": "medium", "framework": "iso27001", "control": "A.7.2", "desc": "Missing security awareness program."},
    {"title": "No API Rate Limiting", "severity": "medium", "framework": "soc2", "control": "CC6.6", "desc": "APIs lack rate limiting."},
    {"title": "Incomplete Audit Trail", "severity": "medium", "framework": "soc2", "control": "CC7.2", "desc": "Data modifications not logged."},
    {"title": "No Vulnerability Disclosure", "severity": "medium", "framework": "iso27001", "control": "A.12.6", "desc": "No public VDP or bug bounty."},
    {"title": "Background Checks Missing", "severity": "medium", "framework": "soc2", "control": "CC1.4", "desc": "No documented background check process."},
    {"title": "IDOR Vulnerability", "severity": "medium", "framework": "soc2", "control": "CC6.1", "desc": "Insecure direct object references found."},
    {"title": "Wildcard CORS", "severity": "medium", "framework": "soc2", "control": "CC6.6", "desc": "Access-Control-Allow-Origin: * header."},
    {"title": "Tokens in URL", "severity": "medium", "framework": "pci_dss", "control": "4.2", "desc": "Sensitive data in URL parameters."},
    {"title": "No Change Management", "severity": "medium", "framework": "soc2", "control": "CC8.1", "desc": "Missing formal change approval process."},
    {"title": "No Data Classification", "severity": "medium", "framework": "iso27001", "control": "A.8.2", "desc": "No data classification scheme."},
    {"title": "Flat Network", "severity": "medium", "framework": "pci_dss", "control": "1.3", "desc": "Production and dev share network."},
    # LOW
    {"title": "Missing Security Headers", "severity": "low", "framework": "soc2", "control": "CC6.6", "desc": "X-Content-Type-Options missing."},
    {"title": "Verbose Error Messages", "severity": "low", "framework": "soc2", "control": "CC6.1", "desc": "Stack traces in error responses."},
    {"title": "Cookie Missing Secure Flag", "severity": "low", "framework": "soc2", "control": "CC6.7", "desc": "Session cookie lacks Secure flag."},
    {"title": "No Privacy Policy Version", "severity": "low", "framework": "iso27001", "control": "A.18.1", "desc": "Privacy policy lacks versioning."},
    {"title": "Example Credentials in Docs", "severity": "low", "framework": "soc2", "control": "CC6.1", "desc": "Default creds in API docs."},
    {"title": "Missing SRI", "severity": "low", "framework": "soc2", "control": "CC6.6", "desc": "No subresource integrity hashes."},
    {"title": "Inconsistent Log Format", "severity": "low", "framework": "soc2", "control": "CC7.2", "desc": "Mixed date formats in logs."},
    {"title": "SSL Cert Expiring Soon", "severity": "low", "framework": "soc2", "control": "CC6.7", "desc": "Certificate expires in 22 days."},
]


@router.post("/seed-demo-data", response_model=SeedResponse)
async def seed_demo_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SeedResponse:
    """Seed demo data for the current user's organization.

    This endpoint populates the database with realistic vendor,
    document, and finding data for demonstration purposes.
    """
    org_id = current_user.organization_id

    # Clear existing data
    # Delete findings first
    result = await db.execute(select(Finding).where(Finding.organization_id == org_id))
    for finding in result.scalars().all():
        await db.delete(finding)

    # Delete analysis runs
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.organization_id == org_id))
    for run in result.scalars().all():
        await db.delete(run)

    # Delete chunks (need to get document IDs first)
    result = await db.execute(select(Document).where(Document.organization_id == org_id))
    docs_to_delete = result.scalars().all()
    for doc in docs_to_delete:
        chunk_result = await db.execute(select(DocumentChunk).where(DocumentChunk.document_id == doc.id))
        for chunk in chunk_result.scalars().all():
            await db.delete(chunk)

    # Delete documents
    result = await db.execute(select(Document).where(Document.organization_id == org_id))
    for doc in result.scalars().all():
        await db.delete(doc)

    # Delete vendors
    result = await db.execute(select(Vendor).where(Vendor.organization_id == org_id))
    for vendor in result.scalars().all():
        await db.delete(vendor)

    await db.commit()

    # Create vendors
    vendor_map = {}
    for v in DEMO_VENDORS:
        vendor = Vendor(
            id=str(uuid4()),
            organization_id=org_id,
            name=v["name"],
            description=v["description"],
            website=v["website"],
            tier=v["tier"],
            status=VendorStatus.ACTIVE.value,
            category=v["category"],
            criticality_score=v["criticality_score"],
            data_classification="sensitive" if v["tier"] in ["critical", "high"] else "internal",
            recommended_frameworks=json.dumps(["soc2", "iso27001"]),
            data_types=json.dumps(["customer_data", "credentials"]),
            categorization_confidence=0.92,
            last_assessed=datetime.now(timezone.utc) - timedelta(days=random.randint(10, 90)),
            risk_score=random.uniform(60, 95) if v["tier"] == "critical" else random.uniform(30, 70),
            risk_calculated_at=datetime.now(timezone.utc),
        )
        db.add(vendor)
        vendor_map[v["name"]] = vendor

    await db.commit()

    # Create documents with chunks
    documents = []
    chunks_created = 0
    doc_chunks_map = {}  # Map document ID to its chunks for later use

    for d in DEMO_DOCUMENTS:
        vendor = vendor_map.get(d["vendor"])
        if not vendor:
            continue

        doc_id = str(uuid4())
        doc = Document(
            id=doc_id,
            organization_id=org_id,
            vendor_id=vendor.id,
            filename=d["filename"],
            storage_path=f"documents/{org_id}/{d['filename']}",
            file_size=d["size"],
            mime_type="application/pdf",
            document_type=d["doc_type"],
            status=DocumentStatus.PROCESSED.value,
            processing_stage=ProcessingStage.COMPLETED.value,
            page_count=d["pages"],
            processed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
        )
        db.add(doc)
        documents.append(doc)

        # Get content based on document type and vendor name
        # Map doc_type to content type
        content_type_map = {
            "soc2": "soc2",
            "iso27001": "iso27001",
            "pentest": "pentest",
            "sig_core": "sig_core",
            "sig_lite": "sig_lite",
            "other": "soc2",  # Default to soc2 for other types
        }
        content_type = content_type_map.get(d["doc_type"], "soc2")
        vendor_name = vendor.name.split(" (")[0]  # Remove "(AWS)" etc.

        # Get realistic document content
        content_sections = get_document_content(content_type, vendor_name)
        doc_chunks = []

        for idx, section in enumerate(content_sections):
            chunk = DocumentChunk(
                id=str(uuid4()),
                document_id=doc_id,
                content=section["content"],
                token_count=len(section["content"].split()) * 4 // 3,  # Rough token estimate
                chunk_index=idx,
                page_number=section["page_number"],
                section_header=section["section_header"],
                embedding=None,  # No embedding for demo data
                metadata_=json.dumps({
                    "source": d["filename"],
                    "vendor": vendor.name,
                    "doc_type": d["doc_type"],
                }),
            )
            db.add(chunk)
            doc_chunks.append(chunk)
            chunks_created += 1

        doc_chunks_map[doc_id] = doc_chunks

    await db.commit()

    # Create analysis runs
    runs = []
    for doc in documents[:8]:
        run = AnalysisRun(
            id=str(uuid4()),
            organization_id=org_id,
            document_id=doc.id,
            framework=random.choice(["soc2", "iso27001", "pci_dss"]),
            model_used="claude-3-5-sonnet-20241022",
            status="completed",
            chunks_analyzed=random.randint(20, 80),
            findings_count=random.randint(2, 8),
            input_tokens=random.randint(50000, 150000),
            output_tokens=random.randint(5000, 15000),
            started_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(24, 72)),
            completed_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24)),
            summary=f"Analysis completed for {doc.filename}. Multiple control gaps identified.",
        )
        db.add(run)
        runs.append(run)

    await db.commit()

    # Create findings linked to actual chunks
    findings_created = 0
    for f in DEMO_FINDINGS:
        if not runs:
            break
        run = random.choice(runs)

        # Get a random chunk from this document for citation
        doc_chunks = doc_chunks_map.get(run.document_id, [])
        cited_chunk = random.choice(doc_chunks) if doc_chunks else None

        # Create detailed evidence based on chunk content
        evidence_text = "Identified during document analysis."
        if cited_chunk:
            # Extract a snippet from the chunk content for evidence
            content_snippet = cited_chunk.content[:300] + "..." if len(cited_chunk.content) > 300 else cited_chunk.content
            evidence_text = f"Found in section '{cited_chunk.section_header}': \"{content_snippet}\""

        finding = Finding(
            id=str(uuid4()),
            analysis_run_id=run.id,
            document_id=run.document_id,
            organization_id=org_id,
            title=f["title"],
            severity=f["severity"],
            status=random.choice([FindingStatus.OPEN.value, FindingStatus.OPEN.value, FindingStatus.ACKNOWLEDGED.value]),
            framework=f["framework"],
            framework_control=f["control"],
            description=f["desc"],
            evidence=evidence_text,
            remediation="Implement appropriate controls to address this finding.",
            impact="Security posture affected until remediated.",
            confidence_score=random.uniform(0.75, 0.98),
            chunk_id=cited_chunk.id if cited_chunk else None,
            page_number=cited_chunk.page_number if cited_chunk else random.randint(1, 15),
            section_header=cited_chunk.section_header if cited_chunk else None,
        )
        db.add(finding)
        findings_created += 1

    await db.commit()

    return SeedResponse(
        success=True,
        message="Demo data seeded successfully",
        vendors_created=len(vendor_map),
        documents_created=len(documents),
        chunks_created=chunks_created,
        analysis_runs_created=len(runs),
        findings_created=findings_created,
    )


@router.delete("/clear-demo-data")
async def clear_demo_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Clear all demo data for the current user's organization."""
    org_id = current_user.organization_id

    # Delete in order due to foreign keys
    result = await db.execute(select(Finding).where(Finding.organization_id == org_id))
    findings_count = 0
    for finding in result.scalars().all():
        await db.delete(finding)
        findings_count += 1

    result = await db.execute(select(AnalysisRun).where(AnalysisRun.organization_id == org_id))
    runs_count = 0
    for run in result.scalars().all():
        await db.delete(run)
        runs_count += 1

    # Delete chunks first (before documents)
    result = await db.execute(select(Document).where(Document.organization_id == org_id))
    chunks_count = 0
    docs_to_delete = result.scalars().all()
    for doc in docs_to_delete:
        chunk_result = await db.execute(select(DocumentChunk).where(DocumentChunk.document_id == doc.id))
        for chunk in chunk_result.scalars().all():
            await db.delete(chunk)
            chunks_count += 1

    # Now delete documents
    result = await db.execute(select(Document).where(Document.organization_id == org_id))
    docs_count = 0
    for doc in result.scalars().all():
        await db.delete(doc)
        docs_count += 1

    result = await db.execute(select(Vendor).where(Vendor.organization_id == org_id))
    vendors_count = 0
    for vendor in result.scalars().all():
        await db.delete(vendor)
        vendors_count += 1

    await db.commit()

    return {
        "success": True,
        "message": "Demo data cleared",
        "deleted": {
            "vendors": vendors_count,
            "documents": docs_count,
            "chunks": chunks_count,
            "analysis_runs": runs_count,
            "findings": findings_count,
        }
    }
