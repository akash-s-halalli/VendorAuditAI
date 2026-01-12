"""Seed database with comprehensive demo data for interview presentation.

This script populates the demo organization with:
- 12 vendors (across all tiers)
- 18 documents (various compliance types)
- 30 findings (distributed by severity)
- 6 analysis runs

Usage:
    python -m app.scripts.seed_demo_data
"""

import asyncio
import json
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_factory, init_db
from app.models.document import Document, DocumentStatus, DocumentType, ProcessingStage
from app.models.finding import AnalysisRun, Finding, FindingSeverity, FindingStatus
from app.models.organization import Organization
from app.models.user import User
from app.models.vendor import Vendor, VendorStatus, VendorTier


# =============================================================================
# DEMO DATA DEFINITIONS
# =============================================================================

DEMO_VENDORS = [
    # CRITICAL TIER (2)
    {
        "name": "Amazon Web Services (AWS)",
        "description": "Cloud infrastructure and computing services including EC2, S3, RDS, Lambda, and 200+ services.",
        "website": "https://aws.amazon.com",
        "tier": VendorTier.CRITICAL.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "cloud_infrastructure",
        "criticality_score": 95,
        "data_classification": "highly_sensitive",
        "recommended_frameworks": json.dumps(["soc2", "iso27001", "pci_dss", "hipaa"]),
        "data_types": json.dumps(["customer_pii", "financial_data", "health_records", "credentials"]),
    },
    {
        "name": "Stripe",
        "description": "Payment processing platform handling credit cards, ACH, and international payments.",
        "website": "https://stripe.com",
        "tier": VendorTier.CRITICAL.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "payment_processing",
        "criticality_score": 98,
        "data_classification": "highly_sensitive",
        "recommended_frameworks": json.dumps(["pci_dss", "soc2", "soc1"]),
        "data_types": json.dumps(["payment_cards", "bank_accounts", "transaction_data"]),
    },
    # HIGH TIER (3)
    {
        "name": "Okta",
        "description": "Identity and access management platform for SSO, MFA, and user lifecycle management.",
        "website": "https://okta.com",
        "tier": VendorTier.HIGH.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "identity_access",
        "criticality_score": 88,
        "data_classification": "sensitive",
        "recommended_frameworks": json.dumps(["soc2", "iso27001", "fedramp"]),
        "data_types": json.dumps(["user_credentials", "access_logs", "identity_data"]),
    },
    {
        "name": "Snowflake",
        "description": "Cloud data warehouse for analytics, data sharing, and machine learning workloads.",
        "website": "https://snowflake.com",
        "tier": VendorTier.HIGH.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "data_warehouse",
        "criticality_score": 85,
        "data_classification": "sensitive",
        "recommended_frameworks": json.dumps(["soc2", "iso27001", "hipaa"]),
        "data_types": json.dumps(["analytics_data", "customer_data", "business_metrics"]),
    },
    {
        "name": "OpenAI",
        "description": "AI/ML platform providing GPT models, embeddings, and AI infrastructure.",
        "website": "https://openai.com",
        "tier": VendorTier.HIGH.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "ai_ml",
        "criticality_score": 82,
        "data_classification": "sensitive",
        "recommended_frameworks": json.dumps(["soc2", "nist_ai_rmf"]),
        "data_types": json.dumps(["prompts", "training_data", "model_outputs"]),
    },
    # MEDIUM TIER (4)
    {
        "name": "Zendesk",
        "description": "Customer support and ticketing platform for help desk operations.",
        "website": "https://zendesk.com",
        "tier": VendorTier.MEDIUM.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "customer_support",
        "criticality_score": 65,
        "data_classification": "internal",
        "recommended_frameworks": json.dumps(["soc2", "sig_lite"]),
        "data_types": json.dumps(["support_tickets", "customer_emails", "chat_logs"]),
    },
    {
        "name": "Slack",
        "description": "Team collaboration and messaging platform for internal communications.",
        "website": "https://slack.com",
        "tier": VendorTier.MEDIUM.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "communication",
        "criticality_score": 60,
        "data_classification": "internal",
        "recommended_frameworks": json.dumps(["soc2", "sig_lite"]),
        "data_types": json.dumps(["messages", "files", "channel_data"]),
    },
    {
        "name": "GitHub",
        "description": "Source code repository and CI/CD platform for development teams.",
        "website": "https://github.com",
        "tier": VendorTier.MEDIUM.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "devops",
        "criticality_score": 70,
        "data_classification": "confidential",
        "recommended_frameworks": json.dumps(["soc2", "iso27001"]),
        "data_types": json.dumps(["source_code", "secrets", "ci_cd_configs"]),
    },
    {
        "name": "Datadog",
        "description": "Infrastructure monitoring, APM, and log management platform.",
        "website": "https://datadoghq.com",
        "tier": VendorTier.MEDIUM.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "monitoring",
        "criticality_score": 55,
        "data_classification": "internal",
        "recommended_frameworks": json.dumps(["soc2"]),
        "data_types": json.dumps(["metrics", "logs", "traces", "infrastructure_data"]),
    },
    # LOW TIER (3)
    {
        "name": "Notion",
        "description": "Team wiki and documentation platform for knowledge management.",
        "website": "https://notion.so",
        "tier": VendorTier.LOW.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "collaboration",
        "criticality_score": 35,
        "data_classification": "internal",
        "recommended_frameworks": json.dumps(["sig_lite"]),
        "data_types": json.dumps(["documents", "wikis", "project_data"]),
    },
    {
        "name": "Calendly",
        "description": "Scheduling and appointment booking platform.",
        "website": "https://calendly.com",
        "tier": VendorTier.LOW.value,
        "status": VendorStatus.ACTIVE.value,
        "category": "productivity",
        "criticality_score": 25,
        "data_classification": "public",
        "recommended_frameworks": json.dumps(["sig_lite"]),
        "data_types": json.dumps(["calendar_events", "contact_info"]),
    },
    {
        "name": "DocuSign",
        "description": "Electronic signature and contract management platform.",
        "website": "https://docusign.com",
        "tier": VendorTier.LOW.value,
        "status": VendorStatus.ONBOARDING.value,
        "category": "legal",
        "criticality_score": 40,
        "data_classification": "confidential",
        "recommended_frameworks": json.dumps(["soc2", "sig_lite"]),
        "data_types": json.dumps(["contracts", "signatures", "legal_documents"]),
    },
]

