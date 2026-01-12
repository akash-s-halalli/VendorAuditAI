# VendorAuditAI Platform Overview

**How It Works: From Upload to Insight**

---

## End-to-End Workflow

```
+===========================================================================+
|                        VENDORAUDITAI WORKFLOW                              |
+===========================================================================+

                              CUSTOMER JOURNEY
    +-----------------------------------------------------------------------+
    |                                                                       |
    |  [1] UPLOAD         [2] PROCESS         [3] ANALYZE       [4] ACT    |
    |      |                   |                   |                |       |
    |      v                   v                   v                v       |
    |  +--------+         +---------+         +----------+    +---------+  |
    |  | Vendor |         |   AI    |         | Natural  |    |Remediate|  |
    |  | Docs   |-------->| Engine  |-------->| Language |----| & Track |  |
    |  +--------+         +---------+         |  Query   |    +---------+  |
    |                                         +----------+                  |
    +-----------------------------------------------------------------------+

                                    |
                                    v

    +-----------------------------------------------------------------------+
    |                        DOCUMENT TYPES SUPPORTED                        |
    +-----------------------------------------------------------------------+
    |                                                                       |
    |   [SOC 2 Type II]  [SIG Lite]  [SIG Core]  [HECVAT]  [ISO 27001]     |
    |                                                                       |
    |   [Pen Test Reports]  [Security Questionnaires]  [Any PDF/DOCX]      |
    |                                                                       |
    +-----------------------------------------------------------------------+
```

---

## Stage 1: Document Upload

```
USER ACTION                              SYSTEM RESPONSE
-----------                              ---------------

  +--------+                             +------------------+
  |  User  |  ---> Drag & Drop --->      |  Upload API     |
  +--------+      or Browse              +------------------+
                                                |
                                                v
                                         +------------------+
                                         | File Validation |
                                         | - Type check    |
                                         | - Size check    |
                                         | - Virus scan    |
                                         +------------------+
                                                |
                                                v
                                         +------------------+
                                         | Secure Storage  |
                                         | - Encrypted     |
                                         | - Indexed       |
                                         +------------------+

SUPPORTED FORMATS:
+----------+----------+----------+
|   PDF    |   DOCX   |  Scanned |
|  Native  |  Native  |   OCR    |
+----------+----------+----------+
```

---

## Stage 2: AI Processing Pipeline

```
+===========================================================================+
|                          PROCESSING PIPELINE                               |
+===========================================================================+

    UPLOADED          PARSING           CHUNKING          EMBEDDING
        |                |                 |                  |
        v                v                 v                  v
    +-------+        +-------+         +-------+          +-------+
    | .PDF  |        | Text  |         |Semantic|         |Vector |
    | .DOCX |------->|Extract|-------->|Chunks  |-------->|Search |
    +-------+        +-------+         +-------+          +-------+
                         |                 |                  |
                         v                 v                  v
                    +---------+       +---------+        +---------+
                    |Metadata |       | Section |        |OpenAI   |
                    |Extract  |       | Headers |        |Embedding|
                    +---------+       +---------+        +---------+


CHUNKING DETAIL:
+-----------------------------------------------------------------------+
|  Original Document (200 pages)                                         |
|  +------------------------------------------------------------------+ |
|  | Section 1: Executive Summary                                      | |
|  | Section 2: System Description                                     | |
|  | Section 3: Control Objectives                                     | |
|  | Section 4: Testing Results                                        | |
|  | Section 5: Auditor Opinion                                        | |
|  +------------------------------------------------------------------+ |
|                              |                                         |
|                              v                                         |
|  +----------+ +----------+ +----------+ +----------+ +----------+     |
|  | Chunk 1  | | Chunk 2  | | Chunk 3  | | Chunk 4  | | Chunk N  |     |
|  | 500 tok  | | 500 tok  | | 500 tok  | | 500 tok  | | 500 tok  |     |
|  +----------+ +----------+ +----------+ +----------+ +----------+     |
+-----------------------------------------------------------------------+
```

---

