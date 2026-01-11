<div align="center">

# VendorAuditAI

## Version 1.0.0 - Enterprise Security Release

### Enterprise AI Platform for Third-Party Risk Management

<br/>

[![Version](https://img.shields.io/badge/VERSION-1.0.0-blue?style=for-the-badge)](CHANGELOG.md)
&nbsp;&nbsp;
[![Live Demo](https://img.shields.io/badge/DEMO-LIVE-success?style=for-the-badge&logo=vercel)](https://vendor-audit-ai.netlify.app)
&nbsp;&nbsp;
[![API Status](https://img.shields.io/badge/API-OPERATIONAL-success?style=for-the-badge&logo=fastapi)](https://vendorauditai-production.up.railway.app/health)
&nbsp;&nbsp;
[![Tests](https://img.shields.io/badge/TESTS-123_PASSING-success?style=for-the-badge&logo=pytest)](/)

<br/>

**Automate vendor security assessments from 6-8 hours to under 15 minutes**

[View Demo](https://vendor-audit-ai.netlify.app) &nbsp;|&nbsp; [API Docs](https://vendorauditai-production.up.railway.app/docs) &nbsp;|&nbsp; [Changelog](CHANGELOG.md) &nbsp;|&nbsp; [Contact Sales](mailto:contact@vendorauditai.com)

<br/>

---

<br/>

</div>

## The Problem We Solve

<br/>

<div align="center">

| | |
|:---:|:---:|
| **60%** | of data breaches originate from third-party vendors |
| **$4.45M** | average cost per data breach (IBM 2023) |
| **6-8 hours** | time spent on each manual vendor assessment |
| **$100K-$500K** | annual cost of legacy GRC tools |

</div>

<br/>

> *"Third-party vendor risk is the #1 blind spot in enterprise security"*
> *— Ponemon Institute*

<br/>

---

<br/>

## Our Solution

<br/>

<div align="center">

### Upload. Analyze. Act.

</div>

<br/>

**1. Upload** any vendor security document (SOC 2, SIG, HECVAT, ISO 27001, Pentest Reports)

**2. Analyze** with AI that extracts controls, maps to frameworks, and identifies gaps

**3. Act** on findings with remediation workflows, SLA tracking, and continuous monitoring

<br/>

<div align="center">

| Metric | Result |
|:------:|:------:|
| Assessment Time | **Under 15 min** |
| Cost Savings | **90%** |
| Accuracy | **97%** |
| Frameworks | **9** |

</div>

<br/>

---

<br/>

## Platform Capabilities

<br/>

### Document Intelligence

> PDF, DOCX, and scanned documents with Azure Document Intelligence
> Table extraction and 50+ language support

<br/>

### Compliance Analysis

> Automated gap detection across 9 frameworks
> Risk scoring with page-specific citations

<br/>

### Remediation Workflow

> Full issue lifecycle with SLA management
> Task assignment, audit trail, and threaded comments

<br/>

### AI Vendor Risk Assessment

> Data provenance, model security, bias detection
> Built on NIST AI Risk Management Framework

<br/>

### Continuous Monitoring

> Scheduled assessments: daily, weekly, monthly, quarterly
> Multi-channel alerts: Slack, Email, Teams, Webhooks

<br/>

### Natural Language Query

> Ask questions like *"Which vendors lack MFA?"*
> Semantic search across your entire vendor portfolio

<br/>

---

<br/>

## Supported Frameworks

<br/>

<div align="center">

| Framework | Controls | Industry |
|:---------:|:--------:|:--------:|
| **NIST 800-53** | 1,000+ | Federal & Regulated |
| **SOC 2 TSC** | 64 | SaaS & Cloud |
| **ISO 27001** | 114 | International |
| **CIS Controls** | 153 | Security Baselines |
| **PCI-DSS** | 250+ | Payments |
| **HIPAA** | 75 | Healthcare |
| **CAIQ** | 260+ | Cloud Security |
| **NIST AI RMF** | 70+ | AI Governance |
| **AI Risk** | 40+ | AI Vendors |

</div>

<br/>

---

<br/>

## Technology

<br/>

<div align="center">

**AI & ML**

Claude Opus 4.5 &nbsp;|&nbsp; Gemini 3 Pro &nbsp;|&nbsp; OpenAI Embeddings &nbsp;|&nbsp; RAG

<br/>

**Backend**

Python 3.12 &nbsp;|&nbsp; FastAPI &nbsp;|&nbsp; SQLAlchemy 2.0 &nbsp;|&nbsp; PostgreSQL

<br/>

**Frontend**

React 18 &nbsp;|&nbsp; TypeScript 5 &nbsp;|&nbsp; TailwindCSS &nbsp;|&nbsp; TanStack Query

<br/>

**Infrastructure**

Docker &nbsp;|&nbsp; Railway &nbsp;|&nbsp; Netlify &nbsp;|&nbsp; GitHub Actions

<br/>

**Security**

SSO/SAML 2.0 &nbsp;|&nbsp; MFA (TOTP) &nbsp;|&nbsp; JWT + OAuth2 &nbsp;|&nbsp; RBAC &nbsp;|&nbsp; Audit Logging &nbsp;|&nbsp; Rate Limiting &nbsp;|&nbsp; AES-256 &nbsp;|&nbsp; TLS 1.3

</div>

<br/>

---

<br/>

## Quick Start

<br/>

### Cloud Demo

<br/>

<div align="center">

**https://vendor-audit-ai.netlify.app**

| | |
|:--|:--|
| Email | `demo@vendorauditai.com` |
| Password | `DemoPass123` |

</div>

<br/>

### Self-Hosted

```bash
git clone https://github.com/MikeDominic92/VendorAuditAI.git
cd VendorAuditAI

# Backend
cd backend && python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]" && cp .env.example .env
uvicorn app.main:app --reload

# Frontend
cd ../frontend && npm install && npm run dev
```

<br/>

---

<br/>

## API Reference

<br/>

<div align="center">

**Base URL:** `https://vendorauditai-production.up.railway.app/api/v1`

</div>

<br/>

| Category | Endpoints |
|:---------|:----------|
| **Auth** | `POST /auth/register` · `POST /auth/login` · `POST /auth/mfa/enable` · `POST /auth/mfa/verify` |
| **SSO** | `GET /sso/metadata/{org}` · `GET /sso/login/{org}` · `POST /sso/acs/{org}` · `POST /sso/configure` |
| **Vendors** | `GET /vendors` · `POST /vendors` |
| **Documents** | `GET /documents` · `POST /documents/upload` |
| **Analysis** | `POST /analysis/run` · `GET /findings` · `POST /query` |
| **Frameworks** | `GET /frameworks` · `GET /frameworks/search` |
| **Remediation** | `GET /remediation/tasks` · `POST /remediation/tasks` · `POST /remediation/tasks/{id}/transition` |
| **Monitoring** | `GET /monitoring/schedules` · `GET /monitoring/alerts` · `POST /monitoring/channels` |
| **Audit** | `GET /audit/logs` · `GET /audit/logs/export` |

<br/>

<div align="center">

[View Full API Documentation](https://vendorauditai-production.up.railway.app/docs)

</div>

<br/>

---

<br/>

## Roadmap

<br/>

### v1.0.0 - Enterprise Security Release (January 2026)

- [x] **SSO/SAML 2.0** - Azure AD, Okta, Google, OneLogin
- [x] **Multi-Factor Authentication** - TOTP with backup codes
- [x] **System-Wide Audit Logging** - SOC 2 compliant
- [x] **API Rate Limiting** - Brute force protection
- [x] Dashboard performance optimization (3x faster)

<br/>

### v0.9.0 - AI & Compliance Release

- [x] Document analysis engine
- [x] Multi-framework compliance mapping (9 frameworks)
- [x] Natural language query interface
- [x] Real-time dashboard
- [x] CAIQ Framework (Cloud Security Alliance)
- [x] NIST AI Risk Management Framework
- [x] AI Vendor Risk Assessment Module
- [x] Remediation Workflow with SLA tracking
- [x] Continuous Monitoring & Alerts
- [x] Multi-channel notifications (Slack, Email, Teams, Webhooks)

<br/>

### Coming Soon

- [ ] Vendor Risk Scoring Algorithm
- [ ] Advanced Analytics Dashboard
- [ ] Excel Export (XLSX)
- [ ] Jira Integration
- [ ] Custom framework builder
- [ ] GraphQL API
- [ ] Mobile application

<br/>

---

<br/>

## Pricing

<br/>

<div align="center">

| Plan | Vendors | Documents | Support |
|:----:|:-------:|:---------:|:-------:|
| **Starter** | 50 | 500/mo | Email |
| **Professional** | 200 | 2,000/mo | Priority |
| **Enterprise** | Unlimited | Unlimited | Dedicated CSM |

<br/>

[Contact Sales](mailto:contact@vendorauditai.com)

</div>

<br/>

---

<br/>

<div align="center">

## Get Started Today

<br/>

[![Try Demo](https://img.shields.io/badge/Try_Demo-00C853?style=for-the-badge&logo=vercel&logoColor=white)](https://vendor-audit-ai.netlify.app)
&nbsp;&nbsp;&nbsp;
[![View API](https://img.shields.io/badge/View_API-0066FF?style=for-the-badge&logo=swagger&logoColor=white)](https://vendorauditai-production.up.railway.app/docs)
&nbsp;&nbsp;&nbsp;
[![Contact](https://img.shields.io/badge/Contact_Sales-FF6B00?style=for-the-badge&logo=gmail&logoColor=white)](mailto:contact@vendorauditai.com)

<br/>
<br/>

---

<br/>

**VendorAuditAI**

*Built for security teams who refuse to accept the status quo.*

<br/>

[Demo](https://vendor-audit-ai.netlify.app) &nbsp;|&nbsp; [API](https://vendorauditai-production.up.railway.app/docs) &nbsp;|&nbsp; [Email](mailto:contact@vendorauditai.com)

</div>