# Document templates per vendor
DEMO_DOCUMENTS = [
    # AWS documents
    {"vendor_name": "Amazon Web Services (AWS)", "filename": "AWS_SOC2_Type_II_Report_2025.pdf", "document_type": DocumentType.SOC2.value, "page_count": 156, "file_size": 4500000},
    {"vendor_name": "Amazon Web Services (AWS)", "filename": "AWS_ISO27001_Certificate_2025.pdf", "document_type": DocumentType.ISO27001.value, "page_count": 12, "file_size": 850000},
    # Stripe documents
    {"vendor_name": "Stripe", "filename": "Stripe_SOC2_Type_II_2025.pdf", "document_type": DocumentType.SOC2.value, "page_count": 89, "file_size": 3200000},
    {"vendor_name": "Stripe", "filename": "Stripe_PCI_DSS_AOC_2025.pdf", "document_type": DocumentType.OTHER.value, "page_count": 24, "file_size": 1100000},
    # Okta documents
    {"vendor_name": "Okta", "filename": "Okta_SOC2_Report_2025.pdf", "document_type": DocumentType.SOC2.value, "page_count": 134, "file_size": 3800000},
    {"vendor_name": "Okta", "filename": "Okta_Pentest_Report_Q4_2025.pdf", "document_type": DocumentType.PENTEST.value, "page_count": 45, "file_size": 2100000},
    # Snowflake documents
    {"vendor_name": "Snowflake", "filename": "Snowflake_SOC2_Type_II_2025.pdf", "document_type": DocumentType.SOC2.value, "page_count": 112, "file_size": 3400000},
    {"vendor_name": "Snowflake", "filename": "Snowflake_ISO27001_Cert.pdf", "document_type": DocumentType.ISO27001.value, "page_count": 8, "file_size": 650000},
    # OpenAI documents
    {"vendor_name": "OpenAI", "filename": "OpenAI_SOC2_Type_II_2025.pdf", "document_type": DocumentType.SOC2.value, "page_count": 78, "file_size": 2900000},
    {"vendor_name": "OpenAI", "filename": "OpenAI_SIG_Core_2025.docx", "document_type": DocumentType.SIG_CORE.value, "page_count": 245, "file_size": 1800000},
    # Zendesk documents
    {"vendor_name": "Zendesk", "filename": "Zendesk_SIG_Lite_2025.pdf", "document_type": DocumentType.SIG_LITE.value, "page_count": 32, "file_size": 980000},
    # Slack documents
    {"vendor_name": "Slack", "filename": "Slack_SOC2_Report_2025.pdf", "document_type": DocumentType.SOC2.value, "page_count": 95, "file_size": 3100000},
    # GitHub documents
    {"vendor_name": "GitHub", "filename": "GitHub_SOC2_Type_II_2025.pdf", "document_type": DocumentType.SOC2.value, "page_count": 102, "file_size": 3500000},
    {"vendor_name": "GitHub", "filename": "GitHub_Pentest_Summary_2025.pdf", "document_type": DocumentType.PENTEST.value, "page_count": 28, "file_size": 1400000},
    # Datadog documents
    {"vendor_name": "Datadog", "filename": "Datadog_ISO27001_Certificate.pdf", "document_type": DocumentType.ISO27001.value, "page_count": 6, "file_size": 520000},
    # Notion documents
    {"vendor_name": "Notion", "filename": "Notion_SIG_Lite_Assessment.pdf", "document_type": DocumentType.SIG_LITE.value, "page_count": 28, "file_size": 890000},
    # DocuSign documents
    {"vendor_name": "DocuSign", "filename": "DocuSign_SIG_Core_Questionnaire.pdf", "document_type": DocumentType.SIG_CORE.value, "page_count": 198, "file_size": 1650000},
    # Calendly - no documents yet (demo showing gap)
]

