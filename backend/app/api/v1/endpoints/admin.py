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
from app.models.agent import Agent, AgentTask, AgentLog, TaskStatus, TaskType, LogLevel
from app.models.audit_log import AuditLog, AuditAction
from app.models.playbook import AIPlaybook, PlaybookStep
from app.data.playbooks.defaults import DEFAULT_PLAYBOOKS  # Direct import to bypass broken __init__
from app.models.chunk import DocumentChunk
from app.models.document import Document, DocumentStatus, DocumentType, ProcessingStage
from app.models.finding import AnalysisRun, Finding, FindingSeverity, FindingStatus
from app.models.monitoring import (
    MonitoringSchedule, ScheduledRun, AlertRule, Alert, NotificationChannel,
    ScheduleFrequency, ScheduleStatus, AlertSeverity, AlertStatus, NotificationChannelType
)
from app.models.query import ConversationThread, QueryHistory, QueryStatus
from app.models.remediation import RemediationTask, RemediationComment, SLAPolicy, RemediationStatus, RemediationPriority
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
    remediation_tasks_created: int = 0
    remediation_comments_created: int = 0
    sla_policies_created: int = 0
    schedules_created: int = 0
    scheduled_runs_created: int = 0
    alert_rules_created: int = 0
    alerts_created: int = 0
    notification_channels_created: int = 0
    audit_logs_created: int = 0
    agent_tasks_created: int = 0
    agent_logs_created: int = 0
    conversations_created: int = 0
    queries_created: int = 0
    playbooks_created: int = 0
    playbook_steps_created: int = 0


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

# Remediation demo data
DEMO_SLA_POLICIES = [
    {"name": "Default SLA Policy", "critical_days": 3, "high_days": 7, "medium_days": 30, "low_days": 90, "is_default": True},
    {"name": "Expedited SLA Policy", "critical_days": 1, "high_days": 3, "medium_days": 14, "low_days": 30, "is_default": False},
]

DEMO_REMEDIATION_TASKS = [
    {"title": "Implement MFA for Admin Access", "status": "in_progress", "priority": "critical", "sla_days": 3},
    {"title": "Deploy Encryption at Rest Solution", "status": "in_progress", "priority": "critical", "sla_days": 3},
    {"title": "Create Incident Response Plan", "status": "assigned", "priority": "critical", "sla_days": 3},
    {"title": "Upgrade TLS Configuration", "status": "in_progress", "priority": "high", "sla_days": 7},
    {"title": "Enhance Access Logging", "status": "pending_review", "priority": "high", "sla_days": 7},
    {"title": "Update Subprocessor Disclosure", "status": "assigned", "priority": "high", "sla_days": 7},
    {"title": "Strengthen Password Policy", "status": "pending_assignment", "priority": "high", "sla_days": 7},
    {"title": "Document Data Retention Policy", "status": "pending_review", "priority": "medium", "sla_days": 30},
    {"title": "Develop BCP/DR Plan", "status": "pending_assignment", "priority": "medium", "sla_days": 30},
    {"title": "Patch Critical Vulnerabilities", "status": "pending_verification", "priority": "high", "sla_days": 7},
    {"title": "Configure Session Timeouts", "status": "verified", "priority": "medium", "sla_days": 30},
    {"title": "Implement Security Training", "status": "verified", "priority": "medium", "sla_days": 30},
    {"title": "Add API Rate Limiting", "status": "closed", "priority": "low", "sla_days": 90},
    {"title": "Add Security Headers", "status": "closed", "priority": "low", "sla_days": 90},
    {"title": "Fix Verbose Errors", "status": "draft", "priority": "low", "sla_days": 90},
]

DEMO_TASK_COMMENTS = [
    "Initial assessment completed. This is a critical priority item.",
    "Reviewing vendor documentation for compliance requirements.",
    "Implementation plan drafted and awaiting approval.",
    "Technical team assigned to work on this task.",
    "Progress update: 50% complete, on track for deadline.",
    "Awaiting additional information from vendor.",
    "Testing in progress, initial results look promising.",
    "Escalated to security team for review.",
    "Blocked: waiting for infrastructure team availability.",
    "Completed internal review, ready for verification.",
    "Successfully deployed to staging environment.",
    "Final testing completed, ready for production.",
    "Verified in production, closing task.",
    "Documentation updated with new procedures.",
    "Training materials prepared for team.",
]

# Monitoring demo data
DEMO_SCHEDULES = [
    {"name": "Weekly SOC 2 Compliance Check", "frequency": "weekly", "status": "active", "framework": "soc2"},
    {"name": "Monthly ISO 27001 Assessment", "frequency": "monthly", "status": "active", "framework": "iso27001"},
    {"name": "Bi-weekly Vendor Risk Review", "frequency": "biweekly", "status": "paused", "framework": None},
    {"name": "Daily Security Posture Monitor", "frequency": "daily", "status": "active", "framework": None},
    {"name": "Quarterly PCI DSS Audit", "frequency": "quarterly", "status": "active", "framework": "pci_dss"},
]

DEMO_ALERT_RULES = [
    {"name": "Critical Finding Detected", "trigger_type": "finding_severity", "severity": "critical", "threshold": 1},
    {"name": "SLA Breach Warning", "trigger_type": "sla_breach", "severity": "high", "threshold": 1},
    {"name": "Document Processing Failed", "trigger_type": "processing_error", "severity": "medium", "threshold": 3},
    {"name": "High Risk Vendor Detected", "trigger_type": "risk_threshold", "severity": "high", "threshold": 85},
    {"name": "Compliance Gap Identified", "trigger_type": "compliance_gap", "severity": "medium", "threshold": 2},
]

