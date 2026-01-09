# EPIC-004: Natural Language Query

**Status:** COMPLETED
**Priority:** High
**Complexity:** Medium

---

## Overview

Implement a natural language query interface that allows users to ask questions about their documents and receive context-aware, cited responses using RAG.

---

## Stories

### STORY-018: Query Service [COMPLETED]
**Complexity:** Medium

Create the query service that handles natural language questions.

**Acceptance Criteria:**
- [x] Create query service using existing Claude and search services
- [x] Implement context retrieval from relevant chunks
- [x] Generate answers with citations to source documents
- [x] Support conversation history for follow-up questions
- [x] Handle queries across multiple documents

**Implementation:** `backend/app/services/query.py`

---

### STORY-019: Query Schemas [COMPLETED]
**Complexity:** Low

Create Pydantic schemas for query requests and responses.

**Acceptance Criteria:**
- [x] QueryRequest schema with question, document_ids filter, conversation_id
- [x] QueryResponse schema with answer, citations, confidence, sources
- [x] ConversationMessage schema for chat history
- [x] Citation schema with document_id, page, excerpt, relevance

**Implementation:** `backend/app/schemas/query.py`

---

### STORY-020: Query API Endpoints [COMPLETED]
**Complexity:** Medium

Create REST API endpoints for the query interface.

**Acceptance Criteria:**
- [x] POST /api/v1/query - Submit a question
- [x] POST /api/v1/query/conversation - Create/continue conversation
- [x] GET /api/v1/query/history - Get query history
- [x] GET /api/v1/query/{query_id} - Get specific query result

**Implementation:** `backend/app/api/v1/endpoints/query.py`

---

### STORY-021: Query Model [COMPLETED]
**Complexity:** Low

Create database model to store query history.

**Acceptance Criteria:**
- [x] QueryHistory model with question, answer, citations
- [x] ConversationThread model for multi-turn conversations
- [x] Link to organization and user
- [x] Store token usage and response time

**Implementation:** `backend/app/models/query.py`

---

## Completion Criteria

EPIC-004 is complete when:
1. [x] Users can ask natural language questions about documents
2. [x] Answers include citations to specific pages/sections
3. [x] Follow-up questions maintain conversation context
4. [x] Query history is persisted for review
5. [x] All endpoints are authenticated and org-isolated

---

## Next Epic

EPIC-005: Frontend Implementation
- React components for all features
- Authentication flow
- Document management UI
- Analysis dashboard
- Query interface
