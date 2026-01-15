<p align="center">
  <img src="https://img.shields.io/badge/VENDORAUDITAI-000000?style=for-the-badge&logoColor=white" alt="VendorAuditAI" height="80"/>
</p>

<h1 align="center">Third Party Risk Management: Technical Problem Solving Portfolio</h1>
<h3 align="center">VendorAuditAI | Enterprise TPRM Platform | 2026</h3>
<p align="center"><em>Demonstrating how to architect AI-driven solutions for the hardest problems in vendor risk management</em></p>

<p align="center">
  <a href="https://github.com/MikeDominic92/VendorAuditAI/actions/workflows/ci.yml"><img src="https://github.com/MikeDominic92/VendorAuditAI/actions/workflows/ci.yml/badge.svg" alt="CI/CD"/></a>
  <a href="https://vendorauditai-production.up.railway.app/health"><img src="https://img.shields.io/badge/Backend-Live-00D4AA?style=flat-square" alt="Backend Status"/></a>
  <a href="https://vendor-audit-ai.netlify.app"><img src="https://img.shields.io/badge/Demo-Available-B026FF?style=flat-square" alt="Demo"/></a>
  <img src="https://img.shields.io/badge/Version-1.1.0-00D4AA.svg?style=flat-square" alt="Version"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12-3776AB.svg?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688.svg?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/React-18-61DAFB.svg?style=flat-square&logo=react&logoColor=black" alt="React"/>
  <img src="https://img.shields.io/badge/TypeScript-5.0-3178C6.svg?style=flat-square&logo=typescript&logoColor=white" alt="TypeScript"/>
  <img src="https://img.shields.io/badge/Claude-Opus_4.5-CC785C.svg?style=flat-square" alt="Claude"/>
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?style=flat-square&logo=postgresql&logoColor=white" alt="PostgreSQL"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/API_Endpoints-100+-0066FF.svg?style=flat-square" alt="API Endpoints"/>
  <img src="https://img.shields.io/badge/Tests-129_Passing-00D4AA.svg?style=flat-square" alt="Tests"/>
  <img src="https://img.shields.io/badge/Frameworks-12_Supported-FFB800.svg?style=flat-square" alt="Frameworks"/>
  <img src="https://img.shields.io/badge/AI_Agents-4_Active-CC785C.svg?style=flat-square" alt="AI Agents"/>
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

## The Six Hardest Problems in TPRM and How I Solved Them

<div align="center">

*Every challenge below represents a real problem that costs enterprises millions annually. Each solution demonstrates the architectural thinking required to solve it.*

</div>

<table>
<tr>
<td width="50%" valign="top">

### Challenge 1: Scaling Vendor Assessments

> *"How do you assess 500+ vendors annually when each SOC 2 report takes 6-8 hours?"*

**My Answer:** You don't scale humans - you scale intelligence. I built a three-stage pipeline: (1) Document intake with PDF/DOCX parsing and auto-classification, (2) AI analysis using Claude Opus 4.5 with RAG to extract controls and map to 12 frameworks simultaneously, (3) Analyst review of pre-populated findings for approval. The AI handles 90%, humans handle 10%. Result: 6-8 hours becomes 15 minutes.

```
┌────────────────────────────────────┐
│   AI-POWERED ASSESSMENT PIPELINE   │
├────────────────────────────────────┤
│                                    │
│  DOCUMENT INTAKE                   │
│  ┌──────────────────────────────┐  │
│  │ Upload SOC 2, ISO, SIG docs  │  │
│  │ PDF/DOCX parsing + OCR       │  │
│  │ Auto classification          │  │
│  └──────────────────────────────┘  │
│               │                    │
│               ▼                    │
│  AI ANALYSIS ENGINE                │
│  ┌──────────────────────────────┐  │
│  │ Claude Opus 4.5 + RAG        │  │
│  │ Extract controls/findings    │  │
│  │ Map to 12 frameworks         │  │
│  │ Generate risk scores         │  │
│  └──────────────────────────────┘  │
│               │                    │
│               ▼                    │
│  ANALYST REVIEW                    │
│  ┌──────────────────────────────┐  │
│  │ AI: 90% | Analyst: 10%       │  │
│  │ Pre-populated findings       │  │
│  │ One-click approval           │  │
│  └──────────────────────────────┘  │
│                                    │
│  6-8 hours → 15 minutes            │
└────────────────────────────────────┘
```

| Metric | Impact |
|:------:|:------:|
| Assessment time | **-97%** |
| Analyst capacity | **+900%** |
| Cost per assessment | **-87%** |

</td>
<td width="50%" valign="top">

### Challenge 2: Vendor Risk Tiering

> *"How do you categorize hundreds of vendors into meaningful risk tiers?"*

