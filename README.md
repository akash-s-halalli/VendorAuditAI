<div align="center">

<br/>

<img src="https://img.shields.io/badge/VENDORAUDITAI-000000?style=for-the-badge&logoColor=white" alt="VendorAuditAI" height="60"/>

<br/>
<br/>

# The Future of Third-Party Risk Management

<br/>

**Enterprise AI Platform That Transforms Vendor Security Assessments**

*From 8 Hours to 15 Minutes. From Chaos to Clarity.*

<br/>

[![Version](https://img.shields.io/badge/v0.2.0-PRODUCTION-00D4AA?style=for-the-badge)](CHANGELOG.md)
[![Uptime](https://img.shields.io/badge/UPTIME-99.9%25-00D4AA?style=for-the-badge)]()
[![Tests](https://img.shields.io/badge/129_TESTS-PASSING-00D4AA?style=for-the-badge)]()
[![Security](https://img.shields.io/badge/SOC_2-COMPLIANT-00D4AA?style=for-the-badge)]()

<br/>

[**Launch Demo**](https://vendor-audit-ai.netlify.app) | [**API Docs**](https://vendorauditai-production.up.railway.app/docs) | [**Platform Overview**](docs/PLATFORM_OVERVIEW.md) | [**Contact Sales**](mailto:contact@vendorauditai.com)

<br/>

---

<br/>

</div>

## Why VendorAuditAI Exists

<br/>

Every enterprise today relies on dozens, sometimes hundreds, of third-party vendors. Each vendor is a potential gateway for data breaches, compliance failures, and operational risks.

**The problem?** Evaluating vendor security is painfully manual.

| The Old Way | The VendorAuditAI Way |
|:------------|:----------------------|
| 6-8 hours reading a single SOC 2 report | 15 minutes with AI-powered analysis |
| Spreadsheets and manual tracking | Automated workflows with SLA management |
| Missed risks buried in 200-page documents | Instant gap detection across 9 frameworks |
| $100K-$500K/year for legacy GRC tools | Modern, scalable, cost-effective |

<br/>

> **"60% of data breaches originate from third-party vendors."**
>
> *- Ponemon Institute*

<br/>

---

<br/>

## How It Works

<br/>

<div align="center">

```
 UPLOAD              ANALYZE              ACT
   |                    |                  |
   v                    v                  v
+--------+         +---------+        +----------+
|  SOC 2 |         |   AI    |        | Findings |
| SIG    |  --->   | Engine  |  --->  | Reports  |
| HECVAT |         | (Claude)|        | Actions  |
| ISO    |         +---------+        +----------+
+--------+              |
                        v
                 +-------------+
                 | 9 Frameworks|
                 | Gap Analysis|
                 | Risk Score  |
                 +-------------+
```

</div>

<br/>

### Step 1: Upload
Drop your vendor documents - SOC 2 Type II, SIG Lite, SIG Core, HECVAT, ISO 27001, penetration test reports, or any security questionnaire.

### Step 2: Analyze
Our AI engine powered by Claude Opus 4.5 reads, understands, and maps every control to your compliance requirements. Automatically.

### Step 3: Act
Get actionable findings, assign remediation tasks, track SLAs, and monitor continuously. All in one platform.

<br/>

---

<br/>

## Platform Capabilities

<br/>

### Document Intelligence
| Feature | Description |
|:--------|:------------|
| **Multi-Format Support** | PDF, DOCX, scanned documents with OCR |
| **Smart Parsing** | Automatic section detection and control extraction |
| **Chunk Indexing** | Semantic search across all uploaded documents |

<br/>

### AI-Powered Analysis
| Feature | Description |
|:--------|:------------|
| **Natural Language Query** | Ask questions in plain English, get cited answers |
| **Gap Detection** | Automatic identification of missing or weak controls |
| **Risk Scoring** | AI-generated risk assessments per vendor |
| **Multi-Framework Mapping** | One document, mapped to 9 compliance frameworks |

<br/>

### Workflow Automation
| Feature | Description |
|:--------|:------------|
| **Remediation Tasks** | Create, assign, and track remediation items |
| **SLA Management** | Set deadlines, escalate automatically |
| **Continuous Monitoring** | Scheduled assessments with alerting |
| **Audit Trail** | Complete history for compliance audits |

<br/>

### Enterprise Security
| Feature | Description |
|:--------|:------------|
| **SSO/SAML 2.0** | Azure AD, Okta, Google Workspace, OneLogin |
| **Multi-Factor Auth** | TOTP with backup recovery codes |
| **Role-Based Access** | Admin, Analyst, Viewer permissions |
| **API Rate Limiting** | DDoS and brute force protection |
| **Encryption** | AES-256 at rest, TLS 1.3 in transit |

<br/>

---

<br/>

## Supported Compliance Frameworks

<br/>

<div align="center">

| Framework | Controls | Best For |
|:---------:|:--------:|:---------|
| **SOC 2 TSC** | 64 | SaaS vendors, cloud services |
| **NIST 800-53** | 1,000+ | Federal contractors, regulated industries |
| **ISO 27001** | 114 | International compliance |
| **CIS Controls** | 153 | Security baselines |
| **PCI-DSS** | 250+ | Payment processors |
| **HIPAA** | 75 | Healthcare vendors |
| **CAIQ** | 260+ | Cloud security (CSA) |
| **NIST AI RMF** | 70+ | AI/ML vendors |
| **Custom** | Unlimited | Your internal frameworks |

</div>

<br/>

---

<br/>

## Technology Architecture

<br/>

```
+------------------+     +------------------+     +------------------+
|    FRONTEND      |     |     BACKEND      |     |   AI SERVICES    |
+------------------+     +------------------+     +------------------+
| React 18         |     | FastAPI          |     | Claude Opus 4.5  |
| TypeScript 5     |<--->| Python 3.12      |<--->| Gemini 2.0 Flash |
| TailwindCSS      |     | SQLAlchemy 2.0   |     | OpenAI Embeddings|
| TanStack Query   |     | PostgreSQL       |     | RAG Architecture |
| Shadcn/UI        |     | Redis Cache      |     |                  |
+------------------+     +------------------+     +------------------+
        |                        |                        |
        +------------------------+------------------------+
                                 |
                    +------------------------+
                    |    INFRASTRUCTURE      |
                    +------------------------+
                    | Railway (Backend)      |
                    | Netlify (Frontend)     |
                    | GitHub Actions (CI/CD) |
                    | Docker Containers      |
                    +------------------------+
```

<br/>

---

<br/>

## Live Demo

<br/>

<div align="center">

### [https://vendor-audit-ai.netlify.app](https://vendor-audit-ai.netlify.app)

<br/>

| | |
|:--|:--|
| **Email** | `newdemo@vendorauditai.com` |
| **Password** | `Demo12345` |

<br/>

*Full access to all features. Sample documents pre-loaded.*

</div>

<br/>

---

<br/>

## API Reference

<br/>

**Base URL:** `https://vendorauditai-production.up.railway.app/api/v1`

<br/>

### Authentication
```bash
# Login
POST /auth/login
Content-Type: application/x-www-form-urlencoded

username=user@company.com&password=yourpassword

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

<br/>

### Core Endpoints

| Category | Endpoints | Description |
|:---------|:----------|:------------|
| **Auth** | `POST /auth/login` `POST /auth/register` | Authentication |
| **Documents** | `POST /documents/upload` `GET /documents` | Document management |
| **Query** | `POST /query` | Natural language Q&A |
| **Analysis** | `POST /analysis/documents/{id}/analyze` | Run AI analysis |
| **Vendors** | `GET /vendors` `POST /vendors` | Vendor management |
| **Findings** | `GET /findings` | View analysis results |
| **Frameworks** | `GET /frameworks` `GET /frameworks/search` | Compliance frameworks |
| **Remediation** | `GET /remediation/tasks` `POST /remediation/tasks` | Task management |
| **Monitoring** | `GET /monitoring/alerts` | Continuous monitoring |
| **Audit** | `GET /audit/logs` | Audit trail |

<br/>

[**View Full API Documentation**](https://vendorauditai-production.up.railway.app/docs)

<br/>

---

<br/>

## Quick Start

<br/>

### Option 1: Cloud (Recommended)

Visit [vendor-audit-ai.netlify.app](https://vendor-audit-ai.netlify.app) and create an account.

<br/>

### Option 2: Self-Hosted

```bash
# Clone the repository
git clone https://github.com/MikeDominic92/VendorAuditAI.git
cd VendorAuditAI

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env       # Configure your API keys
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

<br/>

### Environment Variables

```env
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/vendorauditai
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-min-32-chars

# LLM Provider (choose one)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Or use Gemini
LLM_PROVIDER=gemini
GOOGLE_API_KEY=AIza...

# Embeddings
OPENAI_API_KEY=sk-...
```

<br/>

---

<br/>

## Release History

<br/>

### v0.2.0 - Production Release (January 2026)
- CORS configuration for cross-origin deployments
- Document processing pipeline with async optimization
- AI-powered Query feature with source citations
- Multi-LLM support (Anthropic Claude, Google Gemini)
- Database async operation fixes
- 129 passing tests

### v0.1.0 - Initial Release
- Document upload and parsing (PDF, DOCX)
- 9 compliance framework mappings
- Natural language query interface
- Remediation workflow with SLA tracking
- Continuous monitoring and alerts
- SSO/SAML 2.0 integration
- Multi-factor authentication

<br/>

### Roadmap

- [ ] Vendor Risk Scoring Algorithm
- [ ] Advanced Analytics Dashboard
- [ ] Excel/CSV Export
- [ ] Jira & ServiceNow Integration
- [ ] Custom Framework Builder
- [ ] Mobile Application (iOS/Android)
- [ ] GraphQL API
- [ ] On-Premise Deployment Option

<br/>

---

<br/>

## Competitive Advantage

<br/>

<div align="center">

**Why VendorAuditAI Wins**

</div>

<br/>

```
DOCUMENT ANALYSIS SPEED COMPARISON

VendorAuditAI     [==================] 15 minutes
                  AI reads entire document, extracts controls

Legacy GRC        [================================================================] 6-8 hours
                  Manual analyst review required
```

<br/>

| Capability | VendorAuditAI | OneTrust | Vanta | SecurityScorecard |
|:-----------|:-------------:|:--------:|:-----:|:-----------------:|
| **AI Document Analysis** | Yes | Limited | No | No |
| **Natural Language Query** | Yes | No | No | No |
| **Time to First Assessment** | 15 min | 60+ days | 7 days | N/A |
| **Starting Price** | $$ | $$$$$ | $$$ | $$$$ |
| **Multi-Framework Mapping** | 9 frameworks | 9+ | 3 | External only |

<br/>

[**View Full Competitive Analysis**](COMPETITIVE_ANALYSIS.md) | [**Platform Deep Dive**](docs/PLATFORM_OVERVIEW.md)

<br/>

---

<br/>

## Enterprise Plans

<br/>

<div align="center">

| | Starter | Professional | Enterprise |
|:--|:-------:|:------------:|:----------:|
| **Vendors** | 50 | 200 | Unlimited |
| **Documents/Month** | 500 | 2,000 | Unlimited |
| **Users** | 5 | 25 | Unlimited |
| **Frameworks** | 3 | All 9 | All + Custom |
| **SSO** | - | Yes | Yes |
| **API Access** | - | Yes | Yes |
| **SLA** | Email | Priority | Dedicated CSM |
| **Deployment** | Cloud | Cloud | Cloud or On-Prem |

<br/>

[**Contact Sales**](mailto:contact@vendorauditai.com)

</div>

<br/>

---

<br/>

## Security & Compliance

<br/>

VendorAuditAI is built with enterprise security as a foundation, not an afterthought.

| Certification | Status |
|:--------------|:-------|
| SOC 2 Type II | In Progress |
| ISO 27001 | Planned |
| GDPR Compliant | Yes |
| CCPA Compliant | Yes |

<br/>

**Security Features:**
- End-to-end encryption (AES-256 at rest, TLS 1.3 in transit)
- Zero-trust architecture
- Regular penetration testing
- 99.9% uptime SLA
- Data residency options (US, EU)

<br/>

---

<br/>

## Support

<br/>

| Channel | Response Time |
|:--------|:--------------|
| Documentation | [docs.vendorauditai.com](https://vendorauditai-production.up.railway.app/docs) |
| Email Support | support@vendorauditai.com |
| Enterprise Support | Dedicated Slack channel |

<br/>

---

<br/>

<div align="center">

## Ready to Transform Your Vendor Risk Program?

<br/>

[![Start Free Trial](https://img.shields.io/badge/START_FREE_TRIAL-00D4AA?style=for-the-badge)](https://vendor-audit-ai.netlify.app)
&nbsp;&nbsp;&nbsp;
[![Schedule Demo](https://img.shields.io/badge/SCHEDULE_DEMO-0066FF?style=for-the-badge)](mailto:contact@vendorauditai.com)
&nbsp;&nbsp;&nbsp;
[![View API](https://img.shields.io/badge/VIEW_API-333333?style=for-the-badge)](https://vendorauditai-production.up.railway.app/docs)

<br/>
<br/>

---

<br/>

**VendorAuditAI**

*Securing the supply chain, one vendor at a time.*

<br/>

[Website](https://vendor-audit-ai.netlify.app) | [API](https://vendorauditai-production.up.railway.app/docs) | [GitHub](https://github.com/MikeDominic92/VendorAuditAI) | [Contact](mailto:contact@vendorauditai.com)

<br/>

Copyright 2026 VendorAuditAI. All rights reserved.

<br/>

</div>