# Finding templates
DEMO_FINDINGS = [
    # CRITICAL (3)
    {
        "title": "Missing Multi-Factor Authentication for Admin Access",
        "severity": FindingSeverity.CRITICAL.value,
        "framework": "soc2",
        "framework_control": "CC6.1",
        "description": "Administrative access to the vendor's production systems does not require multi-factor authentication, creating significant risk of unauthorized access.",
        "evidence": "Section 4.2 of SOC 2 report indicates single-factor authentication for privileged accounts.",
        "remediation": "Require MFA for all administrative and privileged access. Implement hardware tokens or authenticator apps.",
        "impact": "Unauthorized access to critical systems could lead to data breach or service disruption.",
        "confidence_score": 0.95,
    },
    {
        "title": "Encryption at Rest Not Implemented for Customer Data",
        "severity": FindingSeverity.CRITICAL.value,
        "framework": "pci_dss",
        "framework_control": "3.4",
        "description": "Customer payment card data and PII stored in databases is not encrypted at rest, violating PCI DSS requirements.",
        "evidence": "Database configuration review shows AES encryption disabled for primary data stores.",
        "remediation": "Enable AES-256 encryption for all databases containing sensitive data. Implement key rotation policies.",
        "impact": "Data breach could expose unencrypted customer financial information.",
        "confidence_score": 0.98,
    },
    {
        "title": "No Incident Response Plan Documented",
        "severity": FindingSeverity.CRITICAL.value,
        "framework": "iso27001",
        "framework_control": "A.16.1",
        "description": "The vendor lacks a documented incident response plan for security breaches and data incidents.",
        "evidence": "Requested IR documentation returned 'under development' status.",
        "remediation": "Develop and document comprehensive incident response procedures. Conduct tabletop exercises.",
        "impact": "Delayed or ineffective response to security incidents could amplify damage.",
        "confidence_score": 0.92,
    },
    # HIGH (7)
    {
        "title": "Outdated TLS Version in Use",
        "severity": FindingSeverity.HIGH.value,
        "framework": "soc2",
        "framework_control": "CC6.7",
        "description": "API endpoints support TLS 1.0 and 1.1 which have known vulnerabilities.",
        "evidence": "SSL scan shows TLS 1.0 enabled on api.vendor.com",
        "remediation": "Disable TLS 1.0 and 1.1. Enable only TLS 1.2 and 1.3.",
        "impact": "Man-in-the-middle attacks possible on encrypted connections.",
        "confidence_score": 0.94,
    },
    {
        "title": "Insufficient Access Logging",
        "severity": FindingSeverity.HIGH.value,
        "framework": "soc2",
        "framework_control": "CC7.2",
        "description": "Access logs do not capture sufficient detail for forensic analysis including source IP and user agent.",
        "evidence": "Sample log entries missing IP addresses and timestamp precision.",
        "remediation": "Enhance logging to capture complete request metadata. Implement centralized log management.",
        "impact": "Security incidents cannot be properly investigated.",
        "confidence_score": 0.88,
    },
    {
        "title": "Third-Party Subprocessor Not Disclosed",
        "severity": FindingSeverity.HIGH.value,
        "framework": "iso27001",
        "framework_control": "A.15.1",
        "description": "Vendor uses undisclosed third-party data processor for analytics without contractual safeguards.",
        "evidence": "Network analysis reveals data flows to uncontracted third party.",
        "remediation": "Disclose all subprocessors. Establish DPAs with each third party.",
        "impact": "Data may be processed without appropriate legal basis.",
        "confidence_score": 0.85,
    },
    {
        "title": "Weak Password Policy",
        "severity": FindingSeverity.HIGH.value,
        "framework": "soc2",
        "framework_control": "CC6.1",
        "description": "Password policy allows 6-character passwords without complexity requirements.",
        "evidence": "Security questionnaire response indicates minimum 6 characters, no special character requirement.",
        "remediation": "Implement 12+ character minimum with complexity requirements. Enable password breach checking.",
        "impact": "User accounts vulnerable to brute force and credential stuffing attacks.",
        "confidence_score": 0.91,
    },
    {
        "title": "No Data Retention Policy",
        "severity": FindingSeverity.HIGH.value,
        "framework": "iso27001",
        "framework_control": "A.8.3",
        "description": "Vendor has no documented data retention or deletion policy for customer data.",
        "evidence": "Data handling section of questionnaire marked 'N/A'.",
        "remediation": "Define and implement data retention schedules. Automate data deletion processes.",
        "impact": "Data retained indefinitely increases breach impact and compliance risk.",
        "confidence_score": 0.87,
    },
    {
        "title": "Missing Business Continuity Plan",
        "severity": FindingSeverity.HIGH.value,
        "framework": "soc2",
        "framework_control": "A1.2",
        "description": "No documented business continuity or disaster recovery plan available for review.",
        "evidence": "BCP documentation request returned 'confidential' without executive summary.",
        "remediation": "Document BCP/DR plans. Provide summary to customers. Test annually.",
        "impact": "Service availability risk during major incidents.",
        "confidence_score": 0.83,
    },
    {
        "title": "Unpatched Known Vulnerabilities",
        "severity": FindingSeverity.HIGH.value,
        "framework": "soc2",
        "framework_control": "CC7.1",
        "description": "Penetration test identified 3 high-severity CVEs unpatched for over 90 days.",
        "evidence": "Pentest report section 5.2 lists CVE-2024-1234, CVE-2024-5678, CVE-2024-9012.",
        "remediation": "Implement 30-day patching SLA for high-severity vulnerabilities.",
        "impact": "Known attack vectors available to malicious actors.",
        "confidence_score": 0.96,
    },
    # MEDIUM (12)
    {
        "title": "Session Timeout Too Long",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "soc2",
        "framework_control": "CC6.1",
        "description": "User sessions remain active for 24 hours without re-authentication.",
        "evidence": "Testing confirmed session valid after 24 hours of inactivity.",
        "remediation": "Reduce session timeout to 15-30 minutes for sensitive operations.",
        "impact": "Unattended sessions could be hijacked.",
        "confidence_score": 0.89,
    },
    {
        "title": "No Security Awareness Training Program",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "iso27001",
        "framework_control": "A.7.2",
        "description": "Vendor does not have documented security awareness training for employees.",
        "evidence": "HR policy document lacks security training requirements.",
        "remediation": "Implement annual security awareness training with phishing simulations.",
        "impact": "Employees may fall victim to social engineering attacks.",
        "confidence_score": 0.84,
    },
    {
        "title": "API Rate Limiting Not Implemented",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "soc2",
        "framework_control": "CC6.6",
        "description": "API endpoints do not enforce rate limiting, enabling brute force attacks.",
        "evidence": "10,000 requests sent in 1 minute without throttling.",
        "remediation": "Implement rate limiting (100 requests/minute per IP).",
        "impact": "APIs vulnerable to denial of service and enumeration attacks.",
        "confidence_score": 0.92,
    },
    {
        "title": "Incomplete Audit Trail",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "soc2",
        "framework_control": "CC7.2",
        "description": "Audit logs do not capture data modification events.",
        "evidence": "Log sample shows access events but no create/update/delete entries.",
        "remediation": "Log all CRUD operations with before/after values.",
        "impact": "Data tampering cannot be detected or investigated.",
        "confidence_score": 0.86,
    },
    {
        "title": "No Vulnerability Disclosure Program",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "iso27001",
        "framework_control": "A.12.6",
        "description": "Vendor has no public vulnerability disclosure or bug bounty program.",
        "evidence": "Website and security page lack disclosure policy.",
        "remediation": "Establish responsible disclosure policy and security contact.",
        "impact": "Security researchers cannot report vulnerabilities responsibly.",
        "confidence_score": 0.78,
    },
    {
        "title": "Background Checks Not Verified",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "soc2",
        "framework_control": "CC1.4",
        "description": "Background check process for employees with data access not documented.",
        "evidence": "HR policy does not specify background check requirements.",
        "remediation": "Document and verify background check requirements for sensitive roles.",
        "impact": "Insider threat risk not adequately mitigated.",
        "confidence_score": 0.81,
    },
    {
        "title": "Insecure Direct Object References",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "soc2",
        "framework_control": "CC6.1",
        "description": "API allows access to resources by predictable IDs without authorization checks.",
        "evidence": "Pentest report section 4.3 demonstrates IDOR vulnerability.",
        "remediation": "Implement authorization checks for all resource access.",
        "impact": "Users may access other customers' data.",
        "confidence_score": 0.93,
    },
    {
        "title": "Missing CORS Configuration",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "soc2",
        "framework_control": "CC6.6",
        "description": "API returns Access-Control-Allow-Origin: * header.",
        "evidence": "Browser dev tools show wildcard CORS header.",
        "remediation": "Configure specific allowed origins for CORS.",
        "impact": "Cross-site request forgery attacks possible.",
        "confidence_score": 0.88,
    },
    {
        "title": "Sensitive Data in URL Parameters",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "pci_dss",
        "framework_control": "4.2",
        "description": "API passes user tokens and IDs in URL query parameters.",
        "evidence": "Request logs show tokens in URL: /api/data?token=xxx",
        "remediation": "Move sensitive data to request headers or body.",
        "impact": "Tokens logged in server logs and browser history.",
        "confidence_score": 0.90,
    },
    {
        "title": "No Change Management Process",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "soc2",
        "framework_control": "CC8.1",
        "description": "Changes to production systems lack formal approval process.",
        "evidence": "No change advisory board or approval workflow documented.",
        "remediation": "Implement change management with approval gates.",
        "impact": "Unauthorized or untested changes may cause outages.",
        "confidence_score": 0.82,
    },
    {
        "title": "Missing Data Classification Policy",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "iso27001",
        "framework_control": "A.8.2",
        "description": "No data classification scheme documented for handling different data types.",
        "evidence": "Information security policy lacks classification section.",
        "remediation": "Define data classification levels and handling procedures.",
        "impact": "Sensitive data may not receive appropriate protection.",
        "confidence_score": 0.79,
    },
    {
        "title": "Inadequate Network Segmentation",
        "severity": FindingSeverity.MEDIUM.value,
        "framework": "pci_dss",
        "framework_control": "1.3",
        "description": "Production and development environments share network segments.",
        "evidence": "Network diagram shows flat network topology.",
        "remediation": "Implement network segmentation with firewalls between zones.",
        "impact": "Compromise of dev environment can spread to production.",
        "confidence_score": 0.85,
    },
    # LOW (8)
    {
        "title": "Security Headers Missing",
        "severity": FindingSeverity.LOW.value,
        "framework": "soc2",
        "framework_control": "CC6.6",
        "description": "HTTP responses missing X-Content-Type-Options and X-Frame-Options headers.",
        "evidence": "Response headers analysis shows missing security headers.",
        "remediation": "Add X-Content-Type-Options, X-Frame-Options, and CSP headers.",
        "impact": "Minor increase in clickjacking and MIME sniffing risk.",
        "confidence_score": 0.91,
    },
    {
        "title": "Verbose Error Messages",
        "severity": FindingSeverity.LOW.value,
        "framework": "soc2",
        "framework_control": "CC6.1",
        "description": "API returns detailed stack traces in error responses.",
        "evidence": "Error response includes internal file paths and line numbers.",
        "remediation": "Return generic error messages. Log details server-side only.",
        "impact": "Information disclosure aids attackers.",
        "confidence_score": 0.87,
    },
    {
        "title": "Cookie Missing Secure Flag",
        "severity": FindingSeverity.LOW.value,
        "framework": "soc2",
        "framework_control": "CC6.7",
        "description": "Session cookie does not have Secure flag set.",
        "evidence": "Set-Cookie header lacks Secure attribute.",
        "remediation": "Add Secure flag to all cookies containing sensitive data.",
        "impact": "Cookies may be sent over unencrypted connections.",
        "confidence_score": 0.93,
    },
    {
        "title": "No Privacy Policy Version Control",
        "severity": FindingSeverity.LOW.value,
        "framework": "iso27001",
        "framework_control": "A.18.1",
        "description": "Privacy policy lacks version number and last updated date.",
        "evidence": "Public privacy policy page has no version information.",
        "remediation": "Add version control and change history to privacy policy.",
        "impact": "Difficult to track policy changes over time.",
        "confidence_score": 0.76,
    },
    {
        "title": "Default Credentials in Documentation",
        "severity": FindingSeverity.LOW.value,
        "framework": "soc2",
        "framework_control": "CC6.1",
        "description": "API documentation shows example credentials that could be mistaken for defaults.",
        "evidence": "Docs show admin/admin123 as example login.",
        "remediation": "Use clearly fake credentials in documentation (user@example.com).",
        "impact": "Users may inadvertently use weak credentials.",
        "confidence_score": 0.72,
    },
    {
        "title": "Missing Subresource Integrity",
        "severity": FindingSeverity.LOW.value,
        "framework": "soc2",
        "framework_control": "CC6.6",
        "description": "Third-party JavaScript libraries loaded without SRI hashes.",
        "evidence": "Script tags lack integrity attributes.",
        "remediation": "Add SRI hashes to all CDN-loaded scripts.",
        "impact": "CDN compromise could inject malicious code.",
        "confidence_score": 0.83,
    },
    {
        "title": "Inconsistent Date Format in Logs",
        "severity": FindingSeverity.LOW.value,
        "framework": "soc2",
        "framework_control": "CC7.2",
        "description": "Log entries use inconsistent date formats across services.",
        "evidence": "Sample logs show mix of ISO 8601 and Unix timestamps.",
        "remediation": "Standardize on ISO 8601 format for all logs.",
        "impact": "Log correlation and analysis more difficult.",
        "confidence_score": 0.74,
    },
    {
        "title": "Outdated SSL Certificate",
        "severity": FindingSeverity.LOW.value,
        "framework": "soc2",
        "framework_control": "CC6.7",
        "description": "SSL certificate expires in less than 30 days.",
        "evidence": "Certificate check shows expiry in 22 days.",
        "remediation": "Renew certificate and implement automated renewal.",
        "impact": "Service disruption if certificate expires.",
        "confidence_score": 0.95,
    },
]


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

