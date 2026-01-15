<h1 align="center">VendorAuditAI</h1>
<h3 align="center">Enterprise TPRM AI Platform | 2026</h3>
<p align="center"><em>Demonstrating how to architect AI-driven solutions for the hardest problems in vendor risk management</em></p>

<p align="center">
  <a href="https://vendor-audit-ai.netlify.app"><img src="https://img.shields.io/badge/Live_Demo-Available-B026FF?style=flat-square" alt="Demo"/></a>
  <img src="https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB.svg?style=flat-square&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/Claude_Opus_4.5-CC785C.svg?style=flat-square" alt="Claude"/>
  <img src="https://img.shields.io/badge/12_Frameworks-FFB800.svg?style=flat-square" alt="Frameworks"/>
  <img src="https://img.shields.io/badge/4_AI_Agents-CC785C.svg?style=flat-square" alt="AI Agents"/>
</p>

<p align="center">
  <strong>Transform vendor security assessments from 8 hours to 15 minutes using AI-powered document analysis, multi-framework compliance mapping, and autonomous agent monitoring</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> |
  <a href="#key-features">Features</a> |
  <a href="#platform-modules">Modules</a> |
  <a href="#ai-agent-network">AI Agents</a> |
  <a href="#compliance-frameworks">Compliance</a> |
  <a href="#architecture">Architecture</a> |
  <a href="#api-reference">API</a> |
  <a href="#quick-start">Quick Start</a>
</p>

---

<div align="center">

### Live Demo

