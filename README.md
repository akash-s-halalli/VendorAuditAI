<p align="center">
  <img src="https://img.shields.io/badge/VENDORAUDITAI-000000?style=for-the-badge&logoColor=white" alt="VendorAuditAI" height="80"/>
</p>

<h1 align="center">VendorAuditAI</h1>

<h3 align="center">AI-Powered Third-Party Risk Management Platform</h3>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB.svg" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688.svg" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB.svg" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-5.0-3178C6.svg" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Claude-Opus_4.5-CC785C.svg" alt="Claude"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1.svg" alt="PostgreSQL"/>
  <img src="https://img.shields.io/badge/Version-1.0.0-00D4AA.svg" alt="Version"/>
  <img src="https://img.shields.io/badge/Tests-129_Passing-00D4AA.svg" alt="Tests"/>
  <img src="https://img.shields.io/badge/AI_Agents-4_Active-CC785C.svg" alt="AI Agents"/>
  <img src="https://img.shields.io/badge/License-Proprietary-red.svg" alt="License"/>
</p>

<p align="center">
  <strong>Transform vendor security assessments from 8 hours to 15 minutes using AI-powered document analysis and multi-framework compliance mapping</strong>
</p>

<table align="center">
<tr>
<td align="center">
<h3>Try the Live Demo</h3>
<a href="https://vendor-audit-ai.netlify.app"><strong>vendor-audit-ai.netlify.app</strong></a><br/><br/>
<code>Email: newdemo@vendorauditai.com</code><br/>
<code>Password: Demo12345</code>
</td>
</tr>
</table>

---

## The Problem

<table>
<tr>
<td width="50%">

### Third-Party Risk is Manual and Broken

- **60% of data breaches** originate from third-party vendors (Ponemon Institute)
- **$4.88M average cost** per data breach in 2024 (IBM)
- **6-8 hours per vendor** to manually review a single SOC 2 report
- **200+ page documents** with critical risks buried in dense text
- **Spreadsheet chaos** - no centralized tracking or automation
- **Missed SLAs** - remediation tasks lost in email threads
- **Audit failures** - incomplete evidence and gaps in coverage

</td>
<td width="50%">

### What Security Teams Need

- **Instant document analysis** - AI reads and understands vendor reports
- **Multi-framework mapping** - One document mapped to 12 compliance frameworks
- **Natural language queries** - Ask questions, get cited answers
- **Automated gap detection** - Find missing controls automatically
- **Remediation workflows** - Track tasks with SLA management
- **Continuous monitoring** - Scheduled assessments with alerts
- **Audit-ready reports** - Complete evidence trail for compliance

</td>
</tr>
</table>

---

## The Solution: VendorAuditAI

<table>
<tr>
<td width="33%">

| Metric | Value |
|--------|-------|
| **Assessment Time** | 15 minutes |
| **Time Savings** | 97% reduction |
| **Frameworks** | 12 supported |
| **Document Types** | PDF, DOCX, OCR |

</td>
<td width="33%">

| Metric | Value |
|--------|-------|
| **AI Engine** | Claude Opus 4.5 |
| **Embeddings** | OpenAI |
| **Architecture** | RAG Pipeline |
| **Uptime SLA** | 99.9% |

</td>
<td width="33%">

| Metric | Value |
|--------|-------|
| **API Endpoints** | 90+ |
| **Test Coverage** | 129 tests |
| **Auth** | SSO/SAML 2.0 |
| **Encryption** | AES-256/TLS 1.3 |

</td>
</tr>
</table>

<br/>