**My Answer:** Classification drives prioritization. I built a 25-category taxonomy (Cloud Infrastructure, Payment Processing, AI/ML Platforms, etc.) with AI auto-classification from vendor metadata. Each category maps to risk tiers 1-4 based on data access and business criticality. Tier 1 (critical) gets quarterly reviews; Tier 4 gets biennial. This ensures you spend time where risk lives.

```
┌────────────────────────────────────┐
│  INTELLIGENT VENDOR CLASSIFICATION │
├────────────────────────────────────┤
│                                    │
│  INPUT: Vendor name, website       │
│               │                    │
│               ▼                    │
│  AI CLASSIFICATION ENGINE          │
│  ┌──────────────────────────────┐  │
│  │ 25 Categories:               │  │
│  │ - Cloud Infrastructure       │  │
│  │ - Payment Processing         │  │
│  │ - AI/ML Platforms            │  │
│  │ - Identity & Access          │  │
│  │ - Security Tools             │  │
│  │ + 20 more                    │  │
│  └──────────────────────────────┘  │
│               │                    │
│               ▼                    │
│  RISK TIER ASSIGNMENT              │
│  ┌──────────────────────────────┐  │
│  │ Tier 1: Quarterly review     │  │
│  │ Tier 2: Semi-annual          │  │
│  │ Tier 3: Annual               │  │
│  │ Tier 4: Biennial             │  │
│  └──────────────────────────────┘  │
│                                    │
└────────────────────────────────────┘
```

**Implementation:**
- Auto-Classification by AI
- Data Access Level tracking
- Assessment Scheduling
- Override Controls with audit

</td>
</tr>
</table>

<table>
<tr>
<td width="50%" valign="top">

### Challenge 3: AI/ML Vendor Risk

> *"How do you assess AI vendors when traditional frameworks don't cover autonomous systems?"*

**My Answer:** Traditional frameworks weren't built for AI. I created a dedicated AI Tool Classification module implementing NIST AI RMF (70+ controls) plus custom risk factors: Stack Type (Foundation Model, GenAI App, Autonomous Agent), Data Training practices (does your data train their models?), and Autonomous Action scope (read-only vs. fully autonomous). These are the questions SOC 2 doesn't ask.

```
┌────────────────────────────────────┐
│    AI VENDOR RISK CLASSIFICATION   │
├────────────────────────────────────┤
│                                    │
│  STACK TYPE CLASSIFICATION         │
│  ┌──────────────────────────────┐  │
│  │ - Foundation Model (HIGH)    │  │
│  │ - GenAI Application          │  │
│  │ - Autonomous Agent (HIGH)    │  │
│  │ - Fine-Tuning Platform       │  │
│  │ - Embedding Service          │  │
│  │ - MLOps Platform             │  │
│  └──────────────────────────────┘  │
│                                    │
│  AI-SPECIFIC RISK FACTORS          │
│  ┌──────────────────────────────┐  │
│  │ Data Training:               │  │
│  │ □ No customer data           │  │
│  │ □ Opt-in only                │  │
│  │ □ All data (HIGH RISK)       │  │
│  │                              │  │
│  │ Autonomous Actions:          │  │
│  │ □ Read-only                  │  │
│  │ □ Human approval             │  │
│  │ □ Fully autonomous (HIGH)    │  │
│  └──────────────────────────────┘  │
│                                    │
│  NIST AI RMF + Custom Controls     │
└────────────────────────────────────┘
```

**Implementation:**
- AI Tool Classification module
- NIST AI RMF (70+ controls)
- AI Governance Playbooks
- Approved AI Registry

</td>
<td width="50%" valign="top">

### Challenge 4: Continuous Monitoring

> *"A SOC 2 report is a snapshot. How do you know if security has degraded?"*

**My Answer:** Point-in-time assessments create blind spots. I deployed four autonomous AI agents that run 24/7: Sentinel Prime (threat detection), Vector Analyst (risk scoring), Watchdog Zero (vulnerability scanning), and Audit Core (compliance verification). When they find issues, they push alerts to your existing tools - Jira, ServiceNow, Slack. No new dashboards to watch.

```
┌────────────────────────────────────┐
│    AI AGENT MONITORING NETWORK     │
├────────────────────────────────────┤
│                                    │
│  ┌────────┐ ┌────────┐ ┌────────┐  │
│  │SENTINEL│ │ VECTOR │ │WATCHDOG│  │
│  │ PRIME  │ │ANALYST │ │  ZERO  │  │
│  │        │ │        │ │        │  │
│  │ Threat │ │  Risk  │ │  Vuln  │  │
│  │ Detect │ │ Score  │ │  Scan  │  │
│  └───┬────┘ └───┬────┘ └───┬────┘  │
│      │          │          │       │
│      └──────────┼──────────┘       │
│                 │                  │
│                 ▼                  │
│  ┌──────────────────────────────┐  │
│  │         AUDIT CORE           │  │
│  │                              │  │
│  │ - Framework coverage         │  │
│  │ - Control monitoring         │  │
│  │ - Cert expiration alerts     │  │
│  └──────────────────────────────┘  │
│                 │                  │
│                 ▼                  │
│  ┌──────────────────────────────┐  │
│  │    ALERT & REMEDIATION       │  │
│  │ Jira | ServiceNow | Slack    │  │
│  └──────────────────────────────┘  │
│                                    │
└────────────────────────────────────┘
```