| | |
|:--|:--|
| **URL** | [vendor-audit-ai.netlify.app](https://vendor-audit-ai.netlify.app) |
| **Email** | `newdemo@vendorauditai.com` |
| **Password** | `Demo12345` |

</div>

---

## Overview

<div align="center">

### The Problem

| Challenge | Impact |
|:---------:|:------:|
| **60% of data breaches** originate from third-party vendors | Ponemon Institute |
| **$4.88M average cost** per data breach in 2024 | IBM Security |
| **6-8 hours per vendor** to manually review SOC 2 reports | Industry average |
| **200+ page documents** with critical risks buried in text | Analyst fatigue |

### The Solution

| Capability | Result |
|:----------:|:------:|
| **AI Document Analysis** | 15-minute assessments vs 8 hours |
| **Multi-Framework Mapping** | One document mapped to 12 frameworks |
| **Autonomous Agents** | 24/7 threat detection and monitoring |
| **Natural Language Q&A** | Ask questions, get cited answers |

</div>

---

<h2 align="center">Technical Problem Solving</h2>

<p align="center"><em>Real enterprise TPRM challenges and the architectural solutions I built to solve them.</em></p>

<div align="center">

<h3>Challenge 1: Scaling Vendor Assessments</h3>

> *"How do you assess 500+ vendors annually when each SOC 2 report takes 6-8 hours?"*

**My Answer:** You don't scale humans. You scale intelligence.

- **Stage 1: Document Intake** - PDF/DOCX parsing with OCR and auto-classification
- **Stage 2: AI Analysis** - Claude Opus 4.5 with RAG extracts controls, maps to 12 frameworks simultaneously
- **Stage 3: Analyst Review** - Pre-populated findings, one-click approval
- **Result:** AI handles 90%, humans handle 10%. 6-8 hours becomes 15 minutes.

**Solution Architecture:**

```
+------------------------------------------------------------------------+
|                    AI-POWERED ASSESSMENT PIPELINE                       |
+------------------------------------------------------------------------+
|                                                                        |
|   DOCUMENT INTAKE                                                      |
|   +------------------------------------------------------------------+ |
|   |  Upload SOC 2, ISO 27001, SIG, questionnaires                    | |
|   |  - PDF/DOCX parsing with OCR for scanned docs                    | |
|   |  - Automatic document type classification                        | |
|   |  - Semantic chunking for optimal AI processing                   | |
|   +------------------------------------------------------------------+ |
|                                    |                                   |
|                                    v                                   |
|   AI ANALYSIS ENGINE                                                   |
|   +------------------------------------------------------------------+ |
|   |  Claude Opus 4.5 + RAG Architecture                              | |
|   |  - Extract controls, findings, exceptions                        | |
|   |  - Map to 12 compliance frameworks simultaneously                | |
|   |  - Generate risk scores with confidence levels                   | |
|   +------------------------------------------------------------------+ |
|                                    |                                   |
|                                    v                                   |
|   ANALYST REVIEW                                                       |
|   +------------------------------------------------------------------+ |
|   |  AI does 90% of work, analyst validates 10%                      | |
|   |  - Pre-populated findings with citations                         | |
|   |  - One-click approval or adjustment                              | |
|   +------------------------------------------------------------------+ |
|                                                                        |
|   RESULT: 6-8 hours --> 15 minutes per assessment                      |
|                                                                        |
+------------------------------------------------------------------------+
```

| Metric | Impact |
|:------:|:------:|
| Assessment time | **-97%** |
| Analyst capacity | **+900%** |
| Cost per assessment | **-87%** |

</div>

---

<div align="center">

<h3>Challenge 2: Vendor Risk Tiering</h3>

> *"How do you categorize hundreds of vendors into meaningful risk tiers?"*

**My Answer:** Classification drives prioritization.

- **25-Category Taxonomy** - Cloud Infrastructure, Payment Processing, AI/ML Platforms, Identity & Access, etc.
- **AI Auto-Classification** - Vendor name and website analyzed to assign category
- **Risk Tier Mapping** - Categories map to Tiers 1-4 based on data access and business criticality
- **Assessment Frequency** - Tier 1 quarterly, Tier 2 semi-annual, Tier 3 annual, Tier 4 biennial
- **Result:** You spend time where risk actually lives.

**Solution Architecture:**

```
+------------------------------------------------------------------------+
|                   INTELLIGENT VENDOR CLASSIFICATION                     |
+------------------------------------------------------------------------+
|                                                                        |
|   INPUT: Vendor name, website, business description                    |
|                                    |                                   |
|                                    v                                   |
|   AI CLASSIFICATION ENGINE                                             |
|   +------------------------------------------------------------------+ |
|   |  25 Enterprise Categories:                                       | |
|   |  - Cloud Infrastructure (AWS, Azure, GCP)                        | |
|   |  - Payment Processing (Stripe, Square, Adyen)                    | |
|   |  - AI/ML Platforms (OpenAI, Anthropic, Cohere)                   | |
|   |  - Identity & Access (Okta, Auth0, Ping)                         | |
|   |  - Security Tools (CrowdStrike, Splunk, Palo Alto)               | |
|   |  - Data Analytics, HR Systems, CRM, ERP, + 16 more               | |
|   +------------------------------------------------------------------+ |
|                                    |                                   |
|                                    v                                   |
|   RISK TIER ASSIGNMENT (Based on data access + business criticality)  |
|   +------------------------------------------------------------------+ |
|   |  Tier 1 (Critical)  : Quarterly review   | Payment, Cloud, IAM   | |
|   |  Tier 2 (High)      : Semi-annual review | Security, Analytics   | |
|   |  Tier 3 (Medium)    : Annual review      | HR, CRM, Collaboration| |
|   |  Tier 4 (Low)       : Biennial review    | Marketing, Office     | |
|   +------------------------------------------------------------------+ |
|                                                                        |
|   RESULT: Right-sized assessment frequency based on actual risk        |
|                                                                        |
+------------------------------------------------------------------------+
```

</div>

---

<div align="center">

<h3>Challenge 3: AI/ML Vendor Risk</h3>

> *"How do you assess AI vendors when traditional frameworks don't cover autonomous systems?"*

**My Answer:** Traditional frameworks weren't built for AI.

- **AI Tool Classification Module** - Dedicated assessment for AI/ML vendors
- **NIST AI RMF** - 70+ controls specifically for AI governance
- **Stack Type Classification** - Foundation Model, GenAI App, Autonomous Agent, Fine-Tuning Platform
- **Data Training Risk** - Does your data train their models? Opt-in only or all data?
- **Autonomous Action Scope** - Read-only, human approval required, or fully autonomous?
- **Result:** These are the questions SOC 2 doesn't ask.

**Solution Architecture:**

```
+------------------------------------------------------------------------+
|                     AI VENDOR RISK CLASSIFICATION                       |
+------------------------------------------------------------------------+
|                                                                        |
|   STACK TYPE CLASSIFICATION (What kind of AI is this?)                 |
|   +------------------------------------------------------------------+ |
|   |  - Foundation Model Provider (HIGH RISK)    | OpenAI, Anthropic  | |
|   |  - GenAI Application                        | ChatGPT, Claude    | |
|   |  - Autonomous Agent (HIGH RISK)             | AutoGPT, AgentGPT  | |
|   |  - Fine-Tuning Platform                     | Replicate, Modal   | |
|   |  - Embedding/Vector Service                 | Pinecone, Weaviate | |
|   |  - MLOps Platform                           | Weights & Biases   | |
|   +------------------------------------------------------------------+ |
|                                                                        |
|   DATA TRAINING PRACTICES (Does your data train their models?)         |
|   +------------------------------------------------------------------+ |
|   |  [ ] No customer data used for training           (LOW RISK)     | |
|   |  [ ] Opt-in only with explicit consent            (MEDIUM RISK)  | |
|   |  [ ] All data used by default                     (HIGH RISK)    | |
|   +------------------------------------------------------------------+ |
|                                                                        |
|   AUTONOMOUS ACTION SCOPE (What can the AI do without human approval?) |
|   +------------------------------------------------------------------+ |
|   |  [ ] Read-only / Analysis only                    (LOW RISK)     | |
|   |  [ ] Actions require human approval               (MEDIUM RISK)  | |
|   |  [ ] Fully autonomous execution                   (HIGH RISK)    | |
|   +------------------------------------------------------------------+ |
|                                                                        |
|   FRAMEWORK: NIST AI RMF (70+ controls) + Custom AI Governance         |
|                                                                        |
+------------------------------------------------------------------------+
```

</div>

---

<div align="center">

<h3>Challenge 4: Continuous Monitoring</h3>

> *"A SOC 2 report is a snapshot. How do you know if security has degraded?"*

**My Answer:** Point-in-time assessments create blind spots.

- **Sentinel Prime** - Threat detection, scans for security risks and anomalies
- **Vector Analyst** - Risk scoring based on findings, compliance, and history
- **Watchdog Zero** - Vulnerability scanning, identifies gaps and expired certs
- **Audit Core** - Compliance verification, maps documents to frameworks
- **Integration** - Alerts push to Jira, ServiceNow, Slack automatically
- **Result:** 24/7 coverage. No new dashboards to watch.

**Solution Architecture:**

```
+------------------------------------------------------------------------+
|                      AI AGENT MONITORING NETWORK                        |
+------------------------------------------------------------------------+
|                                                                        |
|   +------------------+  +------------------+  +------------------+      |
|   |  SENTINEL PRIME  |  |  VECTOR ANALYST  |  |  WATCHDOG ZERO   |      |
|   +------------------+  +------------------+  +------------------+      |
|   |                  |  |                  |  |                  |      |
|   | Threat Detection |  | Risk Scoring     |  | Vuln Scanning    |      |
|   | - Security risks |  | - Score findings |  | - Security gaps  |      |
|   | - Anomaly detect |  | - History trends |  | - Expired certs  |      |
|   | - Emerging CVEs  |  | - Confidence lvl |  | - Missing ctrl   |      |
|   |                  |  |                  |  |                  |      |
|   +--------+---------+  +--------+---------+  +--------+---------+      |
|            |                     |                     |               |
|            +---------------------+---------------------+               |
|                                  |                                     |
|                                  v                                     |
|   +------------------------------------------------------------------+ |
|   |                         AUDIT CORE                               | |
|   +------------------------------------------------------------------+ |
|   |  - Framework coverage analysis (12 frameworks, 2500+ controls)   | |
|   |  - Continuous control monitoring and drift detection             | |
|   |  - Certificate expiration tracking and alerts                    | |
|   |  - Compliance score calculation and trending                     | |
|   +------------------------------------------------------------------+ |
|                                  |                                     |
|                                  v                                     |
|   +------------------------------------------------------------------+ |
|   |                    ALERT & REMEDIATION                           | |
|   +------------------------------------------------------------------+ |
|   |  Jira         |  ServiceNow    |  Slack        |  Email          | |
|   |  Auto-create  |  Incident mgmt |  Real-time    |  Digest         | |
|   |  tickets      |  integration   |  alerts       |  reports        | |
|   +------------------------------------------------------------------+ |
|                                                                        |
+------------------------------------------------------------------------+
```

</div>

---

<div align="center">

<h3>Challenge 5: BPO and Fourth-Party Risk</h3>

> *"Your vendor outsources to another vendor. How do you assess that layered risk?"*

**My Answer:** Fourth-party risk is where breaches hide.

- **Provider Profiles** - Company info, contract terms, SLAs, subcontractor disclosure
- **Process-Specific Risk** - Is this Tier 1 financial processing or Tier 3 data entry?
- **Geographic Risk** - GDPR compliance, data residency, political stability, business continuity
- **Visibility** - Track the full chain: Your company > Vendor > Their subcontractor
- **Result:** You can't manage what you can't see.

**Solution Architecture:**

```
+------------------------------------------------------------------------+
|                       BPO RISK MANAGEMENT                               |
+------------------------------------------------------------------------+
|                                                                        |
|   YOUR COMPANY -----> PRIMARY VENDOR -----> BPO PROVIDER (4th Party)   |
|                                                                        |
+------------------------------------------------------------------------+
|                                                                        |
|   LAYER 1: PROVIDER TRACKING                                           |
|   +------------------------------------------------------------------+ |
|   |  Company Profile       | Legal name, HQ location, office sites   | |
|   |  Contract Terms        | SLAs, liability caps, termination       | |
|   |  Data Access Levels    | What data do they touch? PII? Financial?| |
|   |  Subcontractor Disclosure | Who do THEY outsource to?            | |
|   +------------------------------------------------------------------+ |
|                                    |                                   |
|                                    v                                   |
|   LAYER 2: PROCESS-SPECIFIC RISK                                       |
|   +------------------------------------------------------------------+ |
|   |  Financial Processing  (Tier 1)  | Payments, accounting, audit   | |
|   |  Customer Support      (Tier 2)  | Help desk, chat, phone        | |
|   |  IT Support            (Tier 2)  | Infrastructure, dev, ops      | |
|   |  Data Entry            (Tier 3)  | Document processing, input    | |
|   +------------------------------------------------------------------+ |
|                                    |                                   |
|                                    v                                   |
|   LAYER 3: GEOGRAPHIC RISK                                             |
|   +------------------------------------------------------------------+ |
|   |  Data Residency        | GDPR (EU), CCPA (CA), PDPA (SG), etc.   | |
|   |  Political Stability   | Country risk scores, sanctions          | |
|   |  Regulatory Jurisdiction| Which laws apply? Cross-border transfer | |
|   |  Business Continuity   | Natural disasters, infrastructure       | |
|   +------------------------------------------------------------------+ |
|                                                                        |
|   RESULT: Full visibility into fourth-party risk chain                 |
|                                                                        |
+------------------------------------------------------------------------+
```

</div>

---

<div align="center">

<h3>Challenge 6: Executive Reporting</h3>

> *"How do you show the board that TPRM prevents breaches, not just generates paperwork?"*

**My Answer:** Boards don't care about controls. They care about risk posture and ROI.

- **Risk Posture Score** - Overall score with 90-day trend analysis
- **Cost Savings** - $380K+ annually from automation vs. manual assessments
- **Compliance Percentages** - By framework (SOC 2: 94%, ISO 27001: 67%, etc.)
- **Remediation SLAs** - Track whether findings get fixed on time
- **Export** - PDF/CSV for board presentations
- **Result:** Security teams speak risk. Boards speak money. This translates.

**Solution Architecture:**

```
+------------------------------------------------------------------------+
|                     EXECUTIVE DASHBOARD METRICS                         |
+------------------------------------------------------------------------+
|                                                                        |
|   RISK POSTURE (Board-Level Summary)                                   |
|   +------------------------------------------------------------------+ |
|   |  Overall Risk Score:  72/100 (Moderate)                          | |
|   |  90-Day Trend:        +8 points (Improving)                      | |
|   |                                                                  | |
|   |  Risk Distribution:                                              | |
|   |  Critical: 3  |  High: 12  |  Medium: 45  |  Low: 140           | |
|   +------------------------------------------------------------------+ |
|                                    |                                   |
|                                    v                                   |
|   OPERATIONAL EFFICIENCY (ROI Metrics)                                 |
|   +------------------------------------------------------------------+ |
|   |  Assessments Completed (YTD):     127 vendors                    | |
|   |  Average Assessment Time:         18 minutes (was 6 hours)       | |
|   |  Annual Cost Savings:             $380,000+                      | |
|   |  Framework Coverage:              12 frameworks, 2500+ controls  | |
|   +------------------------------------------------------------------+ |
|                                    |                                   |
|                                    v                                   |
|   COMPLIANCE & REMEDIATION STATUS                                      |
|   +------------------------------------------------------------------+ |
|   |  SOC 2 Type II:      94% of vendors compliant                    | |
|   |  ISO 27001:          67% of vendors certified                    | |
|   |  Open Findings:      47 (down from 89 last quarter)              | |
|   |  Remediation SLA:    89% on-time completion                      | |
|   +------------------------------------------------------------------+ |
|                                                                        |
|   EXPORT: PDF Report | CSV Data | Board Presentation Deck              |
|                                                                        |
+------------------------------------------------------------------------+
```

</div>

<div align="center">

### Architecture Decisions Summary

| Problem | My Solution | Why It Works |
|:-------:|:-----------:|:------------:|
| Scale assessments | 3-stage AI pipeline | 90% automation, 10% human review |
| Categorize vendors | 25-category taxonomy | Risk-based assessment frequency |
| Assess AI vendors | NIST AI RMF + custom controls | Covers what SOC 2 misses |
| Continuous monitoring | 4 autonomous agents | 24/7 coverage, existing tool integration |
| Fourth-party risk | 3-layer BPO tracking | Visibility into hidden risk |
| Executive reporting | Business metrics dashboard | Risk posture + ROI in board language |

</div>

---

## Key Features

<div align="center">

### Core Capabilities

| Feature | Description |
|:-------:|:-----------:|
| **Document Intelligence** | Upload PDF/DOCX, AI extracts and analyzes content with semantic chunking |
| **Natural Language Query** | Ask questions about vendor documents, get cited answers with page references |
| **Multi-Framework Compliance** | Map documents to SOC 2, NIST, ISO 27001, DORA, SIG, and 7 more frameworks |
| **AI Agent Network** | 4 autonomous agents for threat detection, risk scoring, and vulnerability scanning |
| **Vendor Management** | Full CRUD with 25-category enterprise taxonomy and auto-classification |
| **Risk Analytics** | Real-time dashboards with risk scoring and trend analysis |
| **Remediation Workflow** | Task management with SLA tracking and external system sync |
| **Continuous Monitoring** | Scheduled assessments, alerts, and notification channels |

### Enterprise Security

| Feature | Implementation |
|:-------:|:--------------:|
| **Authentication** | JWT tokens, refresh tokens, session management |
| **SSO/SAML 2.0** | Azure AD, Google, Okta, OneLogin support |
| **MFA/TOTP** | Time-based one-time passwords with QR provisioning |
| **Audit Logging** | Complete trail of user actions and system events |
| **Rate Limiting** | Configurable per-endpoint protection |
| **Encryption** | AES-256 at rest, TLS 1.3 in transit |

</div>

---

## Platform Modules

<div align="center">

| # | Module | Description |
|:-:|:------:|:-----------:|
| 1 | **Executive Dashboard** | Real-time vendor risk posture with animated metrics |
| 2 | **AI Governance Playbooks** | Guided workflows for AI tool adoption |
| 3 | **Approved AI Registry** | Self-service registry for pre-approved AI tools |
| 4 | **BPO Risk Management** | Business Process Outsourcing risk tracking |
| 5 | **Integration Hub** | Jira, ServiceNow, Slack, Email, Webhooks |
| 6 | **Vendor Management** | 25-category taxonomy with risk tiering |
| 7 | **Document Management** | PDF/DOCX upload with semantic chunking |
| 8 | **Compliance Analysis** | AI-powered multi-framework mapping |
| 9 | **Remediation Workflow** | Task management with SLA tracking |
| 10 | **Continuous Monitoring** | Scheduled assessments and alerts |
| 11 | **AI Tool Classification** | Stack type and risk factor assessment |
| 12 | **Risk Analytics** | Trends, comparisons, exportable reports |

</div>

---

## AI Agent Network

<div align="center">

Four autonomous AI agents continuously monitor your vendor ecosystem.

| Agent | Role | Capabilities |
|:-----:|:----:|:------------:|
| **Sentinel Prime** | Threat Detection | Scans documents for security risks, anomalies, and emerging threats |
| **Vector Analyst** | Risk Assessment | Calculates risk scores based on findings, compliance, and history |
| **Watchdog Zero** | Vulnerability Scanner | Identifies security gaps, missing controls, expired certifications |
| **Audit Core** | Compliance Verification | Maps documents to frameworks, calculates compliance coverage |

**Agent Features:** Autonomous Execution | Task Queue | Activity Logs | Status Dashboard

</div>

---

## Compliance Frameworks

<div align="center">

VendorAuditAI supports **12 compliance frameworks** with **2500+ controls**.

| Framework | Controls | Version | Best For |
|:---------:|:--------:|:-------:|:--------:|
| **SOC 2 TSC** | 64 | 2017 | SaaS vendors, cloud services |
| **SIG 2026** | 800+ | 2026 | Industry gold standard |
| **NIST CSF** | 108 | 2.0 | Critical infrastructure |
| **ISO 27001** | 114 | 2022 | International compliance |
| **CIS Controls** | 153 | 8.0 | Security baselines |
| **DORA** | 100+ | 2025 | EU financial entities |
| **HECVAT** | 200+ | 3.06 | Higher education |
| **CAIQ** | 260+ | 4.0 | Cloud security (CSA STAR) |
| **NIST AI RMF** | 70+ | 1.0 | AI/ML vendors |
| **AI Risk** | 50+ | 1.0 | AI vendor assessment |
| **PCI-DSS** | 300+ | 4.0 | Payment processing |
| **HIPAA** | 150+ | 2013 | Healthcare vendors |

</div>

---

<div align="center">

## Architecture

```
+-----------------------------------------------------------------------------+
|                           VENDORAUDITAI ARCHITECTURE                         |
+-----------------------------------------------------------------------------+

                              +------------------+
                              |   USER/BROWSER   |
                              +--------+---------+
                                       |
                                       v
+-----------------------------------------------------------------------------+
|                              FRONTEND (Netlify)                              |
|  +-------------+  +-------------+  +-------------+  +-------------+         |
|  |   React 18  |  | TypeScript  |  | TailwindCSS |  |  Shadcn/UI  |         |
|  +-------------+  +-------------+  +-------------+  +-------------+         |
+----------------------------------+------+------------------------------------+
                                   | HTTPS/REST API
                                   v
+-----------------------------------------------------------------------------+
|                              BACKEND (Railway)                               |
|  +-------------+  +-------------+  +-------------+  +-------------+         |
|  |   FastAPI   |  | SQLAlchemy  |  |    Async    |  |  Pydantic   |         |
|  |  Python 3.12|  |     2.0     |  |   Workers   |  |  Schemas    |         |
|  +-------------+  +-------------+  +-------------+  +-------------+         |
+----------+------------------+------------------+----------------------------+
           |                  |                  |
           v                  v                  v
+------------------+ +------------------+ +----------------------------------+
|   PostgreSQL     | |   Redis Cache    | |         AI SERVICES              |
|   +----------+   | |   +----------+   | |  +------------+ +------------+   |
|   | Documents|   | |   | Sessions |   | |  |Claude Opus | |  OpenAI    |   |
|   | Chunks   |   | |   | Rate Lim |   | |  |   4.5      | | Embeddings |   |
|   | Findings |   | |   +----------+   | |  +------------+ +------------+   |
|   | Vendors  |   | +------------------+ |  +------------+                   |
|   +----------+   |                      |  |  Gemini    |                   |
+------------------+                      |  |    3.0     |                   |
                                          |  +------------+                   |
                                          +----------------------------------+

+-----------------------------------------------------------------------------+
|                       DOCUMENT PROCESSING PIPELINE                           |
|                                                                              |
|   UPLOAD --> PARSE --> CHUNK --> EMBED --> INDEX --> READY FOR QUERY        |
|     |          |         |         |         |            |                  |
|   PDF/DOCX   Extract   Semantic  Vector   PostgreSQL   Natural Language     |
|   Validation  Text     Splitting  Store   + pgvector   Q&A with Citations   |
+-----------------------------------------------------------------------------+
```

</div>

---

## API Reference

<div align="center">

**100+ REST API Endpoints** | [Swagger UI](https://vendorauditai-production.up.railway.app/docs) | [ReDoc](https://vendorauditai-production.up.railway.app/redoc)

| Category | Endpoints | Description |
|:--------:|:---------:|:-----------:|
| **Auth** | 5 | Login, register, refresh, MFA enable/verify |
| **Vendors** | 5 | CRUD operations for vendor management |
| **Documents** | 4 | Upload, list, get, delete documents |
| **Analysis** | 3 | Run AI analysis, list/get findings |
| **Query** | 2 | Natural language Q&A, history |
| **Agents** | 4 | List agents, get details, create tasks, view logs |
| **Playbooks** | 4 | List, get, start, complete step |
| **Approved Vendors** | 7 | Registry, deploy, request, stats |
| **BPO** | 5 | Providers, processes, assessments, dashboard |
| **Integrations** | 5 | CRUD, test connection, sync, logs |
| **Compliance** | 3 | List frameworks, details, search controls |
| **Remediation** | 4 | Tasks CRUD, external sync |
| **Monitoring** | 3 | Alerts, schedules management |

</div>

---

<div align="center">

## Quick Start

### Prerequisites

Python 3.12+ | Node.js 18+ | PostgreSQL 16+

API Keys: Anthropic (Claude), OpenAI (embeddings)

### Installation

```bash
# Clone repository
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

# Run migrations
alembic upgrade head

# Start backend
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

# LLM Provider
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-...

# Embeddings
OPENAI_API_KEY=sk-...
```

</div>

---

<div align="center">

## Project Structure

```
VendorAuditAI/
|-- backend/
|   |-- app/
|   |   |-- api/v1/endpoints/     # REST API endpoints (100+)
|   |   |-- data/frameworks/      # 12 compliance framework definitions
|   |   |-- models/               # SQLAlchemy ORM models
|   |   |-- schemas/              # Pydantic request/response schemas
|   |   |-- services/             # Business logic and AI services
|   |   `-- prompts/              # AI prompt templates
|   |-- alembic/versions/         # Database migrations
|   |-- tests/                    # 129 pytest tests
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- components/           # React components
|   |   |-- pages/                # Route pages (12 modules)
|   |   |-- hooks/                # Custom React hooks
|   |   |-- stores/               # State management
|   |   `-- lib/                  # API client, utilities
|   `-- package.json
`-- README.md
```

</div>

---

## Roadmap

<div align="center">

### Completed

| Version | Features |
|:-------:|:--------:|
| v0.1 - v0.5 | Document upload, 9 frameworks, SSO/MFA, AI Query, CRUD, remediation |
| v0.6 - v0.9 | AI Agent Network, risk scoring, NIST AI RMF, continuous monitoring |
| v1.0 | Enterprise Security: SSO/SAML 2.0, MFA/TOTP, Audit Logging |
| v1.1 | AI Governance Playbooks, Approved AI Registry, BPO, Integration Hub |

### Upcoming

| Version | Features |
|:-------:|:--------:|
| v1.2 | Custom framework builder, advanced analytics |
| v1.3 | Mobile responsive design, dark mode improvements |
| v2.0 | GraphQL API, multi-tenant architecture |

</div>

---

## Technology Stack

<div align="center">

| Category | Technologies |
|:--------:|:------------:|
| **AI/ML** | Claude Opus 4.5, Gemini 3.0, OpenAI Embeddings, RAG |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2 |
| **Frontend** | React 18, TypeScript 5, TailwindCSS, Shadcn/UI |
| **Database** | PostgreSQL 16, pgvector, Alembic |
| **Security** | JWT, SAML 2.0 SSO, MFA/TOTP, AES-256, TLS 1.3 |
| **Infrastructure** | Railway, Netlify, GitHub Actions CI/CD |

</div>

---

## Author

<div align="center">

**Dominic M. Hoang**

GitHub: [@MikeDominic92](https://github.com/MikeDominic92)

</div>

---

## Related Projects

<div align="center">

| Project | Description |
|:-------:|:-----------:|
| [ai-access-sentinel](https://github.com/MikeDominic92/ai-access-sentinel) | ITDR platform with ML-powered anomaly detection |
| [entra-id-governance](https://github.com/MikeDominic92/entra-id-governance) | Microsoft Entra ID governance toolkit |
| [keyless-kingdom](https://github.com/MikeDominic92/keyless-kingdom) | Multi-cloud workload identity federation |
| [okta-sso-hub](https://github.com/MikeDominic92/okta-sso-hub) | Enterprise SSO with SAML, OIDC, SCIM |

</div>

---

<p align="center">
  <strong>VendorAuditAI</strong>
  <br/>
  <sub>Securing the supply chain, one vendor at a time.</sub>
  <br/><br/>
  <a href="https://vendor-audit-ai.netlify.app">Website</a> |
  <a href="https://vendorauditai-production.up.railway.app/docs">API</a> |
  <a href="https://github.com/MikeDominic92/VendorAuditAI">GitHub</a>
  <br/><br/>
  Proprietary - Copyright 2026 Dominic M. Hoang. All Rights Reserved.
</p>