## Stage 3: AI Analysis Engine

```
+===========================================================================+
|                      CLAUDE OPUS 4.5 AI ENGINE                            |
+===========================================================================+

                    USER QUERY
                        |
                        v
                +---------------+
                |  Query Input  |
                | "What controls|
                |  for data     |
                |  encryption?" |
                +---------------+
                        |
                        v
            +---------------------+
            |   RAG RETRIEVAL     |
            +---------------------+
            | 1. Embed query      |
            | 2. Vector search    |
            | 3. Find relevant    |
            |    chunks           |
            +---------------------+
                        |
                        v
            +---------------------+
            |   CONTEXT WINDOW    |
            +---------------------+
            | Top 10 relevant     |
            | chunks + metadata   |
            +---------------------+
                        |
                        v
            +---------------------+
            |   CLAUDE OPUS 4.5   |
            +---------------------+
            | Generate answer     |
            | with citations      |
            +---------------------+
                        |
                        v
            +---------------------+
            |   STRUCTURED        |
            |   RESPONSE          |
            +---------------------+
            | - Answer text       |
            | - Source citations  |
            | - Confidence score  |
            | - Related sections  |
            +---------------------+


FRAMEWORK MAPPING:
+-----------------------------------------------------------------------+
|                                                                       |
|  Document Control --> Maps To --> Multiple Frameworks                 |
|                                                                       |
|  "AES-256 encryption    [SOC 2 CC6.1]                                |
|   at rest"         ---> [NIST 800-53 SC-28]                          |
|                         [ISO 27001 A.10.1.1]                         |
|                         [PCI-DSS 3.4]                                |
|                         [HIPAA 164.312(a)(2)(iv)]                    |
|                                                                       |
+-----------------------------------------------------------------------+
```

---

## Stage 4: Findings & Remediation

```
+===========================================================================+
|                      FINDINGS DASHBOARD                                    |
+===========================================================================+

    GAP ANALYSIS RESULTS
    +-------------------------------------------------------------------+
    |                                                                   |
    |  CRITICAL [!!!]  HIGH [!!]   MEDIUM [!]   LOW [.]   INFO [i]    |
    |     2              5           12           8          15        |
    |                                                                   |
    +-------------------------------------------------------------------+

    FINDING DETAIL:
    +-------------------------------------------------------------------+
    |  [CRITICAL] Missing MFA for Administrative Access                 |
    |  +---------------------------------------------------------+     |
    |  | Framework: SOC 2 CC6.1, NIST AC-2                        |     |
    |  | Source: Page 47, Section 3.2.1                           |     |
    |  | Evidence: "Password-only auth for admin console"         |     |
    |  | Remediation: Implement TOTP/FIDO2 MFA                    |     |
    |  | SLA: 30 days                                             |     |
    |  +---------------------------------------------------------+     |
    +-------------------------------------------------------------------+


    REMEDIATION WORKFLOW:
    +-------+      +--------+      +----------+      +--------+
    |Finding|----->| Assign |----->|  Track   |----->| Verify |
    |Created|      |  Owner |      | Progress |      |  Close |
    +-------+      +--------+      +----------+      +--------+
        |              |               |                |
        v              v               v                v
    [Jira Ticket] [Email Alert] [Dashboard] [Audit Trail]
```

---

## Risk Scoring Algorithm

