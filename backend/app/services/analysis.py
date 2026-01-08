"""Analysis service for document compliance analysis."""

from datetime import datetime, timezone
from typing import List, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.models.chunk import DocumentChunk
from app.models.finding import AnalysisRun, Finding, FindingSeverity
from app.services.llm import get_claude_service, SUPPORTED_FRAMEWORKS
from app.services.search import get_search_service


async def get_analysis_run_by_id(
    db: AsyncSession,
    run_id: str,
    org_id: str,
) -> AnalysisRun | None:
    """Get an analysis run by ID."""
    result = await db.execute(
        select(AnalysisRun).where(
            AnalysisRun.id == run_id,
            AnalysisRun.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def get_analysis_runs(
    db: AsyncSession,
    org_id: str,
    document_id: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[AnalysisRun], int]:
    """List analysis runs with pagination."""
    query = select(AnalysisRun).where(AnalysisRun.organization_id == org_id)

    if document_id:
        query = query.where(AnalysisRun.document_id == document_id)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.order_by(AnalysisRun.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    runs = list(result.scalars().all())

    return runs, total


async def get_findings(
    db: AsyncSession,
    org_id: str,
    document_id: str | None = None,
    analysis_run_id: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[Finding], int]:
    """List findings with pagination and filtering."""
    query = select(Finding).where(Finding.organization_id == org_id)

    if document_id:
        query = query.where(Finding.document_id == document_id)
    if analysis_run_id:
        query = query.where(Finding.analysis_run_id == analysis_run_id)
    if severity:
        query = query.where(Finding.severity == severity)
    if status:
        query = query.where(Finding.status == status)

    # Count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Paginate
    query = query.order_by(
        # Sort by severity (critical first)
        func.field(Finding.severity, "critical", "high", "medium", "low", "info"),
        Finding.created_at.desc(),
    ).offset(skip).limit(limit)

    result = await db.execute(query)
    findings = list(result.scalars().all())

    return findings, total


async def get_finding_by_id(
    db: AsyncSession,
    finding_id: str,
    org_id: str,
) -> Finding | None:
    """Get a finding by ID."""
    result = await db.execute(
        select(Finding).where(
            Finding.id == finding_id,
            Finding.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def update_finding(
    db: AsyncSession,
    finding_id: str,
    org_id: str,
    update_data: dict,
) -> Finding | None:
    """Update a finding."""
    finding = await get_finding_by_id(db, finding_id, org_id)
    if not finding:
        return None

    for field, value in update_data.items():
        if value is not None:
            setattr(finding, field, value)

    # Track resolution
    if update_data.get("status") in ["remediated", "accepted", "false_positive"]:
        finding.resolved_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(finding)
    return finding


async def run_analysis(
    db: AsyncSession,
    document_id: str,
    org_id: str,
    framework: str,
    chunk_limit: int = 50,
) -> AnalysisRun:
    """Run compliance analysis on a document.

    Args:
        db: Database session
        document_id: Document to analyze
        org_id: Organization ID
        framework: Compliance framework
        chunk_limit: Maximum chunks to analyze

    Returns:
        AnalysisRun with results

    Raises:
        ValueError: If document not found or analysis fails
    """
    # Validate framework
    if framework not in SUPPORTED_FRAMEWORKS:
        raise ValueError(f"Unsupported framework: {framework}")

    # Get document
    doc_result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == org_id,
        )
    )
    document = doc_result.scalar_one_or_none()
    if not document:
        raise ValueError("Document not found")

    if not document.is_processed:
        raise ValueError("Document must be processed before analysis")

    # Get Claude service
    claude_service = get_claude_service()
    if not claude_service.is_configured:
        raise ValueError("Anthropic API key not configured")

    # Create analysis run
    analysis_run = AnalysisRun(
        organization_id=org_id,
        document_id=document_id,
        framework=framework,
        model_used=claude_service.model,
        status="running",
        started_at=datetime.now(timezone.utc),
    )
    db.add(analysis_run)
    await db.flush()

    try:
        # Get document chunks
        chunks_result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .limit(chunk_limit)
        )
        chunks = list(chunks_result.scalars().all())

        if not chunks:
            raise ValueError("Document has no chunks to analyze")

        analysis_run.chunks_analyzed = len(chunks)

        # Prepare chunks for analysis
        chunk_data = [
            {
                "id": chunk.id,
                "content": chunk.content,
                "section_header": chunk.section_header,
                "page_number": chunk.page_number,
            }
            for chunk in chunks
        ]

        # Run analysis
        result = await claude_service.analyze_document(
            chunks=chunk_data,
            framework=framework,
            document_type=document.document_type,
        )

        # Update metrics
        analysis_run.input_tokens = result.input_tokens
        analysis_run.output_tokens = result.output_tokens
        analysis_run.summary = result.summary

        # Create findings
        findings_created = 0
        for finding_data in result.findings:
            finding = Finding(
                analysis_run_id=analysis_run.id,
                document_id=document_id,
                organization_id=org_id,
                title=finding_data.get("title", "Untitled Finding"),
                severity=finding_data.get("severity", "medium"),
                framework=framework,
                framework_control=finding_data.get("framework_control"),
                description=finding_data.get("description", ""),
                evidence=finding_data.get("evidence"),
                remediation=finding_data.get("remediation"),
                confidence_score=finding_data.get("confidence"),
            )
            db.add(finding)
            findings_created += 1

        analysis_run.findings_count = findings_created
        analysis_run.status = "completed"
        analysis_run.completed_at = datetime.now(timezone.utc)

        await db.flush()
        await db.refresh(analysis_run)
        return analysis_run

    except Exception as e:
        analysis_run.status = "failed"
        analysis_run.error_message = str(e)
        analysis_run.completed_at = datetime.now(timezone.utc)
        await db.flush()
        raise ValueError(f"Analysis failed: {str(e)}")


async def get_finding_summary(
    db: AsyncSession,
    org_id: str,
    document_id: str | None = None,
) -> dict:
    """Get summary of findings by severity and status."""
    query = select(Finding).where(Finding.organization_id == org_id)

    if document_id:
        query = query.where(Finding.document_id == document_id)

    result = await db.execute(query)
    findings = list(result.scalars().all())

    summary = {
        "total": len(findings),
        "critical": 0,
        "high": 0,
        "medium": 0,
        "low": 0,
        "info": 0,
        "open": 0,
        "resolved": 0,
    }

    for finding in findings:
        if finding.severity in summary:
            summary[finding.severity] += 1

        if finding.is_open:
            summary["open"] += 1
        else:
            summary["resolved"] += 1

    return summary
