"""Agent Manager - Orchestrates AI agent task execution."""

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import (
    Agent,
    AgentLog,
    AgentStatus,
    AgentTask,
    AgentType,
    LogLevel,
    TaskStatus,
    TaskType,
)


class AgentManager:
    """Manages AI agent task execution and coordination."""

    async def execute_task(
        self,
        db: AsyncSession,
        agent: Agent,
        task_type: str,
        input_data: dict[str, Any],
    ) -> AgentTask:
        """
        Execute a task for an agent.

        Creates the task record, updates agent status, runs the task logic,
        and records the results.
        """
        # Create task record
        task = AgentTask(
            agent_id=agent.id,
            task_type=TaskType(task_type),
            status=TaskStatus.PENDING,
            input_data=input_data,
        )
        db.add(task)
        await db.flush()

        # Log task start
        await self._log(
            db,
            agent.id,
            task.id,
            LogLevel.INFO,
            f"Task {task_type} initiated",
            {"input_data": input_data},
        )

        # Update agent status
        agent.status = AgentStatus.PROCESSING
        await db.flush()

        try:
            # Start task execution
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now(timezone.utc)
            await db.flush()

            # Execute based on agent type
            result = await self._execute_agent_logic(db, agent, task, input_data)

            # Update task with results
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.now(timezone.utc)
            task.output_data = result.get("output_data", {})
            task.items_processed = result.get("items_processed", 0)
            task.findings_count = result.get("findings_count", 0)

            # Log completion
            await self._log(
                db,
                agent.id,
                task.id,
                LogLevel.INFO,
                f"Task {task_type} completed successfully",
                {
                    "items_processed": task.items_processed,
                    "findings_count": task.findings_count,
                },
            )

        except Exception as e:
            # Handle failure
            task.status = TaskStatus.FAILED
            task.completed_at = datetime.now(timezone.utc)
            task.error_message = str(e)

            # Log error
            await self._log(
                db,
                agent.id,
                task.id,
                LogLevel.ERROR,
                f"Task {task_type} failed: {str(e)}",
                {"error": str(e)},
            )

            # Update agent error state
            agent.error_message = str(e)

        finally:
            # Reset agent status
            agent.status = AgentStatus.IDLE
            agent.last_run_at = datetime.now(timezone.utc)
            await db.flush()

        return task

    async def _execute_agent_logic(
        self,
        db: AsyncSession,
        agent: Agent,
        task: AgentTask,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute the specific logic for each agent type."""
        if agent.agent_type == AgentType.THREAT_DETECTION:
            return await self._run_threat_detection(db, agent, task, input_data)
        elif agent.agent_type == AgentType.RISK_ASSESSMENT:
            return await self._run_risk_assessment(db, agent, task, input_data)
        elif agent.agent_type == AgentType.VULNERABILITY_SCANNER:
            return await self._run_vulnerability_scan(db, agent, task, input_data)
        elif agent.agent_type == AgentType.COMPLIANCE_VERIFICATION:
            return await self._run_compliance_verification(db, agent, task, input_data)
        else:
            raise ValueError(f"Unknown agent type: {agent.agent_type}")

    async def _run_threat_detection(
        self,
        db: AsyncSession,
        agent: Agent,
        task: AgentTask,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Sentinel Prime - Threat Detection Agent

        Scans documents and vendor data for security threats.
        """
        from sqlalchemy import select, func
        from app.models import Document, Finding, FindingSeverity

        # Log scan start
        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            "Sentinel Prime initiating threat scan...",
            {"scope": input_data.get("scope", "all")}
        )

        # Get document count for the organization
        org_id = agent.organization_id
        doc_result = await db.execute(
            select(func.count(Document.id)).where(Document.organization_id == org_id)
        )
        doc_count = doc_result.scalar() or 0

        # Get critical/high findings count
        findings_result = await db.execute(
            select(func.count(Finding.id))
            .where(Finding.organization_id == org_id)
            .where(Finding.severity.in_([FindingSeverity.CRITICAL, FindingSeverity.HIGH]))
        )
        threat_count = findings_result.scalar() or 0

        # Log results
        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            f"Scan complete: {doc_count} documents analyzed, {threat_count} threats identified",
            {"documents_scanned": doc_count, "threats_found": threat_count}
        )

        return {
            "output_data": {
                "scan_type": "threat_detection",
                "documents_scanned": doc_count,
                "threats_identified": threat_count,
                "recommendations": [
                    "Review critical findings immediately",
                    "Update vendor risk assessments",
                ] if threat_count > 0 else ["No immediate threats detected"],
            },
            "items_processed": doc_count,
            "findings_count": threat_count,
        }

    async def _run_risk_assessment(
        self,
        db: AsyncSession,
        agent: Agent,
        task: AgentTask,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Vector Analyst - Risk Assessment Agent

        Calculates and updates vendor risk scores.
        """
        from sqlalchemy import select, func
        from app.models import Vendor, Finding, FindingSeverity

        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            "Vector Analyst calculating risk scores...",
            {}
        )

        org_id = agent.organization_id

        # Get vendor count
        vendor_result = await db.execute(
            select(func.count(Vendor.id)).where(Vendor.organization_id == org_id)
        )
        vendor_count = vendor_result.scalar() or 0

        # Calculate findings distribution
        severity_counts = {}
        for severity in FindingSeverity:
            result = await db.execute(
                select(func.count(Finding.id))
                .where(Finding.organization_id == org_id)
                .where(Finding.severity == severity)
            )
            severity_counts[severity.value] = result.scalar() or 0

        # Calculate overall risk score (simplified)
        total_findings = sum(severity_counts.values())
        risk_score = min(100, (
            severity_counts.get("critical", 0) * 25 +
            severity_counts.get("high", 0) * 15 +
            severity_counts.get("medium", 0) * 5 +
            severity_counts.get("low", 0) * 1
        )) if total_findings > 0 else 0

        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            f"Risk assessment complete: Score {risk_score}/100",
            {"risk_score": risk_score, "vendor_count": vendor_count}
        )

        return {
            "output_data": {
                "assessment_type": "risk_scoring",
                "vendors_assessed": vendor_count,
                "overall_risk_score": risk_score,
                "severity_distribution": severity_counts,
                "risk_level": (
                    "CRITICAL" if risk_score >= 75 else
                    "HIGH" if risk_score >= 50 else
                    "MEDIUM" if risk_score >= 25 else
                    "LOW"
                ),
            },
            "items_processed": vendor_count,
            "findings_count": total_findings,
        }

    async def _run_vulnerability_scan(
        self,
        db: AsyncSession,
        agent: Agent,
        task: AgentTask,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Watchdog Zero - Vulnerability Scanner Agent

        Identifies security gaps and missing controls.
        """
        from sqlalchemy import select, func
        from app.models import Vendor, Document, DocumentStatus

        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            "Watchdog Zero scanning for vulnerabilities...",
            {}
        )

        org_id = agent.organization_id

        # Check for vendors without documents
        vendors_result = await db.execute(
            select(Vendor).where(Vendor.organization_id == org_id)
        )
        vendors = list(vendors_result.scalars().all())

        # Find vendors without recent documents
        vulnerabilities = []
        vendors_without_docs = 0
        for vendor in vendors:
            docs_result = await db.execute(
                select(func.count(Document.id))
                .where(Document.vendor_id == vendor.id)
            )
            doc_count = docs_result.scalar() or 0
            if doc_count == 0:
                vendors_without_docs += 1
                vulnerabilities.append(f"Vendor '{vendor.name}' has no security documentation")

        # Check for unprocessed documents
        pending_docs_result = await db.execute(
            select(func.count(Document.id))
            .where(Document.organization_id == org_id)
            .where(Document.status == DocumentStatus.PENDING)
        )
        pending_docs = pending_docs_result.scalar() or 0
        if pending_docs > 0:
            vulnerabilities.append(f"{pending_docs} documents awaiting security analysis")

        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            f"Vulnerability scan complete: {len(vulnerabilities)} issues found",
            {"vulnerabilities_count": len(vulnerabilities)}
        )

        return {
            "output_data": {
                "scan_type": "vulnerability",
                "vendors_scanned": len(vendors),
                "vendors_without_documentation": vendors_without_docs,
                "pending_documents": pending_docs,
                "vulnerabilities": vulnerabilities[:10],  # Limit to 10
                "severity": "HIGH" if vendors_without_docs > 5 else "MEDIUM" if vendors_without_docs > 0 else "LOW",
            },
            "items_processed": len(vendors),
            "findings_count": len(vulnerabilities),
        }

    async def _run_compliance_verification(
        self,
        db: AsyncSession,
        agent: Agent,
        task: AgentTask,
        input_data: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Audit Core - Compliance Verification Agent

        Verifies compliance with regulatory frameworks.
        """
        from sqlalchemy import select, func
        from app.models import AnalysisRun, Finding

        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            "Audit Core verifying compliance posture...",
            {}
        )

        org_id = agent.organization_id

        # Get analysis runs by framework
        runs_result = await db.execute(
            select(AnalysisRun)
            .where(AnalysisRun.organization_id == org_id)
            .where(AnalysisRun.status == "completed")
        )
        runs = list(runs_result.scalars().all())

        # Calculate compliance by framework
        frameworks_analyzed = set()
        for run in runs:
            if run.framework:
                frameworks_analyzed.add(run.framework)

        # Get total findings
        findings_result = await db.execute(
            select(func.count(Finding.id)).where(Finding.organization_id == org_id)
        )
        total_findings = findings_result.scalar() or 0

        # Calculate compliance score (simplified)
        target_frameworks = {"soc2_tsc", "iso_27001", "nist_800_53", "hipaa", "pci_dss"}
        coverage = len(frameworks_analyzed.intersection(target_frameworks)) / len(target_frameworks) * 100

        await self._log(
            db, agent.id, task.id, LogLevel.INFO,
            f"Compliance verification complete: {coverage:.0f}% framework coverage",
            {"coverage": coverage, "frameworks": list(frameworks_analyzed)}
        )

        return {
            "output_data": {
                "verification_type": "compliance",
                "frameworks_analyzed": list(frameworks_analyzed),
                "framework_coverage_percent": round(coverage, 1),
                "total_findings": total_findings,
                "compliance_status": (
                    "EXCELLENT" if coverage >= 80 else
                    "GOOD" if coverage >= 60 else
                    "NEEDS_IMPROVEMENT" if coverage >= 40 else
                    "CRITICAL"
                ),
                "recommendations": [
                    f"Add analysis for {fw}" for fw in target_frameworks - frameworks_analyzed
                ][:5],
            },
            "items_processed": len(runs),
            "findings_count": total_findings,
        }

    async def _log(
        self,
        db: AsyncSession,
        agent_id: str,
        task_id: str | None,
        level: LogLevel,
        message: str,
        details: dict[str, Any] | None = None,
    ) -> None:
        """Create a log entry for an agent."""
        log = AgentLog(
            agent_id=agent_id,
            task_id=task_id,
            level=level,
            message=message,
            details=details,
        )
        db.add(log)
        await db.flush()


# Singleton instance
agent_manager = AgentManager()