```
+===========================================================================+
|                      VENDOR RISK SCORE                                     |
+===========================================================================+

    SCORE COMPONENTS:
    +-------------------------------------------------------------------+
    |                                                                   |
    |  Control Coverage    [============........]  60%    Weight: 30%  |
    |  Finding Severity    [================....]  80%    Weight: 25%  |
    |  Audit Opinion       [====================]  100%   Weight: 20%  |
    |  Remediation Status  [========............]  40%    Weight: 15%  |
    |  Document Currency   [================....]  80%    Weight: 10%  |
    |                                                                   |
    +-------------------------------------------------------------------+
                                    |
                                    v
    +-------------------------------------------------------------------+
    |                                                                   |
    |              OVERALL RISK SCORE: 72 / 100                        |
    |                                                                   |
    |              [======================........]                     |
    |                                                                   |
    |              Rating: MEDIUM RISK                                  |
    |              Recommendation: Proceed with conditions              |
    |                                                                   |
    +-------------------------------------------------------------------+


    RISK TIERS:
    +----------+----------+----------+----------+----------+
    | CRITICAL |   HIGH   |  MEDIUM  |   LOW    |  MINIMAL |
    |  0-20    |  21-40   |  41-60   |  61-80   |  81-100  |
    +----------+----------+----------+----------+----------+
    |   RED    |  ORANGE  |  YELLOW  |  GREEN   |   BLUE   |
    +----------+----------+----------+----------+----------+
```

---

## Continuous Monitoring

```
+===========================================================================+
|                      CONTINUOUS MONITORING                                 |
+===========================================================================+

    MONITORING SCHEDULE:
    +-------------------------------------------------------------------+
    |                                                                   |
    |  DAILY:    Security news scanning for vendor mentions            |
    |  WEEKLY:   Control status check against SLAs                     |
    |  MONTHLY:  Full re-assessment prompt                             |
    |  ANNUALLY: Complete document refresh required                    |
    |                                                                   |
    +-------------------------------------------------------------------+

    ALERT TYPES:
    +-------------------------------------------------------------------+
    |                                                                   |
    |  [!] Document Expiring    - SOC 2 report > 11 months old        |
    |  [!] SLA Breach           - Remediation task overdue            |
    |  [!] Risk Score Change    - Vendor score dropped > 10 points    |
    |  [!] New Breach           - Vendor mentioned in security news   |
    |                                                                   |
    +-------------------------------------------------------------------+

    NOTIFICATION CHANNELS:
    +----------+     +----------+     +----------+     +----------+
    |  Email   |     |  Slack   |     |  Teams   |     | Webhook  |
    +----------+     +----------+     +----------+     +----------+
```

---

## Data Flow Architecture

```
+===========================================================================+
|                      SYSTEM ARCHITECTURE                                   |
+===========================================================================+

    +-------------------+
    |     FRONTEND      |
    |    (Netlify)      |
    |   React + TS      |
    +--------+----------+
             |
             | HTTPS/REST API
             |
    +--------v----------+
    |     BACKEND       |
    |    (Railway)      |
    |   FastAPI + Py    |
    +--------+----------+
             |
    +--------+----------+----------+----------+
    |        |          |          |          |
    v        v          v          v          v
+------+ +------+ +--------+ +--------+ +--------+
|Postgr| |Redis | |Claude  | |OpenAI  | |Storage |
|  SQL | |Cache | |API     | |Embed   | |Backend |
+------+ +------+ +--------+ +--------+ +--------+


    SECURITY LAYERS:
    +-------------------------------------------------------------------+
    |  [TLS 1.3] --> [Rate Limit] --> [Auth] --> [RBAC] --> [Encrypt]  |
    |                                                                   |
    |  - All traffic encrypted in transit                              |
    |  - API rate limiting (DDoS protection)                           |
    |  - JWT + MFA authentication                                       |
    |  - Role-based access control                                     |
    |  - AES-256 encryption at rest                                    |
    +-------------------------------------------------------------------+
```

---

## Comparison: Before & After VendorAuditAI