DEMO_ALERTS = [
    {"title": "Critical SQL Injection Finding", "status": "new", "severity": "critical", "message": "SQL injection vulnerability identified in Stripe API integration."},
    {"title": "SLA Breach: Admin MFA Task", "status": "new", "severity": "high", "message": "Remediation task 'Implement MFA for Admin Access' has exceeded SLA."},
    {"title": "High Risk Score: AWS", "status": "new", "severity": "high", "message": "AWS vendor risk score increased to 92, exceeding threshold."},
    {"title": "Document Upload Failed", "status": "acknowledged", "severity": "medium", "message": "Failed to process Okta_SOC2_Report.pdf after 3 attempts."},
    {"title": "Multiple Medium Findings", "status": "acknowledged", "severity": "medium", "message": "5 new medium severity findings detected in latest analysis."},
    {"title": "SLA Warning: TLS Upgrade", "status": "acknowledged", "severity": "high", "message": "TLS upgrade task approaching SLA deadline (2 days remaining)."},
    {"title": "Compliance Gap: Access Controls", "status": "acknowledged", "severity": "low", "message": "Minor gap identified in access control documentation."},
    {"title": "New Vendor Assessment Due", "status": "in_progress", "severity": "medium", "message": "OpenAI vendor assessment due in 14 days."},
    {"title": "Subprocessor Change Detected", "status": "in_progress", "severity": "medium", "message": "Snowflake added new subprocessor requiring review."},
    {"title": "Backup Verification Needed", "status": "in_progress", "severity": "low", "message": "Quarterly backup verification for GitHub integration due."},
    {"title": "Resolved: Encryption Finding", "status": "resolved", "severity": "high", "message": "Encryption at rest finding has been remediated."},
    {"title": "Resolved: Access Logging", "status": "resolved", "severity": "medium", "message": "Access logging gaps have been addressed."},
]

DEMO_NOTIFICATION_CHANNELS = [
    {"name": "Security Team Email", "channel_type": "email", "status": "active", "config": {"email": "security@company.com"}},
    {"name": "#security-alerts Slack", "channel_type": "slack", "status": "active", "config": {"webhook_url": "https://hooks.slack.com/services/xxx"}},
    {"name": "PagerDuty Webhook", "channel_type": "webhook", "status": "inactive", "config": {"url": "https://events.pagerduty.com/integration/xxx"}},
]

# Audit log demo data
DEMO_AUDIT_ACTIONS = [
    {"action": "LOGIN", "resource_type": "session", "details": "User logged in successfully"},
    {"action": "LOGIN", "resource_type": "session", "details": "User logged in from new device"},
    {"action": "CREATE", "resource_type": "vendor", "details": "Created new vendor: Stripe"},
    {"action": "CREATE", "resource_type": "vendor", "details": "Created new vendor: AWS"},
    {"action": "CREATE", "resource_type": "document", "details": "Uploaded SOC 2 Report"},
    {"action": "CREATE", "resource_type": "document", "details": "Uploaded ISO 27001 Certificate"},
    {"action": "CREATE", "resource_type": "finding", "details": "Analysis generated 5 findings"},
    {"action": "UPDATE", "resource_type": "finding", "details": "Finding status changed to acknowledged"},
    {"action": "UPDATE", "resource_type": "finding", "details": "Finding assigned to security team"},
    {"action": "STATUS_CHANGE", "resource_type": "remediation", "details": "Task moved to in_progress"},
    {"action": "STATUS_CHANGE", "resource_type": "remediation", "details": "Task completed and verified"},
    {"action": "STATUS_CHANGE", "resource_type": "vendor", "details": "Vendor tier changed to critical"},
    {"action": "EXPORT", "resource_type": "report", "details": "Exported compliance report PDF"},
    {"action": "EXPORT", "resource_type": "findings", "details": "Exported findings to CSV"},
    {"action": "LOGIN_FAILED", "resource_type": "session", "details": "Failed login attempt"},
    {"action": "PERMISSION_CHANGE", "resource_type": "user", "details": "User role updated to admin"},
    {"action": "CONFIG_CHANGE", "resource_type": "settings", "details": "Updated notification preferences"},
    {"action": "BULK_OPERATION", "resource_type": "findings", "details": "Bulk acknowledged 10 findings"},
    {"action": "CREATE", "resource_type": "alert_rule", "details": "Created new alert rule"},
    {"action": "DELETE", "resource_type": "document", "details": "Deleted outdated document"},
]

# Agent demo data
DEMO_AGENT_TASKS = [
    {"agent_name": "Sentinel Prime", "task_type": "scan", "status": "completed", "items": 12, "findings": 4},
    {"agent_name": "Sentinel Prime", "task_type": "monitor", "status": "completed", "items": 50, "findings": 2},
    {"agent_name": "Sentinel Prime", "task_type": "scan", "status": "completed", "items": 8, "findings": 1},
    {"agent_name": "Sentinel Prime", "task_type": "monitor", "status": "completed", "items": 45, "findings": 3},
    {"agent_name": "Sentinel Prime", "task_type": "scan", "status": "completed", "items": 15, "findings": 5},
    {"agent_name": "Sentinel Prime", "task_type": "monitor", "status": "running", "items": 0, "findings": 0},
    {"agent_name": "Vector Analyst", "task_type": "analyze", "status": "completed", "items": 25, "findings": 8},
    {"agent_name": "Vector Analyst", "task_type": "report", "status": "completed", "items": 30, "findings": 0},
    {"agent_name": "Vector Analyst", "task_type": "analyze", "status": "completed", "items": 18, "findings": 6},
    {"agent_name": "Vector Analyst", "task_type": "analyze", "status": "completed", "items": 22, "findings": 5},
    {"agent_name": "Vector Analyst", "task_type": "report", "status": "pending", "items": 0, "findings": 0},
    {"agent_name": "Watchdog Zero", "task_type": "scan", "status": "completed", "items": 100, "findings": 12},
    {"agent_name": "Watchdog Zero", "task_type": "audit", "status": "completed", "items": 75, "findings": 8},
    {"agent_name": "Watchdog Zero", "task_type": "scan", "status": "completed", "items": 88, "findings": 10},
    {"agent_name": "Watchdog Zero", "task_type": "audit", "status": "completed", "items": 60, "findings": 5},
    {"agent_name": "Watchdog Zero", "task_type": "scan", "status": "failed", "items": 10, "findings": 0},
    {"agent_name": "Audit Core", "task_type": "audit", "status": "completed", "items": 40, "findings": 15},
    {"agent_name": "Audit Core", "task_type": "report", "status": "completed", "items": 55, "findings": 0},
    {"agent_name": "Audit Core", "task_type": "audit", "status": "completed", "items": 35, "findings": 12},
    {"agent_name": "Audit Core", "task_type": "audit", "status": "running", "items": 20, "findings": 4},
]