| Capability | Technology | Outcome |
|------------|------------|---------|
| Document Intelligence | PDF parsing, OCR, semantic chunking | Extract text from any vendor document format |
| AI-Powered Analysis | Claude Opus 4.5 + Gemini 3.0 + RAG | Natural language Q&A with source citations |
| Multi-Framework Mapping | 12 compliance frameworks, 2500+ controls | One document mapped to SOC 2, NIST, ISO, SIG, DORA |
| Gap Detection | AI control analysis + framework comparison | Automatic identification of missing or weak controls |
| Vendor Management | Full CRUD, 25 categories, auto-classification | Complete vendor lifecycle management |
| **AI Agent Network** | 4 autonomous agents with task execution | Continuous threat detection, risk scoring, vulnerability scanning |
| Remediation Workflow | Task management, SLA tracking, status workflows | Never miss a remediation deadline |
| Continuous Monitoring | Scheduled assessments, alerts, notification channels | Proactive vendor risk management |
| Export & Reporting | CSV, PDF export with findings | Audit-ready compliance documentation |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           VENDORAUDITAI ARCHITECTURE                         │
└─────────────────────────────────────────────────────────────────────────────┘

                              ┌─────────────────┐
                              │   USER/BROWSER  │
                              └────────┬────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Netlify)                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   React 18  │  │ TypeScript  │  │ TailwindCSS │  │  Shadcn/UI  │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ HTTPS/REST API
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BACKEND (Railway)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   FastAPI   │  │ SQLAlchemy  │  │    Async    │  │  Pydantic   │        │
│  │  Python 3.12│  │     2.0     │  │   Workers   │  │  Schemas    │        │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │
└──────────┬──────────────────┬──────────────────┬────────────────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────────────────────┐
│   PostgreSQL     │ │   Redis Cache    │ │         AI SERVICES              │
│   ┌──────────┐   │ │   ┌──────────┐   │ │  ┌────────────┐ ┌────────────┐  │
│   │ Documents│   │ │   │ Sessions │   │ │  │Claude Opus │ │  OpenAI    │  │
│   │ Chunks   │   │ │   │ Rate Lim │   │ │  │   4.5      │ │ Embeddings │  │
│   │ Findings │   │ │   └──────────┘   │ │  └────────────┘ └────────────┘  │
│   │ Vendors  │   │ └──────────────────┘ │  ┌────────────┐                  │
│   └──────────┘   │                      │  │  Gemini    │                  │
└──────────────────┘                      │  │    3.0     │                  │
                                          │  └────────────┘                  │
                                          └──────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                           DOCUMENT PROCESSING PIPELINE                       │
│                                                                              │
│   UPLOAD ──► PARSE ──► CHUNK ──► EMBED ──► INDEX ──► READY FOR QUERY       │
│     │          │         │         │         │            │                 │
│   PDF/DOCX   Extract   Semantic  Vector   PostgreSQL   Natural Language    │
│   Validation  Text     Splitting  Store   + pgvector   Q&A with Citations  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Supported Compliance Frameworks

| Framework | Controls | Version | Best For |
|:---------:|:--------:|:-------:|:---------|
| **SOC 2 TSC** | 64 | 2017 | SaaS vendors, cloud services |
| **SIG 2026** | 800+ | 2026 | Industry gold standard, all vendors |
| **NIST CSF** | 108 | 2.0 | Critical infrastructure, risk management |
| **ISO 27001** | 114 | 2022 | International compliance |
| **CIS Controls** | 153 | 8.0 | Security baselines |
| **DORA** | 100+ | 2025 | EU financial entities (mandatory) |
| **HECVAT** | 200+ | 3.06 | Higher education vendors |
| **CAIQ** | 260+ | 4.0 | Cloud security (CSA STAR) |
| **NIST AI RMF** | 70+ | 1.0 | AI/ML vendors |
| **AI Risk** | 50+ | 1.0 | AI vendor assessment |

---

## Vendor Categorization (25 Categories)

VendorAuditAI implements a comprehensive DoorDash-style TPRM vendor taxonomy with automatic categorization based on keywords, service types, and data access patterns.

### Risk Tiers

| Tier | Risk Level | Assessment Approach | Review Frequency |
|:----:|:----------:|:--------------------|:-----------------|
| **Tier 1** | Critical | SOC 2 Type II + SIG Core + on-site validation | Quarterly |
| **Tier 2** | High | SOC 2 Type II + SIG Core | Semi-annual |
| **Tier 3** | Medium | SOC 2 Type I/II + SIG Lite | Annual |
| **Tier 4** | Low | Self-attestation + basic questionnaire | Every 2-3 years |

### Category Taxonomy

<table>
<tr>
<td width="33%" valign="top">

**Tier 1 - Critical**
- Cloud Infrastructure (AWS, GCP, Azure)
- Data Warehouse (Snowflake, Databricks)
- Payment Processing (Stripe, Adyen)
- Identity & Access (Okta, Auth0)
- Background Check (Checkr, Sterling)
- Healthcare/PHI Vendors
- POS Integration (Toast, Square)

</td>
<td width="33%" valign="top">