async def get_demo_organization(db: AsyncSession) -> tuple[Organization | None, User | None]:
    """Find the demo organization and user."""
    result = await db.execute(
        select(User).where(User.email == "newdemo@vendorauditai.com")
    )
    demo_user = result.scalar_one_or_none()

    if demo_user:
        result = await db.execute(
            select(Organization).where(Organization.id == demo_user.organization_id)
        )
        org = result.scalar_one_or_none()
        return org, demo_user

    return None, None


async def clear_existing_data(db: AsyncSession, organization_id: str) -> None:
    """Clear existing demo data for clean seeding."""
    # Delete in order due to foreign keys
    await db.execute(
        select(Finding).where(Finding.organization_id == organization_id)
    )

    # Get and delete analysis runs
    result = await db.execute(
        select(AnalysisRun).where(AnalysisRun.organization_id == organization_id)
    )
    for run in result.scalars().all():
        await db.delete(run)

    # Get and delete documents
    result = await db.execute(
        select(Document).where(Document.organization_id == organization_id)
    )
    for doc in result.scalars().all():
        await db.delete(doc)

    # Get and delete vendors
    result = await db.execute(
        select(Vendor).where(Vendor.organization_id == organization_id)
    )
    for vendor in result.scalars().all():
        await db.delete(vendor)

    await db.commit()
    print("[*] Cleared existing demo data")


