# EPIC-003: LLM Analysis Engine

**Status:** In Progress
**Priority:** Critical
**Complexity:** High

---

## Overview

Implement the LLM-powered analysis engine that uses Claude to analyze document chunks against compliance frameworks, generate findings with citations, and provide gap analysis.

---

## Stories

### STORY-013: Claude API Integration [PENDING]
**Complexity:** Medium

Integrate Anthropic Claude API for document analysis.

**Acceptance Criteria:**
- [ ] Create Claude service with async support
- [ ] Implement rate limiting and retry logic
- [ ] Add structured output parsing
- [ ] Configure model settings (claude-sonnet-4-20250514)
- [ ] Handle API errors gracefully

---

### STORY-014: Compliance Framework Data [PENDING]
**Complexity:** Medium

Create data structures for compliance frameworks.

**Acceptance Criteria:**
- [ ] Define framework model (NIST, ISO, SOC2 TSC, CIS)
- [ ] Create control/requirement data structures
- [ ] Load framework definitions from config
- [ ] Implement framework selection logic

---

### STORY-015: Finding Model [PENDING]
**Complexity:** Medium

Create data model for analysis findings.

**Acceptance Criteria:**
- [ ] Create Finding SQLAlchemy model
- [ ] Add severity levels (critical, high, medium, low, info)
- [ ] Include citation references (page, section, chunk)
- [ ] Link findings to documents and frameworks
- [ ] Create Finding schemas

---

### STORY-016: RAG Analysis Pipeline [PENDING]
**Complexity:** High

Implement RAG-based document analysis.

**Acceptance Criteria:**
- [ ] Create analysis prompt templates
- [ ] Retrieve relevant chunks for analysis context
- [ ] Generate findings with Claude
- [ ] Extract citations from responses
- [ ] Store analysis results

---

### STORY-017: Analysis API [PENDING]
**Complexity:** Medium

Create API endpoints for analysis operations.

**Acceptance Criteria:**
- [ ] Trigger analysis endpoint
- [ ] List findings endpoint
- [ ] Get finding details endpoint
- [ ] Export findings endpoint
- [ ] Analysis status tracking

---

## Next Epic

EPIC-004: Natural Language Query
- Query interface for document Q&A
- Context-aware responses
- Multi-document search