**Tier 2 - High**
- AI/ML Platforms (Anthropic, OpenAI)
- Fraud Detection (Sift, Forter)
- Analytics & BI (Amplitude, Mixpanel)
- Customer Support (Zendesk, Salesforce)
- Mapping & Logistics (Mapbox, HERE)
- HR & Workforce (Workday, ADP)
- Marketing & Ads (Braze, Segment)
- Security Tools (CrowdStrike, Wiz)
- Insurance & Risk Partners

</td>
<td width="33%" valign="top">

**Tier 3/4 - Medium/Low**
- Communication (Twilio, SendGrid)
- DevOps Tools (GitHub, PagerDuty)
- Legal & Contract (DocuSign, Ironclad)
- Office Collaboration (Slack, Zoom)
- Physical Security (Verkada, Kastle)
- Tax Compliance (Everlance, TaxBandits)
- Fleet Management (Samsara, Geotab)
- Food Safety (FoodLogiQ, Squadle)
- Autonomous/Robotics (Starship, Nuro)

</td>
</tr>
</table>

### Auto-Categorization API

```bash
# Categorize a vendor
curl -X POST "https://vendorauditai-production.up.railway.app/api/v1/categorization/analyze" \
  -H "Content-Type: application/json" \
  -d '{"vendor_name": "Stripe", "vendor_description": "Payment processing platform"}'

# Response
{
  "primary_category": "payment_processing",
  "confidence": 0.95,
  "risk_level": "critical",
  "recommended_frameworks": ["PCI-DSS", "SOC 2 Type II", "SOC 1"],
  "data_types": ["credit_cards", "bank_accounts", "ssn", "transaction_data"],
  "assessment_priority": "immediate"
}
```

---

## AI Agent Network

VendorAuditAI features four autonomous AI agents that continuously monitor and assess your vendor security ecosystem.

| Agent | Role | Capabilities |
|:------|:-----|:-------------|
| **Sentinel Prime** | Threat Detection | Scans documents for security risks, anomalies, and emerging threats. Monitors critical/high findings. |
| **Vector Analyst** | Risk Assessment | Calculates vendor risk scores based on findings, compliance status, and historical data. |
| **Watchdog Zero** | Vulnerability Scanner | Identifies security gaps, missing controls, expired certifications, and documentation deficiencies. |
| **Audit Core** | Compliance Verification | Maps vendor documents to regulatory frameworks and calculates compliance coverage. |

### Agent API

```bash
# List all agents
curl -X GET "https://vendorauditai-production.up.railway.app/api/v1/agents" \
  -H "Authorization: Bearer $TOKEN"

# Run a task on an agent
curl -X POST "https://vendorauditai-production.up.railway.app/api/v1/agents/{agent_id}/tasks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"task_type": "scan", "input_data": {}}'

# View agent logs
curl -X GET "https://vendorauditai-production.up.railway.app/api/v1/agents/{agent_id}/logs" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Use Cases

<table>
<tr>
<td width="50%">

### SOC 2 Report Analysis

**Scenario:** Security analyst receives 180-page SOC 2 Type II report from cloud vendor.

**Before VendorAuditAI:**
- 6-8 hours reading through dense audit language
- Manual extraction of control gaps
- Spreadsheet tracking of findings
- Risk of missing critical issues

**With VendorAuditAI:**
- Upload PDF, processing complete in 2 minutes
- Ask: "What encryption controls are documented?"
- AI returns cited answer with page references
- Automatic gap detection across 12 frameworks
- Remediation tasks auto-created with SLAs

</td>
<td width="50%">

### Multi-Vendor Assessment Program

**Scenario:** Enterprise onboarding 50 new vendors for digital transformation initiative.

**Before VendorAuditAI:**
- 400+ hours of analyst time
- Inconsistent assessment criteria
- No standardized risk scoring
- Audit findings for incomplete coverage

**With VendorAuditAI:**
- Batch upload all vendor documents
- Auto-categorization by vendor type
- Standardized risk scoring algorithm
- Framework mapping for each vendor tier
- Executive dashboard with risk heatmap
- Complete audit trail for compliance

</td>
</tr>
<tr>
<td width="50%">

### Continuous Vendor Monitoring

**Scenario:** Existing vendor's SOC 2 report expires, new assessment needed.

**Before VendorAuditAI:**
- Manual calendar tracking
- Email reminders often missed
- No comparison to previous assessment
- Reactive instead of proactive

**With VendorAuditAI:**
- Automated expiration alerts
- Request new documentation workflow
- AI comparison to previous assessment
- Track remediation progress over time
- Trend analysis and risk scoring

</td>
<td width="50%">

### Regulatory Compliance (DORA/NIS2)

**Scenario:** EU financial entity must comply with DORA ICT third-party requirements.

**Before VendorAuditAI:**
- Manual mapping to DORA articles
- Consultant fees for gap analysis
- Uncertain coverage of requirements
- Risk of regulatory penalties

**With VendorAuditAI:**
- Upload vendor documents
- Automatic DORA framework mapping
- Gap analysis against all 5 DORA pillars
- Evidence collection for regulators
- Third-party register generation
- Audit-ready compliance reports

</td>
</tr>
</table>

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16+
- API keys: Anthropic (Claude) or Google (Gemini), OpenAI (embeddings)

### Installation

```bash
# Clone the repository
git clone https://github.com/MikeDominic92/VendorAuditAI.git
cd VendorAuditAI