# =============================================================================
# SEEDING FUNCTIONS
# =============================================================================

async def seed_vendors(db: AsyncSession, organization_id: str) -> dict[str, Vendor]:
    """Seed vendors and return mapping of name to vendor."""
    vendor_map = {}

    for vendor_data in DEMO_VENDORS:
        vendor = Vendor(
            id=str(uuid4()),
            organization_id=organization_id,
            name=vendor_data["name"],
            description=vendor_data["description"],
            website=vendor_data["website"],
            tier=vendor_data["tier"],
            status=vendor_data["status"],
            category=vendor_data["category"],
            criticality_score=vendor_data["criticality_score"],
            data_classification=vendor_data["data_classification"],
            recommended_frameworks=vendor_data["recommended_frameworks"],
            data_types=vendor_data["data_types"],
            categorization_confidence=0.92,
            last_assessed=datetime.now(timezone.utc) - timedelta(days=random.randint(10, 90)),
            next_assessment_due=(datetime.now(timezone.utc) + timedelta(days=random.randint(30, 180))).date(),
            risk_score=random.uniform(20, 85) if vendor_data["tier"] != VendorTier.CRITICAL.value else random.uniform(70, 95),
            risk_calculated_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
        )
        db.add(vendor)
        vendor_map[vendor_data["name"]] = vendor

    await db.commit()
    print(f"[+] Created {len(vendor_map)} vendors")
    return vendor_map


