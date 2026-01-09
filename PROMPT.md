# VendorAuditAI - Development Prompt

## Current Task: EPIC-004 Natural Language Query

### Objective
Implement the natural language query interface for VendorAuditAI that allows users to ask questions about their compliance documents and receive context-aware, cited responses.

### Stories to Complete

1. **STORY-018: Query Service**
   - Create `backend/app/services/query.py`
   - Use existing `llm.py` Claude service for answers
   - Use existing `search.py` for context retrieval
   - Support conversation history

2. **STORY-019: Query Schemas**
   - Create `backend/app/schemas/query.py`
   - QueryRequest, QueryResponse, Citation schemas
   - Update `schemas/__init__.py`

3. **STORY-020: Query API Endpoints**
   - Create `backend/app/api/v1/endpoints/query.py`
   - POST /query, POST /query/conversation
   - GET /query/history, GET /query/{id}
   - Update `router.py`

4. **STORY-021: Query Model**
   - Create `backend/app/models/query.py`
   - QueryHistory and ConversationThread models
   - Update `models/__init__.py`

### Completion Promise

When all stories are complete:
- All files created and properly imported
- Router updated with query endpoints
- Services and schemas exported
- Story file updated with [COMPLETED] status

Output: <promise>EPIC-004-COMPLETE</promise>

### Quality Gates

Before marking complete:
- [ ] All imports resolve correctly
- [ ] No syntax errors
- [ ] Follows existing code patterns
- [ ] Multi-tenant isolation maintained
- [ ] Authentication required on all endpoints

### Git Commit Format

After each story:
```
FEAT: [Story description]

[Details of implementation]
```

Push after EPIC completion.