**Implementation:**
- 4 Autonomous AI Agents
- Scheduled Assessments
- Integration Hub
- Custom Alert Rules

</td>
</tr>
</table>

<table>
<tr>
<td width="50%" valign="top">

### Challenge 5: BPO and Fourth-Party Risk

> *"Your vendor outsources to another vendor. How do you assess that layered risk?"*

**My Answer:** Fourth-party risk is where breaches hide. The BPO Module I built tracks three layers: Provider profiles (who they are, contract terms, subcontractor disclosure), Process-specific risks (is this Tier 1 financial processing or Tier 3 data entry?), and Geographic risks (GDPR compliance, data residency, political stability). You can't manage what you can't see.

```
┌────────────────────────────────────┐
│      BPO RISK MANAGEMENT           │
├────────────────────────────────────┤
│                                    │
│  PROVIDER TRACKING                 │
│  ┌──────────────────────────────┐  │
│  │ Company profile + locations  │  │
│  │ Contract terms + SLAs        │  │
│  │ Data access levels           │  │
│  │ Subcontractor disclosure     │  │
│  └──────────────────────────────┘  │
│               │                    │
│               ▼                    │
│  PROCESS-SPECIFIC RISK             │
│  ┌──────────────────────────────┐  │
│  │ Customer Support (Tier 2)    │  │
│  │ Data Entry (Tier 3)          │  │
│  │ Financial Processing (T1)    │  │
│  │ IT Support (Tier 2)          │  │
│  └──────────────────────────────┘  │
│               │                    │
│               ▼                    │
│  GEOGRAPHIC RISK                   │
│  ┌──────────────────────────────┐  │
│  │ Data residency (GDPR/CCPA)   │  │
│  │ Political stability          │  │
│  │ Regulatory jurisdiction      │  │
│  │ Business continuity          │  │
│  └──────────────────────────────┘  │
│                                    │
└────────────────────────────────────┘
```

**Implementation:**
- BPO Module for outsourcing
- Process-level risk scoring
- Geographic compliance mapping
- Fourth-party visibility

</td>
<td width="50%" valign="top">

### Challenge 6: Executive Reporting

> *"How do you show the board that TPRM prevents breaches, not just generates paperwork?"*

**My Answer:** Boards don't care about controls - they care about risk posture and ROI. The Executive Dashboard translates security work into business metrics: Overall risk score with 90-day trends, cost savings from automation ($380K+ annually), compliance percentages by framework, and remediation SLA compliance. All exportable to PDF/CSV. Security teams speak risk; boards speak money.

```
┌────────────────────────────────────┐
│   EXECUTIVE DASHBOARD METRICS      │
├────────────────────────────────────┤
│                                    │
│  RISK POSTURE                      │
│  ┌──────────────────────────────┐  │
│  │ Score: 72/100 (Moderate)     │  │
│  │ Trend: +8 pts (90 days)      │  │
│  │ Critical: 3 | High: 12       │  │
│  │ Medium: 45 | Low: 140        │  │
│  └──────────────────────────────┘  │
│               │                    │
│               ▼                    │
│  OPERATIONAL EFFICIENCY            │
│  ┌──────────────────────────────┐  │
│  │ Assessments: 127 (YTD)       │  │
│  │ Avg Time: 18 min vs 6 hrs    │  │
│  │ Cost Savings: $380K          │  │
│  │ Frameworks: 12 (2500+ ctrl)  │  │
│  └──────────────────────────────┘  │
│               │                    │
│               ▼                    │
│  COMPLIANCE & REMEDIATION          │
│  ┌──────────────────────────────┐  │
│  │ SOC 2: 94% compliant         │  │
│  │ ISO 27001: 67% certified     │  │
│  │ Open Findings: 47            │  │
│  │ SLA Compliance: 89%          │  │
│  └──────────────────────────────┘  │
│                                    │
└────────────────────────────────────┘
```

**Implementation:**
- Executive Dashboard
- Trend Analysis
- PDF/CSV Reports
- Complete Audit Trail

</td>
</tr>
</table>

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

## Quick Start

### Prerequisites

- Python 3.12+ | Node.js 18+ | PostgreSQL 16+
- API Keys: Anthropic (Claude), OpenAI (embeddings)

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

---

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