async def seed_documents(
    db: AsyncSession,
    organization_id: str,
    vendor_map: dict[str, Vendor]
) -> list[Document]:
    """Seed documents for vendors."""
    documents = []

    for doc_data in DEMO_DOCUMENTS:
        vendor = vendor_map.get(doc_data["vendor_name"])
        if not vendor:
            continue

        # Most documents are processed, some pending
        status = random.choice([
            DocumentStatus.PROCESSED.value,
            DocumentStatus.PROCESSED.value,
            DocumentStatus.PROCESSED.value,
            DocumentStatus.PENDING.value,
        ])

        processing_stage = (
            ProcessingStage.COMPLETED.value
            if status == DocumentStatus.PROCESSED.value
            else ProcessingStage.UPLOADED.value
        )

        doc = Document(
            id=str(uuid4()),
            organization_id=organization_id,
            vendor_id=vendor.id,
            filename=doc_data["filename"],
            storage_path=f"documents/{organization_id}/{doc_data['filename']}",
            file_size=doc_data["file_size"],
            mime_type="application/pdf" if doc_data["filename"].endswith(".pdf") else "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            document_type=doc_data["document_type"],
            status=status,
            processing_stage=processing_stage,
            page_count=doc_data["page_count"],
            processed_at=datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)) if status == DocumentStatus.PROCESSED.value else None,
        )
        db.add(doc)
        documents.append(doc)

    await db.commit()
    print(f"[+] Created {len(documents)} documents")
    return documents