# Backend setup
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys and database URL

# Run backend
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Variables

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/vendorauditai

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-min-32-chars

# LLM Provider (choose one)
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Or use Gemini
# LLM_PROVIDER=gemini
# GOOGLE_API_KEY=AIza...

# Embeddings (required)
OPENAI_API_KEY=sk-...
```

---

## API Endpoints

### Core Endpoints

| Category | Method | Endpoint | Description |
|:---------|:------:|:---------|:------------|
| **Auth** | POST | `/api/v1/auth/login` | User authentication |
| **Auth** | POST | `/api/v1/auth/register` | User registration |
| **Agents** | GET | `/api/v1/agents` | List AI agents |
| **Agents** | POST | `/api/v1/agents/{id}/tasks` | Run agent task |
| **Agents** | GET | `/api/v1/agents/{id}/logs` | View agent logs |
| **Documents** | POST | `/api/v1/documents/upload` | Upload vendor document |
| **Documents** | GET | `/api/v1/documents` | List all documents |
| **Query** | POST | `/api/v1/query` | Natural language Q&A |
| **Analysis** | POST | `/api/v1/analysis/documents/{id}/analyze` | Run AI analysis |
| **Vendors** | GET | `/api/v1/vendors` | List vendors |
| **Vendors** | GET | `/api/v1/vendors/{id}` | Get vendor details |
| **Vendors** | POST | `/api/v1/vendors` | Create vendor |
| **Frameworks** | GET | `/api/v1/frameworks` | List compliance frameworks |
| **Frameworks** | GET | `/api/v1/frameworks/search` | Search controls |
| **Categorization** | POST | `/api/v1/categorization/analyze` | Auto-categorize vendor |
| **Categorization** | GET | `/api/v1/categorization/categories` | List 25 vendor categories |
| **Categorization** | POST | `/api/v1/categorization/batch` | Batch categorize vendors |
| **Findings** | GET | `/api/v1/analysis/findings` | View analysis findings |
| **Remediation** | GET | `/api/v1/remediation/tasks` | List remediation tasks |
| **Monitoring** | GET | `/api/v1/monitoring/alerts` | View monitoring alerts |

### Live API Documentation

- **Swagger UI:** https://vendorauditai-production.up.railway.app/docs
- **ReDoc:** https://vendorauditai-production.up.railway.app/redoc

---

## Live Demo

| | |
|:--|:--|
| **URL** | https://vendor-audit-ai.netlify.app |
| **Email** | `newdemo@vendorauditai.com` |
| **Password** | `Demo12345` |

*Full access to all features. Sample documents pre-loaded for testing.*

---

## Project Structure

```
VendorAuditAI/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/     # REST API endpoints
│   │   ├── data/frameworks/      # 12 compliance framework definitions
│   │   ├── models/               # SQLAlchemy ORM models
│   │   ├── schemas/              # Pydantic request/response schemas
│   │   ├── services/             # Business logic and AI services
│   │   │   ├── llm.py            # Claude/Gemini integration
│   │   │   ├── embedding.py      # OpenAI embeddings
│   │   │   ├── processing.py     # Document pipeline
│   │   │   ├── compliance.py     # Framework management
│   │   │   └── vendor_categorization.py  # Auto-classification
│   │   └── prompts/              # AI prompt templates
│   ├── tests/                    # 129 pytest tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── pages/                # Route pages
│   │   ├── hooks/                # Custom React hooks
│   │   └── lib/                  # API client, utilities
│   └── package.json
├── docs/
│   └── PLATFORM_OVERVIEW.md      # Detailed platform documentation
├── COMPETITIVE_ANALYSIS.md       # Market positioning analysis
└── README.md
```

---

## Skills Demonstrated

| Category | Technologies & Concepts |
|----------|------------------------|
| **AI/ML Engineering** | LLM integration (Claude, Gemini), RAG architecture, prompt engineering, embeddings, vector search |
| **Backend Development** | Python 3.12, FastAPI, async/await, SQLAlchemy 2.0, Pydantic v2, REST API design |
| **Frontend Development** | React 18, TypeScript 5, TailwindCSS, Shadcn/UI, TanStack Query, Axios |
| **Database** | PostgreSQL, async operations, migrations, pgvector for embeddings |
| **Security** | JWT authentication, SAML 2.0 SSO, MFA/TOTP, RBAC, rate limiting, encryption |
| **DevOps** | Railway deployment, Netlify hosting, GitHub Actions CI/CD, Docker |
| **GRC/Compliance** | SOC 2, NIST, ISO 27001, DORA, HECVAT, SIG, third-party risk management |
| **Architecture** | Microservices, event-driven processing, caching strategies, API design |

---

## Roadmap

- [x] **v0.1.0** - Document upload, parsing, 9 frameworks, SSO/MFA
- [x] **v0.2.0** - AI Query feature, multi-LLM support, production deployment
- [x] **v0.3.0** - SIG 2026, DORA, HECVAT frameworks, basic vendor categorization
- [x] **v0.4.0** - DoorDash-style 25-category TPRM taxonomy with auto-classification
- [x] **v0.5.0** - Full CRUD operations, remediation workflows, monitoring dashboards, 90+ API endpoints
- [x] **v0.6.0** - AI Agent Network (Sentinel Prime, Vector Analyst, Watchdog Zero, Audit Core), Vendor Detail pages, JWT auth
- [x] **v0.7.0** - Risk scoring, analytics enhancements
- [x] **v0.8.0** - Document Intelligence, Multi-Framework Compliance
- [x] **v0.9.0** - NIST AI RMF, CSA CAIQ, Continuous Monitoring, Remediation Workflows
- [x] **v1.0.0** - Enterprise Security Release: SSO/SAML 2.0, MFA/TOTP, Audit Logging, Rate Limiting
- [ ] **v1.1.0** - Custom framework builder, advanced analytics
- [ ] **v1.2.0** - Jira/ServiceNow integration
- [ ] **v2.0.0** - GraphQL API, multi-tenant architecture

---

## Author

**Dominic M. Hoang**

GitHub: [@MikeDominic92](https://github.com/MikeDominic92)

Focus: Identity & Access Management, AI/ML Security, Third-Party Risk Management, Cloud Security

---

## Related Projects

| Project | Description |
|---------|-------------|
| [ai-access-sentinel](https://github.com/MikeDominic92/ai-access-sentinel) | ITDR platform with ML-powered anomaly detection and UEBA |
| [entra-id-governance](https://github.com/MikeDominic92/entra-id-governance) | Microsoft Entra ID governance toolkit with Splunk SIEM |
| [keyless-kingdom](https://github.com/MikeDominic92/keyless-kingdom) | Multi-cloud workload identity federation with zero secrets |
| [okta-sso-hub](https://github.com/MikeDominic92/okta-sso-hub) | Enterprise SSO implementation with SAML, OIDC, SCIM |

---

<p align="center">
  <strong>VendorAuditAI</strong>
  <br/>
  <sub>Securing the supply chain, one vendor at a time.</sub>
  <br/><br/>
  <a href="https://vendor-audit-ai.netlify.app">Website</a> |
  <a href="https://vendorauditai-production.up.railway.app/docs">API</a> |
  <a href="https://github.com/MikeDominic92/VendorAuditAI">GitHub</a> |
  <a href="mailto:contact@vendorauditai.com">Contact</a>
  <br/><br/>
  Proprietary - Copyright 2026 Dominic M. Hoang. All Rights Reserved.
</p>
