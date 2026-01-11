<div align="center">

<br/>

# VENDORAUDITAI

<br/>

## v1.0.0 | Enterprise Security Release

<br/>

### AI-Powered Third-Party Risk Management Platform

<br/>
<br/>

[![Version](https://img.shields.io/badge/VERSION-1.0.0-0066FF?style=for-the-badge)](CHANGELOG.md)
[![Build](https://img.shields.io/badge/BUILD-PASSING-00C853?style=for-the-badge)](/)
[![Tests](https://img.shields.io/badge/TESTS-123-00C853?style=for-the-badge)](/)
[![License](https://img.shields.io/badge/LICENSE-ENTERPRISE-FF6B00?style=for-the-badge)](/)

<br/>

[![Live Demo](https://img.shields.io/badge/LIVE_DEMO-vendor--audit--ai.netlify.app-00C853?style=for-the-badge&logo=netlify&logoColor=white)](https://vendor-audit-ai.netlify.app)
[![API](https://img.shields.io/badge/API-OPERATIONAL-00C853?style=for-the-badge&logo=fastapi&logoColor=white)](https://vendorauditai-production.up.railway.app/health)

<br/>
<br/>

---

<br/>

**Transform vendor security assessments from 6-8 hours to under 15 minutes**

<br/>

[Live Demo](https://vendor-audit-ai.netlify.app) | [API Documentation](https://vendorauditai-production.up.railway.app/docs) | [Changelog](CHANGELOG.md) | [Contact Sales](mailto:contact@vendorauditai.com)

<br/>

---

<br/>
<br/>

## THE PROBLEM

<br/>

| Statistic | Impact |
|:---------:|:------:|
| **60%** | of data breaches originate from third-party vendors |
| **$4.45M** | average cost per data breach (IBM 2023) |
| **6-8 hours** | time spent on each manual vendor assessment |
| **$100K-$500K** | annual cost of legacy GRC tools |

<br/>

> *"Third-party vendor risk is the #1 blind spot in enterprise security"*
>
> *- Ponemon Institute*

<br/>
<br/>

---

<br/>
<br/>

## THE SOLUTION

<br/>

### Upload. Analyze. Act.

<br/>

| Step | Action | Result |
|:----:|:------:|:------:|
| **1** | Upload vendor documents | SOC 2, SIG, HECVAT, ISO 27001, Pentests |
| **2** | AI analyzes content | Control extraction, framework mapping, gap detection |
| **3** | Act on findings | Remediation workflows, SLA tracking, monitoring |

<br/>

| Metric | Result |
|:------:|:------:|
| Assessment Time | **< 15 minutes** |
| Cost Reduction | **90%** |
| Accuracy | **97%** |
| Frameworks | **9** |

<br/>
<br/>

---

<br/>
<br/>

## PLATFORM CAPABILITIES

<br/>

| Capability | Description |
|:----------:|:-----------:|
| **Document Intelligence** | PDF, DOCX, scanned docs with Azure AI |
| **Compliance Analysis** | 9 frameworks with gap detection |
| **Remediation Workflow** | SLA management and audit trail |
| **AI Risk Assessment** | NIST AI RMF compliance |
| **Continuous Monitoring** | Scheduled assessments and alerts |
| **Natural Language Query** | Ask questions in plain English |

<br/>
<br/>

---

<br/>
<br/>

## SUPPORTED FRAMEWORKS

<br/>

| Framework | Controls | Industry |
|:---------:|:--------:|:--------:|
| NIST 800-53 | 1,000+ | Federal & Regulated |
| SOC 2 TSC | 64 | SaaS & Cloud |
| ISO 27001 | 114 | International |
| CIS Controls | 153 | Security Baselines |
| PCI-DSS | 250+ | Payments |
| HIPAA | 75 | Healthcare |
| CAIQ | 260+ | Cloud Security |
| NIST AI RMF | 70+ | AI Governance |
| AI Risk | 40+ | AI Vendors |

<br/>
<br/>

---

<br/>
<br/>

## TECHNOLOGY STACK

<br/>

### AI & Machine Learning

Claude Opus 4.5 | Gemini 3 Pro | OpenAI Embeddings | RAG Architecture

<br/>

### Backend

Python 3.12 | FastAPI | SQLAlchemy 2.0 | PostgreSQL | Redis

<br/>

### Frontend

React 18 | TypeScript 5 | TailwindCSS | TanStack Query | Shadcn/UI

<br/>

### Infrastructure

Docker | Railway | Netlify | GitHub Actions | Terraform

<br/>

### Security

SSO/SAML 2.0 | MFA (TOTP) | JWT + OAuth2 | RBAC | Audit Logging | Rate Limiting | AES-256 | TLS 1.3

<br/>
<br/>

---

<br/>
<br/>

## ENTERPRISE SECURITY FEATURES

<br/>

### v1.0.0 Release Highlights

<br/>

| Feature | Description | Status |
|:-------:|:-----------:|:------:|
| **SSO/SAML 2.0** | Azure AD, Okta, Google, OneLogin | LIVE |
| **Multi-Factor Auth** | TOTP with backup recovery codes | LIVE |
| **Audit Logging** | SOC 2 compliant activity tracking | LIVE |
| **Rate Limiting** | Brute force and DDoS protection | LIVE |

<br/>
<br/>

---

<br/>
<br/>

## API REFERENCE

<br/>

**Base URL**

`https://vendorauditai-production.up.railway.app/api/v1`

<br/>

| Category | Endpoints |
|:--------:|:----------|
| **Auth** | `POST /auth/register` `POST /auth/login` `POST /auth/mfa/enable` `POST /auth/mfa/verify` |
| **SSO** | `GET /sso/metadata/{org}` `GET /sso/login/{org}` `POST /sso/acs/{org}` `POST /sso/configure` |
| **Vendors** | `GET /vendors` `POST /vendors` `GET /vendors/{id}` `PUT /vendors/{id}` |
| **Documents** | `GET /documents` `POST /documents/upload` `DELETE /documents/{id}` |
| **Analysis** | `POST /analysis/run` `GET /findings` `POST /query` |
| **Frameworks** | `GET /frameworks` `GET /frameworks/{id}` `GET /frameworks/search` |
| **Remediation** | `GET /remediation/tasks` `POST /remediation/tasks` `POST /remediation/tasks/{id}/transition` |
| **Monitoring** | `GET /monitoring/schedules` `GET /monitoring/alerts` `POST /monitoring/channels` |
| **Audit** | `GET /audit/logs` `GET /audit/logs/export` |

<br/>

[View Full API Documentation](https://vendorauditai-production.up.railway.app/docs)

<br/>
<br/>

---

<br/>
<br/>

## QUICK START

<br/>

### Cloud Demo

<br/>

**https://vendor-audit-ai.netlify.app**

| Credential | Value |
|:----------:|:-----:|
| Email | `demo@vendorauditai.com` |
| Password | `DemoPass123` |

<br/>

### Self-Hosted Deployment

```bash
git clone https://github.com/MikeDominic92/VendorAuditAI.git
cd VendorAuditAI

# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

<br/>
<br/>

---

<br/>
<br/>

## RELEASE HISTORY

<br/>

### v1.0.0 - Enterprise Security (January 2026)

- [x] SSO/SAML 2.0 - Azure AD, Okta, Google, OneLogin
- [x] Multi-Factor Authentication - TOTP with backup codes
- [x] System-Wide Audit Logging - SOC 2 compliant
- [x] API Rate Limiting - Brute force protection
- [x] Dashboard Performance - 3x faster with parallel queries

<br/>

### v0.9.0 - AI & Compliance

- [x] Document analysis engine
- [x] Multi-framework compliance mapping (9 frameworks)
- [x] Natural language query interface
- [x] CAIQ Framework (Cloud Security Alliance)
- [x] NIST AI Risk Management Framework
- [x] AI Vendor Risk Assessment Module
- [x] Remediation Workflow with SLA tracking
- [x] Continuous Monitoring & Alerts
- [x] Multi-channel notifications

<br/>

### Coming Soon

- [ ] Vendor Risk Scoring Algorithm
- [ ] Advanced Analytics Dashboard
- [ ] Excel Export (XLSX)
- [ ] Jira Integration
- [ ] Custom Framework Builder
- [ ] GraphQL API
- [ ] Mobile Application

<br/>
<br/>

---

<br/>
<br/>

## PRICING

<br/>

| Plan | Vendors | Documents/Month | Support | Price |
|:----:|:-------:|:---------------:|:-------:|:-----:|
| **Starter** | 50 | 500 | Email | Contact |
| **Professional** | 200 | 2,000 | Priority | Contact |
| **Enterprise** | Unlimited | Unlimited | Dedicated CSM | Contact |

<br/>

[Contact Sales](mailto:contact@vendorauditai.com)

<br/>
<br/>

---

<br/>
<br/>

## GET STARTED

<br/>

[![Try Demo](https://img.shields.io/badge/TRY_DEMO-00C853?style=for-the-badge&logo=vercel&logoColor=white)](https://vendor-audit-ai.netlify.app)
&nbsp;&nbsp;
[![View API](https://img.shields.io/badge/VIEW_API-0066FF?style=for-the-badge&logo=swagger&logoColor=white)](https://vendorauditai-production.up.railway.app/docs)
&nbsp;&nbsp;
[![Contact Sales](https://img.shields.io/badge/CONTACT_SALES-FF6B00?style=for-the-badge&logo=gmail&logoColor=white)](mailto:contact@vendorauditai.com)

<br/>
<br/>

---

<br/>

### VENDORAUDITAI

**Built for security teams who refuse to accept the status quo.**

<br/>

[Demo](https://vendor-audit-ai.netlify.app) | [API](https://vendorauditai-production.up.railway.app/docs) | [Changelog](CHANGELOG.md) | [Contact](mailto:contact@vendorauditai.com)

<br/>

Copyright 2026 VendorAuditAI. All rights reserved.

</div>
