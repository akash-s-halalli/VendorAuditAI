# Changelog

All notable changes to VendorAuditAI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-11

### Enterprise Security Release

This release marks VendorAuditAI as enterprise-ready with full security compliance features required by Fortune 500 companies.

### Added

#### TIER 1: Enterprise Security

- **SSO/SAML 2.0 Integration** - Single Sign-On support for enterprise identity providers
  - Azure Active Directory support
  - Okta integration
  - Google Workspace compatibility
  - OneLogin support
  - Custom SAML provider configuration
  - SP metadata generation for IdP setup
  - Assertion Consumer Service (ACS) endpoint

- **Multi-Factor Authentication (MFA)** - TOTP-based two-factor authentication
  - Time-based One-Time Password (TOTP) support
  - QR code provisioning for authenticator apps
  - Backup recovery codes (10 codes per user)
  - MFA enforcement per organization
  - Compatible with Google Authenticator, Authy, 1Password

- **System-Wide Audit Logging** - Complete audit trail for SOC 2 compliance
  - All CRUD operations logged
  - User authentication events (login, logout, failed attempts)
  - Export operations tracked
  - MFA enable/disable events
  - Configuration changes
  - IP address and user agent capture
  - Admin-only audit log viewer
  - CSV export for compliance reports

- **API Rate Limiting** - Protection against abuse and brute force attacks
  - Authentication endpoints: 5 requests/minute
  - Analysis/LLM operations: 10 requests/hour
  - Export operations: 10 requests/minute
  - Standard API: 100 requests/minute
  - SlowAPI middleware integration

#### Platform Improvements

- **Dashboard Performance Optimization** - Parallel query execution
  - 3x faster dashboard load times
  - Concurrent database queries using asyncio.gather

### Security

- Rate limiting prevents brute force attacks on login endpoints
- MFA adds additional authentication layer
- Audit logs enable security incident investigation
- SSO enables centralized identity management

### Technical Details

- **Backend Tests**: 123 passing, 6 skipped
- **New Dependencies**: slowapi (rate limiting), pyotp (MFA)
- **New Models**: AuditLog, SSOConfig
- **New Endpoints**: 15+ new API endpoints

---

## [0.9.0] - 2026-01-10

### AI & Compliance Release

### Added

- **NIST AI Risk Management Framework** - AI governance compliance
  - Trustworthy AI characteristics mapping
  - 70+ controls for AI system risk management

- **AI Vendor Risk Assessment Module** - Specialized AI vendor evaluation
  - Data provenance controls
  - Model poisoning detection
  - Bias detection requirements
  - Model security controls
  - Explainability requirements

- **CSA CAIQ Framework** - Cloud Security Alliance support
  - 260+ controls across 17 domains
  - Yes/No assessment format
  - Cloud provider evaluation

- **Continuous Monitoring & Alerts** - Proactive risk management
  - Scheduled assessments (daily, weekly, monthly, quarterly)
  - Alert rules and thresholds
  - Multi-channel notifications (Slack, Email, Teams, Webhooks)
  - Monitoring dashboard with statistics

- **Remediation Workflow System** - Issue tracking with SLA management
  - 7-stage state machine workflow
  - Task assignment and ownership
  - SLA tracking and breach detection
  - Audit trail for all changes
  - Threaded comments
  - Exception request workflow

### Changed

- Updated AI models to Claude Opus 4.5 and Gemini 3 Pro
- Improved document analysis accuracy

---

## [0.8.0] - 2026-01-09

### Core Platform Release

### Added

- **Document Intelligence Engine**
  - PDF and DOCX parsing
  - Azure Document Intelligence integration
  - Table extraction
  - 50+ language support

- **Multi-Framework Compliance Analysis**
  - NIST 800-53 (1,000+ controls)
  - SOC 2 TSC (64 controls)
  - ISO 27001 (114 controls)
  - CIS Controls (153 controls)
  - PCI-DSS (250+ controls)
  - HIPAA (75 controls)

- **Natural Language Query Interface**
  - Semantic search across vendor portfolio
  - RAG-powered responses
  - Query history tracking

- **Real-Time Dashboard**
  - Vendor statistics
  - Finding severity breakdown
  - Document processing status

- **Vendor Management**
  - CRUD operations
  - Vendor tiers
  - Document association

- **User Authentication**
  - JWT-based authentication
  - Role-based access control (Admin, Analyst, Viewer)
  - Organization-scoped data isolation

### Technical

- FastAPI backend with async support
- React 18 frontend with TypeScript
- PostgreSQL database with SQLAlchemy 2.0
- TanStack Query for state management

---

## API Versioning

| Version | Status | Base URL |
|---------|--------|----------|
| v1 | Current | `/api/v1` |

---

## Upgrade Guide

### From 0.9.x to 1.0.0

1. Database migration required for new tables:
   - `audit_logs`
   - `sso_configs`

2. New environment variables:
   ```
   SSO_SP_ENTITY_ID=https://your-domain.com/sso
   SSO_CALLBACK_URL=https://your-domain.com/api/v1/sso/acs
   ```

3. Rate limiting is now enabled by default

4. MFA is optional but recommended for admin users

---

## Support

- [Documentation](https://vendorauditai-production.up.railway.app/docs)
- [Issues](https://github.com/MikeDominic92/VendorAuditAI/issues)
- [Contact](mailto:contact@vendorauditai.com)