async def seed_analysis_runs(
    db: AsyncSession,
    organization_id: str,
    documents: list[Document]
) -> list[AnalysisRun]:
    """Seed analysis runs for processed documents."""
    runs = []
    processed_docs = [d for d in documents if d.status == DocumentStatus.PROCESSED.value]

    frameworks = ["soc2", "iso27001", "pci_dss", "hipaa", "nist_csf"]

    for doc in processed_docs[:6]:  # Create runs for first 6 processed docs
        framework = random.choice(frameworks)
        status = random.choice(["completed", "completed", "completed", "completed", "in_progress", "pending"])

        run = AnalysisRun(
            id=str(uuid4()),
            organization_id=organization_id,
            document_id=doc.id,
            framework=framework,
            model_used="claude-3-5-sonnet-20241022",
            status=status,
            chunks_analyzed=random.randint(20, 80) if status == "completed" else 0,
            findings_count=random.randint(2, 8) if status == "completed" else 0,
            input_tokens=random.randint(50000, 150000) if status == "completed" else 0,
            output_tokens=random.randint(5000, 15000) if status == "completed" else 0,
            started_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 72)) if status != "pending" else None,
            completed_at=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)) if status == "completed" else None,
            summary=f"Analysis completed for {doc.filename} against {framework.upper()} framework. Multiple control gaps identified requiring remediation." if status == "completed" else None,
        )
        db.add(run)
        runs.append(run)

    await db.commit()
    print(f"[+] Created {len(runs)} analysis runs")
    return runs


