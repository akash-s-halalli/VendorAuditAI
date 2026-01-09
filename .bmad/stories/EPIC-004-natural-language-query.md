# EPIC-004: Natural Language Query

**Status:** Pending
**Priority:** High
**Complexity:** Medium

---

## Overview

Implement a natural language query interface that allows users to ask questions about their documents and receive context-aware, cited responses using RAG.

---

## Stories

### STORY-018: Query Service [PENDING]
**Complexity:** Medium

Create the query service that handles natural language questions.

**Acceptance Criteria:**
- [ ] Create query service using existing Claude and search services
- [ ] Implement context retrieval from relevant chunks
- [ ] Generate answers with citations to source documents
- [ ] Support conversation history for follow-up questions
- [ ] Handle queries across multiple documents

---

### STORY-019: Query Schemas [PENDING]
**Complexity:** Low

Create Pydantic schemas for query requests and responses.

**Acceptance Criteria:**
- [ ] QueryRequest schema with question, document_ids filter, conversation_id
- [ ] QueryResponse schema with answer, citations, confidence, sources
- [ ] ConversationMessage schema for chat history
- [ ] Citation schema with document_id, page, excerpt, relevance

---

### STORY-020: Query API Endpoints [PENDING]
**Complexity:** Medium

Create REST API endpoints for the query interface.

**Acceptance Criteria:**
- [ ] POST /api/v1/query - Submit a question
- [ ] POST /api/v1/query/conversation - Continue conversation
- [ ] GET /api/v1/query/history - Get query history
- [ ] GET /api/v1/query/{query_id} - Get specific query result

---

### STORY-021: Query Model [PENDING]
**Complexity:** Low

Create database model to store query history.

**Acceptance Criteria:**
- [ ] QueryHistory model with question, answer, citations
- [ ] ConversationThread model for multi-turn conversations
- [ ] Link to organization and user
- [ ] Store token usage and response time

---

## Completion Criteria

EPIC-004 is complete when:
1. Users can ask natural language questions about documents
2. Answers include citations to specific pages/sections
3. Follow-up questions maintain conversation context
4. Query history is persisted for review
5. All endpoints are authenticated and org-isolated

---

## Next Epic

EPIC-005: Frontend Implementation
- React components for all features
- Authentication flow
- Document management UI
- Analysis dashboard
- Query interface