```
+===========================================================================+
|                      BEFORE vs AFTER                                       |
+===========================================================================+

    BEFORE (Manual Process):
    +-------------------------------------------------------------------+
    |  Day 1:  Receive SOC 2 report (PDF, 200 pages)                   |
    |  Day 2:  Security analyst begins reading                          |
    |  Day 3:  Continue reading, taking notes                           |
    |  Day 4:  Map controls to internal framework                       |
    |  Day 5:  Identify gaps, document findings                         |
    |  Day 6:  Create Excel tracker for remediation                     |
    |  Day 7:  Present to stakeholders                                  |
    |  Day 8:  Send remediation requests to vendor                      |
    |                                                                   |
    |  TOTAL TIME: 8 business days                                     |
    |  TOTAL COST: ~$2,000 (analyst time)                              |
    +-------------------------------------------------------------------+


    AFTER (VendorAuditAI):
    +-------------------------------------------------------------------+
    |  Minute 0:   Upload SOC 2 report                                 |
    |  Minute 1:   AI parses and chunks document                       |
    |  Minute 5:   Embeddings generated                                |
    |  Minute 10:  Gap analysis complete                               |
    |  Minute 15:  Review AI findings, ask questions                   |
    |  Minute 20:  Remediation tasks auto-created                      |
    |  Minute 25:  Share report with stakeholders                      |
    |                                                                   |
    |  TOTAL TIME: 25 minutes                                          |
    |  TOTAL COST: Platform subscription                               |
    +-------------------------------------------------------------------+


    TIME SAVINGS VISUALIZATION:
    +-------------------------------------------------------------------+
    |                                                                   |
    |  Manual:  [========================================] 8 days      |
    |                                                                   |
    |  VendorAuditAI:  [=] 25 min                                      |
    |                                                                   |
    |  IMPROVEMENT: 99% time reduction                                 |
    |                                                                   |
    +-------------------------------------------------------------------+
```

---

## ROI Calculator

```
+===========================================================================+
|                      RETURN ON INVESTMENT                                  |
+===========================================================================+

    ASSUMPTIONS:
    - 100 vendors assessed annually
    - Analyst cost: $75/hour
    - Manual assessment: 8 hours each

    MANUAL PROCESS COST:
    +-------------------------------------------------------------------+
    |  100 vendors x 8 hours x $75/hour = $60,000/year                 |
    +-------------------------------------------------------------------+

    VENDORAUDITAI COST:
    +-------------------------------------------------------------------+
    |  Professional Plan: ~$15,000/year                                |
    +-------------------------------------------------------------------+

    NET SAVINGS:
    +-------------------------------------------------------------------+
    |                                                                   |
    |  Annual Savings: $45,000                                         |
    |  3-Year Savings: $135,000                                        |
    |  ROI: 300%                                                       |
    |                                                                   |
    +-------------------------------------------------------------------+

    PLUS HIDDEN BENEFITS:
    +-------------------------------------------------------------------+
    |  [+] Faster vendor onboarding (revenue acceleration)             |
    |  [+] Reduced audit findings (compliance cost avoidance)          |
    |  [+] Better risk visibility (breach prevention)                  |
    |  [+] Analyst productivity (redeploy to strategic work)          |
    +-------------------------------------------------------------------+
```

---

## Getting Started

```
+===========================================================================+
|                      QUICK START GUIDE                                     |
+===========================================================================+

    STEP 1: Sign Up
    +-------------------------------------------------------------------+
    |  Visit: https://vendor-audit-ai.netlify.app                      |
    |  Create account with email + password                            |
    |  Enable MFA (recommended)                                        |
    +-------------------------------------------------------------------+

    STEP 2: Upload First Document
    +-------------------------------------------------------------------+
    |  Go to Documents tab                                              |
    |  Drag and drop any SOC 2, SIG, or security document              |
    |  Wait 1-2 minutes for processing                                  |
    +-------------------------------------------------------------------+

    STEP 3: Ask Questions
    +-------------------------------------------------------------------+
    |  Go to Query tab                                                  |
    |  Type: "What encryption controls are documented?"                |
    |  Get AI-generated answer with source citations                   |
    +-------------------------------------------------------------------+

    STEP 4: Review Findings
    +-------------------------------------------------------------------+
    |  Go to Findings tab                                               |
    |  See auto-detected gaps and recommendations                      |
    |  Create remediation tasks                                        |
    +-------------------------------------------------------------------+

    DEMO CREDENTIALS:
    +-------------------------------------------------------------------+
    |  Email:    newdemo@vendorauditai.com                             |
    |  Password: Demo12345                                              |
    +-------------------------------------------------------------------+
```

---

*VendorAuditAI - Securing the supply chain, one vendor at a time.*