async def seed_findings(
    db: AsyncSession,
    organization_id: str,
    documents: list[Document],
    runs: list[AnalysisRun]
) -> list[Finding]:
    """Seed findings from analysis."""
    findings = []

    # Get completed runs
    completed_runs = [r for r in runs if r.status == "completed"]
    if not completed_runs:
        print("[!] No completed runs to attach findings to")
        return findings

    for finding_data in DEMO_FINDINGS:
        # Assign to random completed run and its document
        run = random.choice(completed_runs)

        finding = Finding(
            id=str(uuid4()),
            analysis_run_id=run.id,
            document_id=run.document_id,
            organization_id=organization_id,
            title=finding_data["title"],
            severity=finding_data["severity"],
            status=random.choice([
                FindingStatus.OPEN.value,
                FindingStatus.OPEN.value,
                FindingStatus.ACKNOWLEDGED.value,
                FindingStatus.REMEDIATED.value,
            ]),
            framework=finding_data["framework"],
            framework_control=finding_data["framework_control"],
            description=finding_data["description"],
            evidence=finding_data["evidence"],
            remediation=finding_data["remediation"],
            impact=finding_data["impact"],
            confidence_score=finding_data["confidence_score"],
            page_number=random.randint(1, 50),
            section_header=f"Section {random.randint(1, 10)}.{random.randint(1, 5)}",
        )
        db.add(finding)
        findings.append(finding)

    await db.commit()
    print(f"[+] Created {len(findings)} findings")

    # Print severity breakdown
    severity_counts = {}
    for f in findings:
        severity_counts[f.severity] = severity_counts.get(f.severity, 0) + 1
    print(f"    Severity breakdown: {severity_counts}")

    return findings


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

async def main():
    """Main entry point for seeding demo data."""
    print("=" * 60)
    print(" VendorAuditAI - Demo Data Seeding Script")
    print(" Preparing for Interview Demonstration")
    print("=" * 60)
    print()

    # Initialize database
    print("[*] Initializing database connection...")
    await init_db()

    async with async_session_factory() as db:
        # Find demo organization
        print("[*] Looking for demo organization...")
        org, user = await get_demo_organization(db)

        if not org:
            print("[!] ERROR: Demo organization not found!")
            print("[!] Please ensure newdemo@vendorauditai.com exists")
            print("[!] You may need to register this account first via the app")
            return

        print(f"[+] Found organization: {org.name} (ID: {org.id})")
        print(f"[+] Demo user: {user.email}")
        print()

        # Ask to clear existing data
        print("[*] Seeding fresh demo data...")

        # Clear existing data for clean demo
        await clear_existing_data(db, org.id)
        print()

        # Seed all data
        print("[*] Creating vendors...")
        vendor_map = await seed_vendors(db, org.id)
        print()

        print("[*] Creating documents...")
        documents = await seed_documents(db, org.id, vendor_map)
        print()

        print("[*] Creating analysis runs...")
        runs = await seed_analysis_runs(db, org.id, documents)
        print()

        print("[*] Creating findings...")
        findings = await seed_findings(db, org.id, documents, runs)
        print()

        # Summary
        print("=" * 60)
        print(" DEMO DATA SEEDING COMPLETE")
        print("=" * 60)
        print()
        print(f" Vendors:       {len(vendor_map)}")
        print(f" Documents:     {len(documents)}")
        print(f" Analysis Runs: {len(runs)}")
        print(f" Findings:      {len(findings)}")
        print()
        print(" Demo Login:")
        print("   Email:    newdemo@vendorauditai.com")
        print("   Password: Demo12345")
        print()
        print(" Your demo is ready!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