DEMO_AGENT_LOGS = [
    {"agent_name": "Sentinel Prime", "level": "info", "message": "Starting vendor risk scan"},
    {"agent_name": "Sentinel Prime", "level": "info", "message": "Scanning 12 vendors for compliance gaps"},
    {"agent_name": "Sentinel Prime", "level": "warning", "message": "Vendor AWS has elevated risk score"},
    {"agent_name": "Sentinel Prime", "level": "info", "message": "Scan completed: 4 issues found"},
    {"agent_name": "Sentinel Prime", "level": "info", "message": "Monitoring SOC 2 compliance status"},
    {"agent_name": "Sentinel Prime", "level": "warning", "message": "Stripe SOC 2 report expires in 30 days"},
    {"agent_name": "Vector Analyst", "level": "info", "message": "Analyzing document: AWS_SOC2_Type_II.pdf"},
    {"agent_name": "Vector Analyst", "level": "info", "message": "Extracted 156 pages, generating embeddings"},
    {"agent_name": "Vector Analyst", "level": "info", "message": "Analysis complete: 8 findings identified"},
    {"agent_name": "Vector Analyst", "level": "warning", "message": "High confidence finding: Missing MFA"},
    {"agent_name": "Watchdog Zero", "level": "info", "message": "Starting security posture assessment"},
    {"agent_name": "Watchdog Zero", "level": "info", "message": "Scanning 100 endpoints"},
    {"agent_name": "Watchdog Zero", "level": "error", "message": "Connection timeout to vendor API"},
    {"agent_name": "Watchdog Zero", "level": "info", "message": "Retrying connection with backoff"},
    {"agent_name": "Watchdog Zero", "level": "info", "message": "Audit completed successfully"},
    {"agent_name": "Audit Core", "level": "info", "message": "Generating compliance report"},
    {"agent_name": "Audit Core", "level": "info", "message": "Comparing against ISO 27001 framework"},
    {"agent_name": "Audit Core", "level": "warning", "message": "Gap detected in access control policy"},
    {"agent_name": "Audit Core", "level": "info", "message": "Report generated: 15 recommendations"},
    {"agent_name": "Audit Core", "level": "info", "message": "Sending notification to security team"},
]

# Query demo data
DEMO_CONVERSATIONS = [
    {"title": "Critical Findings Investigation", "message_count": 4},
    {"title": "AWS Security Assessment", "message_count": 3},
    {"title": "Compliance Gap Analysis", "message_count": 5},
]

