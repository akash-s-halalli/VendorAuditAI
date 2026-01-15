<p align="center">
  <img src="https://img.shields.io/badge/VENDORAUDITAI-000000?style=for-the-badge&logoColor=white" alt="VendorAuditAI" height="80"/>
</p>

<h1 align="center">VendorAuditAI</h1>

<h3 align="center">Enterprise AI-Powered Third-Party Risk Management Platform</h3>

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

---

## Live Demo

| | |
|:--|:--|
| **URL** | [vendor-audit-ai.netlify.app](https://vendor-audit-ai.netlify.app) |
| **Email** | `newdemo@vendorauditai.com` |
| **Password** | `Demo12345` |

---

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Platform Modules](#platform-modules)
4. [AI Agent Network](#ai-agent-network)
5. [Compliance Frameworks](#compliance-frameworks)
6. [Architecture](#architecture)
7. [API Reference](#api-reference)
8. [Quick Start](#quick-start)
9. [Project Structure](#project-structure)
10. [Roadmap](#roadmap)

---

## Overview

### The Problem

| Challenge | Impact |
|-----------|--------|
| **60% of data breaches** originate from third-party vendors | Ponemon Institute |
| **$4.88M average cost** per data breach in 2024 | IBM Security |
| **6-8 hours per vendor** to manually review SOC 2 reports | Industry average |
| **200+ page documents** with critical risks buried in text | Analyst fatigue |

### The Solution

VendorAuditAI transforms third-party risk management with:

| Capability | Result |
|------------|--------|
| **AI Document Analysis** | 15-minute assessments vs 8 hours |
| **Multi-Framework Mapping** | One document mapped to 12 frameworks |
| **Autonomous Agents** | 24/7 threat detection and monitoring |
| **Natural Language Q&A** | Ask questions, get cited answers |

---

## Senior TPRM Analyst: Technical Problem-Solving Portfolio

This platform was built to solve the hardest challenges facing enterprise third-party risk management teams. Below are real-world problems and how VendorAuditAI addresses them.

---

### Challenge 1: Scaling Vendor Assessments Without Scaling Headcount

> *"How do you assess 500+ vendors annually when each SOC 2 report takes 6-8 hours to review manually?"*

**The Problem:**

Enterprise organizations onboard dozens of new vendors monthly. Each requires security assessment against multiple frameworks. Manual review doesn't scale - you either hire more analysts (expensive) or accept risk (dangerous).

**My Solution Architecture:**

```
┌─────────────────────────────────────────────────────────────────┐
│                 AI-POWERED ASSESSMENT PIPELINE                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  DOCUMENT INTAKE                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Upload SOC 2, ISO 27001, SIG, questionnaires           │   │
│  │  - PDF/DOCX parsing with OCR for scanned docs           │   │
│  │  - Automatic document type classification               │   │
│  │  - Semantic chunking for optimal AI processing          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  AI ANALYSIS ENGINE                                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Claude Opus 4.5 + RAG Architecture                     │   │
│  │  - Extract controls, findings, exceptions               │   │
│  │  - Map to 12 compliance frameworks simultaneously       │   │
│  │  - Identify gaps and missing controls                   │   │
│  │  - Generate risk scores with confidence levels          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ANALYST REVIEW                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  AI does 90% of work, analyst validates 10%             │   │
│  │  - Pre-populated findings with citations                │   │
│  │  - One-click approval or adjustment                     │   │
│  │  - Natural language Q&A for deep dives                  │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  Result: 6-8 hours → 15 minutes per assessment                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation in VendorAuditAI:**

- **Document Intelligence Module** - Processes 200+ page SOC 2 reports in under 2 minutes
- **Multi-Framework Mapping** - Single document mapped to SOC 2, NIST CSF, ISO 27001, and 9 more
- **Natural Language Query** - Ask "What encryption is used for data at rest?" and get cited answer
- **Batch Processing** - Queue multiple vendors for overnight AI analysis

**Business Results:**

| Metric | Before | After | Impact |
|--------|--------|-------|--------|
| Assessment time | 6-8 hours | 15 minutes | **-97%** |
| Analyst capacity | 50 vendors/year | 500+ vendors/year | **+900%** |
| Consistency | Variable | Standardized | **100% framework coverage** |
| Cost per assessment | $400+ | <$50 | **-87%** |

---

### Challenge 2: Vendor Categorization and Risk Tiering at Scale

> *"How do you categorize hundreds of vendors into meaningful risk tiers when they span everything from cloud infrastructure to office supplies?"*

**The Problem:**

Not all vendors are equal. A payment processor with access to financial data needs quarterly assessments. An office supply vendor needs minimal oversight. But manually categorizing vendors is subjective and inconsistent.

**My Solution: 25-Category Taxonomy with Auto-Classification**

```
┌─────────────────────────────────────────────────────────────────┐
│              INTELLIGENT VENDOR CLASSIFICATION                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  INPUT: Vendor name, website, description                       │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  AI CLASSIFICATION ENGINE                                │   │
│  │                                                          │   │
│  │  Category Detection:                                     │   │
│  │  - Cloud Infrastructure    - Payment Processing          │   │
│  │  - Data Warehouse          - Identity & Access           │   │
│  │  - AI/ML Platforms         - Analytics & BI              │   │
│  │  - Customer Support        - Security Tools              │   │
│  │  - HR & Workforce          - Marketing Tech              │   │
│  │  - Legal & Compliance      - Logistics & Delivery        │   │
│  │  + 13 more categories                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  RISK TIER ASSIGNMENT                                    │   │
│  │                                                          │   │
│  │  Tier 1 (Critical): Payment, Cloud Infra, Identity      │   │
│  │  → Quarterly assessment, executive review required       │   │
│  │                                                          │   │
│  │  Tier 2 (High): Data Warehouse, Security Tools          │   │
│  │  → Semi-annual assessment, manager approval              │   │
│  │                                                          │   │
│  │  Tier 3 (Medium): Analytics, HR Systems                 │   │
│  │  → Annual assessment, standard review                    │   │
│  │                                                          │   │
│  │  Tier 4 (Low): Office Supplies, Facilities              │   │
│  │  → Biennial assessment, self-attestation                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation in VendorAuditAI:**

- **Auto-Classification** - AI suggests category based on vendor description
- **Data Access Levels** - Track what data each vendor can access (PII, financial, health)
- **Assessment Scheduling** - Automatic reminders based on tier and last assessment
- **Override Controls** - Analysts can adjust tier with documented justification

---

### Challenge 3: AI/ML Vendor Risk - A New Category of Threat

> *"How do you assess AI vendors when traditional frameworks don't cover autonomous systems, training data risks, and model governance?"*

**The Problem:**

AI vendors introduce risks that SOC 2 and ISO 27001 weren't designed to address:
- Does the AI train on customer data?
- Can the AI take autonomous actions?
- What's the blast radius if the AI hallucinates?
- Who's liable for AI-generated outputs?

**My Solution: AI-Specific Risk Assessment Framework**

```
┌─────────────────────────────────────────────────────────────────┐
│                 AI VENDOR RISK CLASSIFICATION                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  STACK TYPE CLASSIFICATION                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  - Foundation Model (highest risk)                       │   │
│  │  - GenAI Application                                     │   │
│  │  - Fine-Tuning Platform                                  │   │
│  │  - Autonomous Agent (high risk)                          │   │
│  │  - Embedding Service                                     │   │
│  │  - MLOps Platform                                        │   │
│  │  - Inference Optimization                                │   │
│  │  - Horizontal Layer                                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  AI-SPECIFIC RISK FACTORS                                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Data Training Permissions:                              │   │
│  │  □ No training on customer data                         │   │
│  │  □ Opt-in training only                                 │   │
│  │  □ Trains on all data by default (HIGH RISK)            │   │
│  │                                                          │   │
│  │  Autonomous Action Capability:                           │   │
│  │  □ Read-only / advisory                                 │   │
│  │  □ Requires human approval                              │   │
│  │  □ Fully autonomous (HIGH RISK)                         │   │
│  │                                                          │   │
│  │  Credential Access Level:                                │   │
│  │  □ No credentials                                       │   │
│  │  □ Read-only API access                                 │   │
│  │  □ Write access / admin credentials (HIGH RISK)         │   │
│  │                                                          │   │
│  │  Blast Radius:                                           │   │
│  │  □ Single user impact                                   │   │
│  │  □ Team-wide impact                                     │   │
│  │  □ Organization-wide impact (HIGH RISK)                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  FRAMEWORK MAPPING: NIST AI RMF + Custom AI Risk Controls      │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation in VendorAuditAI:**

- **AI Tool Classification** - Dedicated module for AI vendor categorization
- **NIST AI RMF Framework** - 70+ controls specific to AI/ML systems
- **AI Governance Playbooks** - Step-by-step workflows for AI tool adoption
- **Approved AI Registry** - Pre-approved tools with deployment tracking

---

### Challenge 4: Continuous Monitoring vs Point-in-Time Assessment

> *"A SOC 2 report is a snapshot. How do you know if a vendor's security posture has degraded since their last audit?"*

**The Problem:**

Traditional TPRM is reactive - you assess vendors annually and hope nothing changes. But breaches happen between assessments. You need continuous visibility.

**My Solution: Autonomous Agent Monitoring**

```
┌─────────────────────────────────────────────────────────────────┐
│                  AI AGENT MONITORING NETWORK                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐             │
│  │  SENTINEL   │  │   VECTOR    │  │  WATCHDOG   │             │
│  │   PRIME     │  │  ANALYST    │  │    ZERO     │             │
│  │             │  │             │  │             │             │
│  │ Threat      │  │ Risk Score  │  │ Vuln        │             │
│  │ Detection   │  │ Calculation │  │ Scanning    │             │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘             │
│         │                │                │                     │
│         └────────────────┼────────────────┘                     │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    AUDIT CORE                            │   │
│  │                                                          │   │
│  │  Compliance Verification & Continuous Assessment         │   │
│  │  - Framework coverage tracking                           │   │
│  │  - Control effectiveness monitoring                      │   │
│  │  - Certification expiration alerts                       │   │
│  │  - Regulatory change impact analysis                     │   │
│  └─────────────────────────────────────────────────────────┘   │
│                          │                                      │
│                          ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  ALERT & REMEDIATION                                     │   │
│  │                                                          │   │
│  │  - Real-time risk score changes                          │   │
│  │  - Automated ticket creation (Jira, ServiceNow)          │   │
│  │  - Slack/email notifications                             │   │
│  │  - Executive dashboard updates                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation in VendorAuditAI:**

- **4 AI Agents** - Sentinel Prime, Vector Analyst, Watchdog Zero, Audit Core
- **Scheduled Assessments** - Configurable monitoring frequency per vendor
- **Integration Hub** - Push findings to Jira, ServiceNow, Slack
- **Alert Rules** - Custom thresholds for risk score changes

---

### Challenge 5: BPO and Fourth-Party Risk

> *"Your vendor outsources to another vendor. How do you assess the risk of vendors you don't have a direct relationship with?"*

**The Problem:**

Business Process Outsourcing (BPO) creates layered risk. Your payroll vendor uses a cloud provider. Your cloud provider uses a hardware manufacturer. Each layer adds risk you can't directly assess.

**My Solution: BPO Risk Management Module**

```
┌─────────────────────────────────────────────────────────────────┐
│                    BPO RISK MANAGEMENT                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  PROVIDER TRACKING                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Provider Profile:                                       │   │
│  │  - Company details, locations, headcount                 │   │
│  │  - Contract terms, SLAs, termination clauses             │   │
│  │  - Data access levels (PII, financial, health)           │   │
│  │  - Subcontractor disclosure requirements                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  PROCESS-SPECIFIC RISK                                          │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Each outsourced process assessed individually:          │   │
│  │  - Customer Support (Tier 2)                             │   │
│  │  - Data Entry (Tier 3)                                   │   │
│  │  - Financial Processing (Tier 1)                         │   │
│  │  - IT Support (Tier 2)                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  GEOGRAPHIC RISK                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Location-based risk factors:                            │   │
│  │  - Data residency requirements (GDPR, CCPA)              │   │
│  │  - Political stability risk                              │   │
│  │  - Regulatory jurisdiction                               │   │
│  │  - Business continuity considerations                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation in VendorAuditAI:**

- **BPO Module** - Dedicated management for outsourcing relationships
- **Process-Level Assessment** - Risk scoring per outsourced function
- **Geographic Tracking** - Location-based compliance mapping
- **Fourth-Party Visibility** - Track subcontractor chains

---

### Challenge 6: Demonstrating Value to Executive Leadership

> *"How do you show the board that TPRM investment prevents breaches rather than just generating paperwork?"*

**The Problem:**

TPRM teams struggle to demonstrate ROI. Executives see cost, not value. You need metrics that translate security work into business impact.

**My Solution: Executive Risk Analytics**

```
┌─────────────────────────────────────────────────────────────────┐
│                  EXECUTIVE DASHBOARD METRICS                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  RISK POSTURE                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Overall Risk Score: 72/100 (Moderate)                   │   │
│  │  Trend: ▲ 8 points improvement (90 days)                 │   │
│  │                                                          │   │
│  │  Risk Distribution:                                      │   │
│  │  Critical: 3 vendors | High: 12 | Medium: 45 | Low: 140 │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  OPERATIONAL EFFICIENCY                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Assessments Completed: 127 (YTD)                        │   │
│  │  Average Time: 18 minutes (vs. 6 hours industry avg)     │   │
│  │  Cost Savings: $380,000 (analyst time)                   │   │
│  │  Framework Coverage: 12 frameworks, 2500+ controls       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  COMPLIANCE STATUS                                              │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  SOC 2: 94% vendors compliant                            │   │
│  │  ISO 27001: 67% vendors certified                        │   │
│  │  Expiring Certs (90 days): 8 vendors                     │   │
│  │  Overdue Assessments: 3 vendors                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│  REMEDIATION PROGRESS                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  Open Findings: 47                                       │   │
│  │  Critical/High: 12 (avg resolution: 14 days)             │   │
│  │  SLA Compliance: 89%                                     │   │
│  │  Closed (30 days): 23 findings                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation in VendorAuditAI:**

- **Executive Dashboard** - Real-time risk posture visualization
- **Trend Analysis** - Historical risk score tracking
- **Exportable Reports** - Board-ready PDF/CSV exports
- **Audit Trail** - Complete evidence for compliance audits

---

### Technical Implementation Summary

| Challenge | Solution | Module |
|-----------|----------|--------|
| Scale assessments | AI document analysis | Document Intelligence |
| Categorize vendors | 25-category taxonomy | Vendor Management |
| Assess AI vendors | NIST AI RMF + custom | AI Tool Classification |
| Continuous monitoring | 4 autonomous agents | AI Agent Network |
| BPO/fourth-party risk | Process-level tracking | BPO Module |
| Executive reporting | Real-time dashboards | Risk Analytics |

---

## Key Features

### Core Capabilities

| Feature | Description |
|---------|-------------|
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
|---------|----------------|
| **Authentication** | JWT tokens, refresh tokens, session management |
| **SSO/SAML 2.0** | Azure AD, Google, Okta, OneLogin support |
| **MFA/TOTP** | Time-based one-time passwords with QR provisioning |
| **Audit Logging** | Complete trail of user actions and system events |
| **Rate Limiting** | Configurable per-endpoint protection |
| **Encryption** | AES-256 at rest, TLS 1.3 in transit |

---

## Platform Modules

### 1. Executive Dashboard

Real-time overview of your vendor risk posture with animated metrics and visualizations.

- Total vendors, documents, and findings
- Risk distribution by severity
- Assessment completion rates
- Trending risk indicators

### 2. AI Governance Playbooks

Guided workflows for AI tool adoption across departments.

| Playbook | Purpose |
|----------|---------|
| **Tool Selection** | 5-step evaluation process for new AI tools |
| **Secure Deployment** | 5-step guide for safe AI tool deployment |
| **Regression Protection** | 4-step ongoing monitoring checklist |

- Step-by-step wizards with checklists
- Multi-approver workflows
- Progress tracking per vendor

### 3. Approved AI Vendor Registry

Self-service registry for pre-approved AI tools with deployment tracking.

- **Browse Approved Tools** - Search and filter approved vendors
- **Self-Service Deployment** - Deploy approved tools to your team
- **Request New Tools** - Submit requests for security evaluation
- **Department Restrictions** - Control which teams can use which tools
- **Data Classification Limits** - Enforce data handling policies

### 4. BPO Risk Management

Business Process Outsourcing risk module for service provider management.

- Provider onboarding and tracking
- Process-specific risk assessments
- Geographic location tracking
- Contract and SLA management
- Data access level controls

### 5. Integration Hub

Central hub for external system connections.

| Integration | Capabilities |
|-------------|--------------|
| **Jira** | Create issues, sync status, bidirectional updates |
| **ServiceNow** | Incident management, change requests |
| **Slack** | Notifications, alerts, channel posting |
| **Email** | SMTP notifications, digest reports |
| **Webhooks** | Custom integrations, event triggers |

- Test connections before enabling
- View integration logs and history
- Configure field mappings

### 6. Vendor Management

Complete vendor lifecycle management with enterprise categorization.

**Risk Tiers:**

| Tier | Risk Level | Assessment Frequency |
|:----:|:----------:|:---------------------|
| 1 | Critical | Quarterly |
| 2 | High | Semi-annual |
| 3 | Medium | Annual |
| 4 | Low | Every 2-3 years |

**25 Vendor Categories:**
- Cloud Infrastructure, Data Warehouse, Payment Processing
- Identity & Access, AI/ML Platforms, Analytics & BI
- Customer Support, Security Tools, HR & Workforce
- And 16 more...

### 7. Document Management

Upload, process, and analyze vendor security documents.

- PDF, DOCX, and scanned document support
- Semantic chunking for AI analysis
- Vector embeddings for similarity search
- Processing status tracking

### 8. Compliance Analysis

AI-powered analysis with multi-framework mapping.

- Run analysis on any document
- View findings by severity (Critical, High, Medium, Low)
- Map to 12 compliance frameworks
- Gap detection and recommendations

### 9. Remediation Workflow

Track and manage security findings to resolution.

- Task creation from findings
- Priority and SLA management
- Status workflow (Open -> In Progress -> Resolved)
- External issue tracker sync (Jira, ServiceNow)
- Comment threads and attachments

### 10. Continuous Monitoring

Proactive vendor security monitoring.

- Scheduled assessment runs
- Alert rules and thresholds
- Notification channels
- Certificate expiration tracking
- Compliance deadline alerts

### 11. AI Tool Classification

Classify AI tools by technical architecture and risk level.

**Stack Types:**
- Foundation Model
- GenAI Application
- Inference Optimization
- Fine-Tuning Platform
- Autonomous Agent
- Horizontal Layer
- Embedding Service
- MLOps Platform

**Risk Factors:**
- Credential access level
- Autonomous action capabilities
- Data training permissions
- Blast radius assessment

### 12. Risk Analytics

Advanced analytics and reporting.

- Risk score trends over time
- Vendor comparison charts
- Framework coverage heatmaps
- Exportable reports (CSV, PDF)

---

## AI Agent Network

Four autonomous AI agents continuously monitor your vendor ecosystem.

| Agent | Role | Capabilities |
|:------|:-----|:-------------|
| **Sentinel Prime** | Threat Detection | Scans documents for security risks, anomalies, and emerging threats |
| **Vector Analyst** | Risk Assessment | Calculates risk scores based on findings, compliance, and history |
| **Watchdog Zero** | Vulnerability Scanner | Identifies security gaps, missing controls, expired certifications |
| **Audit Core** | Compliance Verification | Maps documents to frameworks, calculates compliance coverage |

### Agent Features

- **Autonomous Execution** - Agents run on schedules or triggers
- **Task Queue** - Submit tasks and track completion
- **Activity Logs** - Full audit trail of agent actions
- **Status Dashboard** - Real-time agent health monitoring

---

## Compliance Frameworks

VendorAuditAI supports 12 compliance frameworks with 2500+ controls.

| Framework | Controls | Version | Best For |
|:---------:|:--------:|:-------:|:---------|
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

### Authentication

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| POST | `/api/v1/auth/login` | User authentication |
| POST | `/api/v1/auth/register` | User registration |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/mfa/enable` | Enable MFA |
| POST | `/api/v1/auth/mfa/verify` | Verify MFA code |

### Vendors

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/vendors` | List all vendors |
| POST | `/api/v1/vendors` | Create vendor |
| GET | `/api/v1/vendors/{id}` | Get vendor details |
| PUT | `/api/v1/vendors/{id}` | Update vendor |
| DELETE | `/api/v1/vendors/{id}` | Delete vendor |

### Documents

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| POST | `/api/v1/documents/upload` | Upload document |
| GET | `/api/v1/documents` | List documents |
| GET | `/api/v1/documents/{id}` | Get document details |
| DELETE | `/api/v1/documents/{id}` | Delete document |

### Analysis

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| POST | `/api/v1/analysis/documents/{id}/analyze` | Run AI analysis |
| GET | `/api/v1/analysis/findings` | List findings |
| GET | `/api/v1/analysis/findings/{id}` | Get finding details |

### Query

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| POST | `/api/v1/query` | Natural language Q&A |
| GET | `/api/v1/query/history` | Query history |

### Agents

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/agents` | List AI agents |
| GET | `/api/v1/agents/{id}` | Get agent details |
| POST | `/api/v1/agents/{id}/tasks` | Create agent task |
| GET | `/api/v1/agents/{id}/logs` | View agent logs |

### Playbooks

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/playbooks` | List playbooks |
| GET | `/api/v1/playbooks/{id}` | Get playbook details |
| POST | `/api/v1/playbooks/{id}/start` | Start playbook |
| POST | `/api/v1/playbooks/progress/{id}/complete-step` | Complete step |

### Approved Vendors

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/approved-vendors` | List approved vendors |
| POST | `/api/v1/approved-vendors` | Add approved vendor |
| GET | `/api/v1/approved-vendors/stats` | Dashboard statistics |
| POST | `/api/v1/approved-vendors/deploy` | Deploy to team |
| POST | `/api/v1/approved-vendors/request` | Request new tool |
| GET | `/api/v1/approved-vendors/my-deployments` | User deployments |
| GET | `/api/v1/approved-vendors/my-requests` | User requests |

### BPO

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/bpo/providers` | List BPO providers |
| POST | `/api/v1/bpo/providers` | Create provider |
| GET | `/api/v1/bpo/dashboard` | BPO dashboard stats |
| GET | `/api/v1/bpo/providers/{id}/processes` | List processes |
| POST | `/api/v1/bpo/assessments` | Create assessment |

### Integrations

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/integrations` | List integrations |
| POST | `/api/v1/integrations` | Create integration |
| POST | `/api/v1/integrations/{id}/test` | Test connection |
| POST | `/api/v1/integrations/{id}/sync` | Trigger sync |
| GET | `/api/v1/integrations/{id}/logs` | View logs |

### Compliance

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/frameworks` | List frameworks |
| GET | `/api/v1/frameworks/{id}` | Get framework details |
| GET | `/api/v1/frameworks/search` | Search controls |

### Remediation

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/remediation/tasks` | List tasks |
| POST | `/api/v1/remediation/tasks` | Create task |
| PATCH | `/api/v1/remediation/tasks/{id}` | Update task |
| POST | `/api/v1/remediation/tasks/{id}/create-external` | Create in Jira/ServiceNow |

### Monitoring

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| GET | `/api/v1/monitoring/alerts` | List alerts |
| GET | `/api/v1/monitoring/schedules` | List schedules |
| POST | `/api/v1/monitoring/schedules` | Create schedule |

### Full API Documentation

- **Swagger UI:** [vendorauditai-production.up.railway.app/docs](https://vendorauditai-production.up.railway.app/docs)
- **ReDoc:** [vendorauditai-production.up.railway.app/redoc](https://vendorauditai-production.up.railway.app/redoc)

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 16+
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
|   |   |   |-- llm.py            # Claude/Gemini integration
|   |   |   |-- embedding.py      # OpenAI embeddings
|   |   |   |-- processing.py     # Document pipeline
|   |   |   |-- compliance.py     # Framework management
|   |   |   |-- approved_vendor.py # Approved AI registry
|   |   |   |-- bpo.py            # BPO risk management
|   |   |   |-- integrations/     # External system connectors
|   |   |   `-- playbook.py       # AI governance playbooks
|   |   `-- prompts/              # AI prompt templates
|   |-- alembic/versions/         # Database migrations
|   |-- tests/                    # 129 pytest tests
|   `-- requirements.txt
|-- frontend/
|   |-- src/
|   |   |-- components/           # React components
|   |   |   |-- layout/           # Sidebar, header, navigation
|   |   |   `-- ui/               # Shadcn/UI components
|   |   |-- pages/                # Route pages
|   |   |   |-- Dashboard.tsx     # Executive dashboard
|   |   |   |-- Playbooks.tsx     # AI governance playbooks
|   |   |   |-- ApprovedVendors.tsx # Approved AI registry
|   |   |   |-- BPO.tsx           # BPO risk management
|   |   |   |-- Integrations.tsx  # Integration hub
|   |   |   |-- Vendors.tsx       # Vendor management
|   |   |   |-- Documents.tsx     # Document management
|   |   |   |-- Analysis.tsx      # Compliance analysis
|   |   |   |-- Remediation.tsx   # Remediation workflow
|   |   |   |-- Monitoring.tsx    # Continuous monitoring
|   |   |   |-- Risk.tsx          # Risk analytics
|   |   |   |-- Agents.tsx        # AI agent network
|   |   |   `-- Query.tsx         # Natural language Q&A
|   |   |-- hooks/                # Custom React hooks
|   |   |-- stores/               # State management
|   |   `-- lib/                  # API client, utilities
|   `-- package.json
|-- docs/
|   `-- PLATFORM_OVERVIEW.md
|-- COMPETITIVE_ANALYSIS.md
`-- README.md
```

---

## Roadmap

### Completed

- [x] **v0.1.0** - Document upload, parsing, 9 frameworks, SSO/MFA
- [x] **v0.2.0** - AI Query feature, multi-LLM support, production deployment
- [x] **v0.3.0** - SIG 2026, DORA, HECVAT frameworks
- [x] **v0.4.0** - Enterprise 25-category TPRM taxonomy
- [x] **v0.5.0** - Full CRUD operations, remediation workflows, monitoring
- [x] **v0.6.0** - AI Agent Network (4 agents), Vendor Detail pages
- [x] **v0.7.0** - Risk scoring, analytics enhancements
- [x] **v0.8.0** - Document Intelligence, Multi-Framework Compliance
- [x] **v0.9.0** - NIST AI RMF, CSA CAIQ, Continuous Monitoring
- [x] **v1.0.0** - Enterprise Security: SSO/SAML 2.0, MFA/TOTP, Audit Logging
- [x] **v1.1.0** - AI Governance Playbooks, Approved AI Registry, BPO Management, Integration Hub

### Upcoming

- [ ] **v1.2.0** - Custom framework builder, advanced analytics
- [ ] **v1.3.0** - Mobile responsive design, dark mode improvements
- [ ] **v2.0.0** - GraphQL API, multi-tenant architecture

---

## Technology Stack

| Category | Technologies |
|----------|-------------|
| **AI/ML** | Claude Opus 4.5, Gemini 3.0, OpenAI Embeddings, RAG Architecture |
| **Backend** | Python 3.12, FastAPI, SQLAlchemy 2.0, Pydantic v2, Async/Await |
| **Frontend** | React 18, TypeScript 5, TailwindCSS, Shadcn/UI, Framer Motion |
| **Database** | PostgreSQL 16, pgvector, Alembic Migrations |
| **Security** | JWT, SAML 2.0 SSO, MFA/TOTP, RBAC, AES-256, TLS 1.3 |
| **Infrastructure** | Railway, Netlify, GitHub Actions CI/CD |

---

## Author

**Dominic M. Hoang**

GitHub: [@MikeDominic92](https://github.com/MikeDominic92)

---

## Related Projects

| Project | Description |
|---------|-------------|
| [ai-access-sentinel](https://github.com/MikeDominic92/ai-access-sentinel) | ITDR platform with ML-powered anomaly detection |
| [entra-id-governance](https://github.com/MikeDominic92/entra-id-governance) | Microsoft Entra ID governance toolkit |
| [keyless-kingdom](https://github.com/MikeDominic92/keyless-kingdom) | Multi-cloud workload identity federation |
| [okta-sso-hub](https://github.com/MikeDominic92/okta-sso-hub) | Enterprise SSO with SAML, OIDC, SCIM |

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