DEMO_QUERIES = [
    {"question": "What are the critical findings across all vendors?", "answer": "Based on my analysis of your vendor documents, I found 3 critical findings: 1) Missing MFA for Admin Access affecting AWS and Okta, 2) Encryption at Rest Not Implemented affecting Stripe payment processing, 3) No Incident Response Plan affecting multiple vendors. These require immediate attention.", "confidence": 0.94, "chunks": 5},
    {"question": "Which vendors lack SOC 2 certification?", "answer": "Looking at your vendor portfolio, the following vendors do not have SOC 2 Type II reports on file: Notion, Calendly, and DocuSign. However, DocuSign has submitted a SIG Core questionnaire which provides some security assurance.", "confidence": 0.91, "chunks": 4},
    {"question": "Show me encryption-related gaps", "answer": "I identified 4 encryption-related gaps: 1) Stripe - Encryption at Rest Not Implemented for payment data, 2) Snowflake - Outdated TLS Version 1.1 still enabled, 3) OpenAI - No documented key rotation policy, 4) GitHub - Cookie Missing Secure Flag for session management.", "confidence": 0.88, "chunks": 6},
    {"question": "What is AWS's risk score and why?", "answer": "AWS has a risk score of 78/100 (High Risk). Contributing factors include: 1) Critical finding for Missing MFA (40 points), 2) High finding for Outdated TLS Version (20 points), 3) Medium findings for Session Timeout and API Rate Limiting (18 points). Their SOC 2 Type II report was analyzed and showed strong controls in most areas.", "confidence": 0.92, "chunks": 8},
    {"question": "List all high-severity findings", "answer": "There are 7 high-severity findings across your vendors: 1) Outdated TLS Version (AWS), 2) Insufficient Access Logging (Okta), 3) Undisclosed Subprocessor (Snowflake), 4) Weak Password Policy (Stripe), 5) No Data Retention Policy (OpenAI), 6) Missing BCP/DR Plan (GitHub), 7) Unpatched Vulnerabilities (Datadog).", "confidence": 0.95, "chunks": 7},
    {"question": "What controls does Stripe have for data protection?", "answer": "Based on Stripe's SOC 2 report, they implement: 1) AES-256 encryption for data at rest, 2) TLS 1.3 for data in transit, 3) PCI DSS Level 1 compliance, 4) Multi-region data replication, 5) Access controls with MFA for all employees. However, a gap was noted in encryption at rest for certain legacy systems.", "confidence": 0.89, "chunks": 5},
    {"question": "How many vendors need immediate attention?", "answer": "3 vendors require immediate attention based on critical findings: 1) AWS - Missing MFA for Admin Access, 2) Stripe - Encryption at Rest issue, 3) Okta - No documented Incident Response Plan. I recommend prioritizing AWS and Stripe as they handle sensitive customer data.", "confidence": 0.93, "chunks": 4},
    {"question": "Summarize Okta's security posture", "answer": "Okta's security posture is rated Medium-High with a risk score of 68/100. Positives: Strong SOC 2 Type II controls, good access management, comprehensive logging. Concerns: Missing documented incident response plan (critical), Insufficient access logging detail (high), Penetration test showed IDOR vulnerability (medium).", "confidence": 0.90, "chunks": 9},
    {"question": "What is the remediation status for critical findings?", "answer": "Of 3 critical findings: 1) Missing MFA for Admin Access - In Progress (60% complete, due in 2 days), 2) Encryption at Rest - In Progress (implementation started, due in 3 days), 3) No Incident Response Plan - Assigned (documentation phase, due in 5 days). All are being actively worked on within SLA.", "confidence": 0.96, "chunks": 3},
    {"question": "Compare Snowflake and AWS security controls", "answer": "Comparison: AWS has stronger network segmentation and DDoS protection, while Snowflake excels in data encryption and access controls. Both have SOC 2 Type II. Gaps: AWS missing MFA (critical), Snowflake has TLS 1.1 enabled (high) and undisclosed subprocessor (high). Overall: AWS risk score 78, Snowflake risk score 72.", "confidence": 0.87, "chunks": 10},
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


@router.get("/debug-tables")
async def debug_tables(db: AsyncSession = Depends(get_db)) -> dict:
    """Debug endpoint to check which tables exist (no auth required for debugging)."""
    import logging
    from sqlalchemy import text
    logger = logging.getLogger(__name__)
    results = {}

    # Use raw SQL to check tables without ORM model issues
    tables_to_check = [
        "vendors", "documents", "findings", "analysis_runs",
        "agents", "agent_tasks", "agent_logs",
        "ai_playbooks", "playbook_steps",
        "monitoring_schedules", "alerts", "alert_rules",
        "remediation_tasks", "sla_policies",
        "audit_logs", "query_history", "conversation_threads",
    ]

    for table_name in tables_to_check:
        try:
            # Use raw SQL to avoid ORM column mapping issues
            result = await db.execute(text(f"SELECT 1 FROM {table_name} LIMIT 1"))
            results[table_name] = "OK"
        except Exception as e:
            results[table_name] = f"ERROR: {str(e)[:80]}"
        finally:
            # Rollback after each check to clear any failed transaction state
            await db.rollback()

    return {"tables": results, "default_playbooks_count": len(DEFAULT_PLAYBOOKS) if DEFAULT_PLAYBOOKS else 0}


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
    import logging
    logger = logging.getLogger(__name__)

    # Clear ALL existing data in reverse FK order
    # Each section wrapped in try-except to handle missing tables gracefully

    # Delete query history first (FK to conversations)
    try:
        result = await db.execute(select(QueryHistory).where(QueryHistory.organization_id == org_id))
        for q in result.scalars().all():
            await db.delete(q)
    except Exception as e:
        logger.warning(f"Could not delete QueryHistory: {e}")

    # Delete conversation threads
    try:
        result = await db.execute(select(ConversationThread).where(ConversationThread.organization_id == org_id))
        for conv in result.scalars().all():
            await db.delete(conv)
    except Exception as e:
        logger.warning(f"Could not delete ConversationThread: {e}")

    # Delete agent logs and tasks
    try:
        result = await db.execute(select(Agent).where(Agent.organization_id == org_id))
        agents = result.scalars().all()
        for agent in agents:
            log_result = await db.execute(select(AgentLog).where(AgentLog.agent_id == agent.id))
            for log in log_result.scalars().all():
                await db.delete(log)
        for agent in agents:
            task_result = await db.execute(select(AgentTask).where(AgentTask.agent_id == agent.id))
            for task in task_result.scalars().all():
                await db.delete(task)
    except Exception as e:
        logger.warning(f"Could not delete Agent data: {e}")

    # Delete audit logs
    try:
        result = await db.execute(select(AuditLog).where(AuditLog.organization_id == org_id))
        for log in result.scalars().all():
            await db.delete(log)
    except Exception as e:
        logger.warning(f"Could not delete AuditLog: {e}")

    # Delete playbooks (steps will cascade)
    try:
        result = await db.execute(select(AIPlaybook).where(AIPlaybook.organization_id == org_id))
        for playbook in result.scalars().all():
            await db.delete(playbook)
    except Exception as e:
        logger.warning(f"Could not delete AIPlaybook: {e}")

    # Delete notification channels
    try:
        result = await db.execute(select(NotificationChannel).where(NotificationChannel.organization_id == org_id))
        for channel in result.scalars().all():
            await db.delete(channel)
    except Exception as e:
        logger.warning(f"Could not delete NotificationChannel: {e}")

    # Delete alerts
    try:
        result = await db.execute(select(Alert).where(Alert.organization_id == org_id))
        for alert in result.scalars().all():
            await db.delete(alert)
    except Exception as e:
        logger.warning(f"Could not delete Alert: {e}")

    # Delete alert rules
    try:
        result = await db.execute(select(AlertRule).where(AlertRule.organization_id == org_id))
        for rule in result.scalars().all():
            await db.delete(rule)
    except Exception as e:
        logger.warning(f"Could not delete AlertRule: {e}")

    # Delete scheduled runs and monitoring schedules
    try:
        result = await db.execute(select(MonitoringSchedule).where(MonitoringSchedule.organization_id == org_id))
        schedules = result.scalars().all()
        for schedule in schedules:
            run_result = await db.execute(select(ScheduledRun).where(ScheduledRun.schedule_id == schedule.id))
            for run in run_result.scalars().all():
                await db.delete(run)
        for schedule in schedules:
            await db.delete(schedule)
    except Exception as e:
        logger.warning(f"Could not delete MonitoringSchedule: {e}")

    # Delete remediation comments and tasks
    try:
        result = await db.execute(select(RemediationTask).where(RemediationTask.organization_id == org_id))
        tasks = result.scalars().all()
        for task in tasks:
            comment_result = await db.execute(select(RemediationComment).where(RemediationComment.task_id == task.id))
            for comment in comment_result.scalars().all():
                await db.delete(comment)
        for task in tasks:
            await db.delete(task)
    except Exception as e:
        logger.warning(f"Could not delete RemediationTask: {e}")

    # Delete SLA policies
    try:
        result = await db.execute(select(SLAPolicy).where(SLAPolicy.organization_id == org_id))
        for policy in result.scalars().all():
            await db.delete(policy)
    except Exception as e:
        logger.warning(f"Could not delete SLAPolicy: {e}")

    # Delete findings
    try:
        result = await db.execute(select(Finding).where(Finding.organization_id == org_id))
        for finding in result.scalars().all():
            await db.delete(finding)
    except Exception as e:
        logger.warning(f"Could not delete Finding: {e}")

    # Delete analysis runs
    try:
        result = await db.execute(select(AnalysisRun).where(AnalysisRun.organization_id == org_id))
        for run in result.scalars().all():
            await db.delete(run)
    except Exception as e:
        logger.warning(f"Could not delete AnalysisRun: {e}")

    # Delete chunks and documents
    try:
        result = await db.execute(select(Document).where(Document.organization_id == org_id))
        docs_to_delete = result.scalars().all()
        for doc in docs_to_delete:
            chunk_result = await db.execute(select(DocumentChunk).where(DocumentChunk.document_id == doc.id))
            for chunk in chunk_result.scalars().all():
                await db.delete(chunk)
        for doc in docs_to_delete:
            await db.delete(doc)
    except Exception as e:
        logger.warning(f"Could not delete Document: {e}")

    # Delete vendors
    try:
        result = await db.execute(select(Vendor).where(Vendor.organization_id == org_id))
        for vendor in result.scalars().all():
            await db.delete(vendor)
    except Exception as e:
        logger.warning(f"Could not delete Vendor: {e}")

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

    # Get all findings for remediation tasks
    result = await db.execute(select(Finding).where(Finding.organization_id == org_id))
    all_findings = result.scalars().all()

    # Create SLA Policies and Remediation Tasks - wrapped in try-except for schema mismatches
    sla_policies_created = 0
    remediation_tasks_created = 0
    remediation_comments_created = 0
    task_objects = []
    try:
        sla_policy_map = {}
        for policy_data in DEMO_SLA_POLICIES:
            policy = SLAPolicy(
                id=str(uuid4()),
                organization_id=org_id,
                name=policy_data["name"],
                critical_sla_days=policy_data["critical_days"],
                high_sla_days=policy_data["high_days"],
                medium_sla_days=policy_data["medium_days"],
                low_sla_days=policy_data["low_days"],
                is_default=policy_data["is_default"],
            )
            db.add(policy)
            sla_policy_map[policy_data["name"]] = policy
            sla_policies_created += 1

        await db.commit()

        # Create Remediation Tasks (only if we have findings)
        if all_findings:
            for i, task_data in enumerate(DEMO_REMEDIATION_TASKS):
                # Link to a finding (required FK)
                finding = all_findings[i % len(all_findings)]
                vendor = random.choice(list(vendor_map.values()))

                due_date = datetime.now(timezone.utc) + timedelta(days=task_data["sla_days"])
                created_at = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14))

                # Check if SLA is breached (for some older tasks)
                sla_breached = task_data["status"] in ["in_progress", "pending_review"] and random.random() < 0.3

                task = RemediationTask(
                    id=str(uuid4()),
                    organization_id=org_id,
                    finding_id=finding.id,
                    vendor_id=vendor.id,
                    assignee_id=current_user.id if task_data["status"] not in ["draft", "pending_assignment"] else None,
                    created_by_id=current_user.id,
                    title=task_data["title"],
                    description=f"Remediation required: {task_data['title']}. This task addresses a {task_data['priority']} priority security concern.",
                    status=task_data["status"],
                    priority=task_data["priority"],
                    due_date=due_date,
                    sla_days=task_data["sla_days"],
                    sla_breached=sla_breached,
                )
                db.add(task)
                task_objects.append(task)
                remediation_tasks_created += 1

            await db.commit()

        # Create Remediation Comments
        for task in task_objects:
            # Add 2-3 comments per task
            num_comments = random.randint(2, 3)
            for i in range(num_comments):
                comment_text = random.choice(DEMO_TASK_COMMENTS)
                comment = RemediationComment(
                    id=str(uuid4()),
                    task_id=task.id,
                    user_id=current_user.id,
                    content=comment_text,
                    created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23)),
                )
                db.add(comment)
                remediation_comments_created += 1

        await db.commit()
    except Exception as e:
        logger.warning(f"Could not seed remediation data (schema mismatch?): {e}")
        await db.rollback()

    # Create Monitoring Schedules
    schedules_created = 0
    schedule_objects = []
    freq_map = {
        "daily": ScheduleFrequency.DAILY.value,
        "weekly": ScheduleFrequency.WEEKLY.value,
        "biweekly": ScheduleFrequency.BIWEEKLY.value,
        "monthly": ScheduleFrequency.MONTHLY.value,
        "quarterly": ScheduleFrequency.QUARTERLY.value,
    }
    status_map = {
        "active": ScheduleStatus.ACTIVE.value,
        "paused": ScheduleStatus.PAUSED.value,
        "disabled": ScheduleStatus.DISABLED.value,
    }

    for sched_data in DEMO_SCHEDULES:
        schedule = MonitoringSchedule(
            id=str(uuid4()),
            organization_id=org_id,
            name=sched_data["name"],
            frequency=freq_map[sched_data["frequency"]],
            status=status_map[sched_data["status"]],
            framework=sched_data["framework"],
            last_run_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 7)) if sched_data["status"] == "active" else None,
            next_run_at=datetime.now(timezone.utc) + timedelta(days=random.randint(1, 7)) if sched_data["status"] == "active" else None,
        )
        db.add(schedule)
        schedule_objects.append(schedule)
        schedules_created += 1

    await db.commit()

    # Create Scheduled Runs
    scheduled_runs_created = 0
    for schedule in schedule_objects:
        # Create 2-3 runs per schedule
        num_runs = random.randint(2, 3)
        for i in range(num_runs):
            started = datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30), hours=random.randint(0, 23))
            run = ScheduledRun(
                id=str(uuid4()),
                schedule_id=schedule.id,
                organization_id=org_id,
                status="completed" if random.random() > 0.1 else "failed",
                started_at=started,
                completed_at=started + timedelta(minutes=random.randint(5, 45)),
                vendors_assessed=random.randint(5, 12),
                documents_analyzed=random.randint(3, 20),
                findings_generated=random.randint(0, 10),
                error_message=None if random.random() > 0.1 else "Connection timeout during scan",
            )
            db.add(run)
            scheduled_runs_created += 1

    await db.commit()

    # Create Alert Rules
    alert_rules_created = 0
    rule_objects = []
    severity_map = {
        "critical": AlertSeverity.CRITICAL.value,
        "high": AlertSeverity.HIGH.value,
        "medium": AlertSeverity.MEDIUM.value,
        "low": AlertSeverity.LOW.value,
        "info": AlertSeverity.INFO.value,
    }

    for rule_data in DEMO_ALERT_RULES:
        rule = AlertRule(
            id=str(uuid4()),
            organization_id=org_id,
            name=rule_data["name"],
            trigger_type=rule_data["trigger_type"],
            severity=severity_map[rule_data["severity"]],
            trigger_conditions=json.dumps({"threshold": rule_data["threshold"]}),
            is_active=True,
        )
        db.add(rule)
        rule_objects.append(rule)
        alert_rules_created += 1

    await db.commit()

    # Create Alerts
    alerts_created = 0
    alert_status_map = {
        "new": AlertStatus.NEW.value,
        "acknowledged": AlertStatus.ACKNOWLEDGED.value,
        "in_progress": AlertStatus.IN_PROGRESS.value,
        "resolved": AlertStatus.RESOLVED.value,
        "dismissed": AlertStatus.DISMISSED.value,
    }

    vendor_list = list(vendor_map.values())
    for alert_data in DEMO_ALERTS:
        rule = random.choice(rule_objects) if rule_objects else None
        vendor = random.choice(vendor_list)

        alert = Alert(
            id=str(uuid4()),
            organization_id=org_id,
            rule_id=rule.id if rule else None,
            vendor_id=vendor.id,
            title=alert_data["title"],
            description=alert_data["message"],
            status=alert_status_map[alert_data["status"]],
            severity=severity_map[alert_data["severity"]],
            acknowledged_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)) if alert_data["status"] != "new" else None,
            acknowledged_by_id=current_user.id if alert_data["status"] != "new" else None,
            resolved_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 24)) if alert_data["status"] == "resolved" else None,
            resolved_by_id=current_user.id if alert_data["status"] == "resolved" else None,
        )
        db.add(alert)
        alerts_created += 1

    await db.commit()

    # Create Notification Channels
    notification_channels_created = 0
    channel_type_map = {
        "email": NotificationChannelType.EMAIL.value,
        "slack": NotificationChannelType.SLACK.value,
        "webhook": NotificationChannelType.WEBHOOK.value,
        "teams": NotificationChannelType.TEAMS.value,
    }

    for channel_data in DEMO_NOTIFICATION_CHANNELS:
        channel = NotificationChannel(
            id=str(uuid4()),
            organization_id=org_id,
            name=channel_data["name"],
            channel_type=channel_type_map[channel_data["channel_type"]],
            is_active=channel_data["status"] == "active",
            config=json.dumps(channel_data["config"]),
            last_used_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14)) if channel_data["status"] == "active" else None,
        )
        db.add(channel)
        notification_channels_created += 1

    await db.commit()

    # Create Audit Logs
    audit_logs_created = 0
    action_map = {
        "LOGIN": AuditAction.LOGIN.value,
        "LOGIN_FAILED": AuditAction.LOGIN_FAILED.value,
        "CREATE": AuditAction.CREATE.value,
        "UPDATE": AuditAction.UPDATE.value,
        "DELETE": AuditAction.DELETE.value,
        "EXPORT": AuditAction.EXPORT.value,
        "STATUS_CHANGE": AuditAction.STATUS_CHANGE.value,
        "PERMISSION_CHANGE": AuditAction.PERMISSION_CHANGE.value,
        "CONFIG_CHANGE": AuditAction.CONFIG_CHANGE.value,
        "BULK_OPERATION": AuditAction.BULK_OPERATION.value,
    }

    # Create 50+ audit log entries
    for _ in range(3):  # Repeat the demo actions 3 times
        for log_data in DEMO_AUDIT_ACTIONS:
            audit_log = AuditLog(
                id=str(uuid4()),
                organization_id=org_id,
                user_id=current_user.id,
                action=action_map[log_data["action"]],
                resource_type=log_data["resource_type"],
                resource_id=str(uuid4()),
                details=log_data["details"],
                ip_address=f"192.168.1.{random.randint(1, 254)}",
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
            )
            db.add(audit_log)
            audit_logs_created += 1

    await db.commit()

    # Get agents for tasks/logs - wrapped in try-except for missing tables
    agent_tasks_created = 0
    agent_logs_created = 0
    agent_task_objects = []
    try:
        result = await db.execute(select(Agent).where(Agent.organization_id == org_id))
        agents = {a.name: a for a in result.scalars().all()}

        # Create Agent Tasks
        task_type_map = {
            "scan": TaskType.SCAN.value,
            "analyze": TaskType.ANALYZE.value,
            "report": TaskType.REPORT.value,
            "monitor": TaskType.MONITOR.value,
            "audit": TaskType.AUDIT.value,
        }
        task_status_map = {
            "pending": TaskStatus.PENDING.value,
            "running": TaskStatus.RUNNING.value,
            "completed": TaskStatus.COMPLETED.value,
            "failed": TaskStatus.FAILED.value,
            "cancelled": TaskStatus.CANCELLED.value,
        }

        for task_data in DEMO_AGENT_TASKS:
            agent = agents.get(task_data["agent_name"])
            if not agent:
                continue

            started = datetime.now(timezone.utc) - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))
            agent_task = AgentTask(
                id=str(uuid4()),
                agent_id=agent.id,
                task_type=TaskType(task_data["task_type"]),
                status=TaskStatus(task_data["status"]),
                input_data={"vendors": "all", "framework": "soc2"},
                output_data={"summary": f"Processed {task_data['items']} items, found {task_data['findings']} findings"} if task_data["status"] == "completed" else None,
                items_processed=task_data["items"],
                findings_count=task_data["findings"],
                started_at=started,
                completed_at=started + timedelta(minutes=random.randint(5, 60)) if task_data["status"] in ["completed", "failed"] else None,
                error_message="Connection timeout" if task_data["status"] == "failed" else None,
            )
            db.add(agent_task)
            agent_task_objects.append(agent_task)
            agent_tasks_created += 1

        await db.commit()

        # Create Agent Logs
        for log_data in DEMO_AGENT_LOGS:
            agent = agents.get(log_data["agent_name"])
            if not agent:
                continue

            # Find a task for this agent
            agent_task = next((t for t in agent_task_objects if t.agent_id == agent.id), None)

            agent_log = AgentLog(
                id=str(uuid4()),
                agent_id=agent.id,
                task_id=agent_task.id if agent_task else None,
                level=LogLevel(log_data["level"]),
                message=log_data["message"],
            )
            db.add(agent_log)
            agent_logs_created += 1

        await db.commit()
    except Exception:
        pass  # Agent tables may not exist yet

    # Create Conversation Threads
    conversations_created = 0
    conversation_objects = []
    for conv_data in DEMO_CONVERSATIONS:
        conversation = ConversationThread(
            id=str(uuid4()),
            organization_id=org_id,
            user_id=current_user.id,
            title=conv_data["title"],
            message_count=conv_data["message_count"],
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 14)),
        )
        db.add(conversation)
        conversation_objects.append(conversation)
        conversations_created += 1

    await db.commit()

    # Create Query History
    queries_created = 0
    for i, query_data in enumerate(DEMO_QUERIES):
        # Assign to a conversation
        conv = conversation_objects[i % len(conversation_objects)] if conversation_objects else None

        query = QueryHistory(
            id=str(uuid4()),
            organization_id=org_id,
            user_id=current_user.id,
            conversation_id=conv.id if conv else None,
            question=query_data["question"],
            answer=query_data["answer"],
            citations=json.dumps([{"chunk_id": str(uuid4()), "text": "Sample citation"} for _ in range(query_data["chunks"])]),
            confidence_score=query_data["confidence"],
            chunks_retrieved=query_data["chunks"],
            status=QueryStatus.COMPLETED.value,
            created_at=datetime.now(timezone.utc) - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23)),
        )
        db.add(query)
        queries_created += 1

    await db.commit()

    # Create AI Governance Playbooks from defaults
    # Wrapped in try-except to handle missing tables gracefully
    playbooks_created = 0
    playbook_steps_created = 0
    try:
        for playbook_data in DEFAULT_PLAYBOOKS:
            playbook = AIPlaybook(
                id=str(uuid4()),
                organization_id=org_id,
                created_by_id=current_user.id,
                name=playbook_data["name"],
                description=playbook_data["description"],
                phase=playbook_data["phase"],
                target_audience=playbook_data["target_audience"],
                department=playbook_data["department"],
                estimated_duration_minutes=playbook_data.get("estimated_duration_minutes"),
                icon=playbook_data.get("icon"),
                color=playbook_data.get("color"),
                is_active=True,
                is_default=True,
            )
            db.add(playbook)
            await db.flush()  # Get the playbook ID

            # Create steps for this playbook
            for step_data in playbook_data.get("steps", []):
                step = PlaybookStep(
                    id=str(uuid4()),
                    playbook_id=playbook.id,
                    step_number=step_data["step_number"],
                    title=step_data["title"],
                    description=step_data.get("description"),
                    instructions=step_data["instructions"],
                    checklist=json.dumps(step_data.get("checklist")) if step_data.get("checklist") else None,
                    required_approvals=json.dumps(step_data.get("required_approvals")) if step_data.get("required_approvals") else None,
                    estimated_time_minutes=step_data.get("estimated_time_minutes"),
                    resources=json.dumps(step_data.get("resources")) if step_data.get("resources") else None,
                    tips=step_data.get("tips"),
                    warning=step_data.get("warning"),
                )
                db.add(step)
                playbook_steps_created += 1

            playbooks_created += 1

        await db.commit()
    except Exception as e:
        # Log and continue - playbooks are optional enhancement
        import logging
        logging.error(f"Failed to seed playbooks: {e}")
        await db.rollback()

    return SeedResponse(
        success=True,
        message="Demo data seeded successfully with all features",
        vendors_created=len(vendor_map),
        documents_created=len(documents),
        chunks_created=chunks_created,
        analysis_runs_created=len(runs),
        findings_created=findings_created,
        remediation_tasks_created=remediation_tasks_created,
        remediation_comments_created=remediation_comments_created,
        sla_policies_created=sla_policies_created,
        schedules_created=schedules_created,
        scheduled_runs_created=scheduled_runs_created,
        alert_rules_created=alert_rules_created,
        alerts_created=alerts_created,
        notification_channels_created=notification_channels_created,
        audit_logs_created=audit_logs_created,
        agent_tasks_created=agent_tasks_created,
        agent_logs_created=agent_logs_created,
        conversations_created=conversations_created,
        queries_created=queries_created,
        playbooks_created=playbooks_created,
        playbook_steps_created=playbook_steps_created,
    )


@router.delete("/clear-demo-data")
async def clear_demo_data(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    """Clear all demo data for the current user's organization."""
    org_id = current_user.organization_id
    deleted = {}

    # Delete query history first (FK to conversations)
    result = await db.execute(select(QueryHistory).where(QueryHistory.organization_id == org_id))
    deleted["queries"] = 0
    for q in result.scalars().all():
        await db.delete(q)
        deleted["queries"] += 1

    # Delete conversation threads
    result = await db.execute(select(ConversationThread).where(ConversationThread.organization_id == org_id))
    deleted["conversations"] = 0
    for conv in result.scalars().all():
        await db.delete(conv)
        deleted["conversations"] += 1

    # Delete agent logs (FK to tasks)
    result = await db.execute(select(Agent).where(Agent.organization_id == org_id))
    agents = result.scalars().all()
    deleted["agent_logs"] = 0
    for agent in agents:
        log_result = await db.execute(select(AgentLog).where(AgentLog.agent_id == agent.id))
        for log in log_result.scalars().all():
            await db.delete(log)
            deleted["agent_logs"] += 1

    # Delete agent tasks
    deleted["agent_tasks"] = 0
    for agent in agents:
        task_result = await db.execute(select(AgentTask).where(AgentTask.agent_id == agent.id))
        for task in task_result.scalars().all():
            await db.delete(task)
            deleted["agent_tasks"] += 1

    # Delete audit logs
    result = await db.execute(select(AuditLog).where(AuditLog.organization_id == org_id))
    deleted["audit_logs"] = 0
    for log in result.scalars().all():
        await db.delete(log)
        deleted["audit_logs"] += 1

    # Delete playbooks (steps will cascade)
    result = await db.execute(select(AIPlaybook).where(AIPlaybook.organization_id == org_id))
    deleted["playbooks"] = 0
    for playbook in result.scalars().all():
        await db.delete(playbook)
        deleted["playbooks"] += 1

    # Delete notification channels
    result = await db.execute(select(NotificationChannel).where(NotificationChannel.organization_id == org_id))
    deleted["notification_channels"] = 0
    for channel in result.scalars().all():
        await db.delete(channel)
        deleted["notification_channels"] += 1

    # Delete alerts
    result = await db.execute(select(Alert).where(Alert.organization_id == org_id))
    deleted["alerts"] = 0
    for alert in result.scalars().all():
        await db.delete(alert)
        deleted["alerts"] += 1

    # Delete alert rules
    result = await db.execute(select(AlertRule).where(AlertRule.organization_id == org_id))
    deleted["alert_rules"] = 0
    for rule in result.scalars().all():
        await db.delete(rule)
        deleted["alert_rules"] += 1

    # Delete scheduled runs (FK to schedules)
    result = await db.execute(select(MonitoringSchedule).where(MonitoringSchedule.organization_id == org_id))
    schedules = result.scalars().all()
    deleted["scheduled_runs"] = 0
    for schedule in schedules:
        run_result = await db.execute(select(ScheduledRun).where(ScheduledRun.schedule_id == schedule.id))
        for run in run_result.scalars().all():
            await db.delete(run)
            deleted["scheduled_runs"] += 1

    # Delete monitoring schedules
    deleted["schedules"] = 0
    for schedule in schedules:
        await db.delete(schedule)
        deleted["schedules"] += 1

    # Delete remediation comments (FK to tasks)
    result = await db.execute(select(RemediationTask).where(RemediationTask.organization_id == org_id))
    tasks = result.scalars().all()
    deleted["remediation_comments"] = 0
    for task in tasks:
        comment_result = await db.execute(select(RemediationComment).where(RemediationComment.task_id == task.id))
        for comment in comment_result.scalars().all():
            await db.delete(comment)
            deleted["remediation_comments"] += 1

    # Delete remediation tasks
    deleted["remediation_tasks"] = 0
    for task in tasks:
        await db.delete(task)
        deleted["remediation_tasks"] += 1

    # Delete SLA policies
    result = await db.execute(select(SLAPolicy).where(SLAPolicy.organization_id == org_id))
    deleted["sla_policies"] = 0
    for policy in result.scalars().all():
        await db.delete(policy)
        deleted["sla_policies"] += 1

    # Delete findings
    result = await db.execute(select(Finding).where(Finding.organization_id == org_id))
    deleted["findings"] = 0
    for finding in result.scalars().all():
        await db.delete(finding)
        deleted["findings"] += 1

    # Delete analysis runs
    result = await db.execute(select(AnalysisRun).where(AnalysisRun.organization_id == org_id))
    deleted["analysis_runs"] = 0
    for run in result.scalars().all():
        await db.delete(run)
        deleted["analysis_runs"] += 1

    # Delete chunks (FK to documents)
    result = await db.execute(select(Document).where(Document.organization_id == org_id))
    docs_to_delete = result.scalars().all()
    deleted["chunks"] = 0
    for doc in docs_to_delete:
        chunk_result = await db.execute(select(DocumentChunk).where(DocumentChunk.document_id == doc.id))
        for chunk in chunk_result.scalars().all():
            await db.delete(chunk)
            deleted["chunks"] += 1

    # Delete documents
    deleted["documents"] = 0
    for doc in docs_to_delete:
        await db.delete(doc)
        deleted["documents"] += 1

    # Delete vendors
    result = await db.execute(select(Vendor).where(Vendor.organization_id == org_id))
    deleted["vendors"] = 0
    for vendor in result.scalars().all():
        await db.delete(vendor)
        deleted["vendors"] += 1

    await db.commit()

    return {
        "success": True,
        "message": "All demo data cleared",
        "deleted": deleted,
    }
