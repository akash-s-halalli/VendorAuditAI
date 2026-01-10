"""Pydantic schemas for natural language queries."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

QueryStatusType = Literal["pending", "processing", "completed", "failed"]


class Citation(BaseModel):
    """Citation from a source document."""

    document_id: str
    document_filename: str | None = None
    chunk_id: str | None = None
    page_number: int | None = None
    section_header: str | None = None
    excerpt: str = Field(..., description="Relevant excerpt from the document")
    relevance_score: float = Field(ge=0.0, le=1.0, default=0.0)


class QueryRequest(BaseModel):
    """Request to ask a question."""

    question: str = Field(
        ..., min_length=3, max_length=2000, description="The question to ask"
    )
    document_ids: list[str] | None = Field(
        None, description="Optional list of document IDs to search within"
    )
    conversation_id: str | None = Field(
        None, description="Optional conversation ID for follow-up questions"
    )
    max_chunks: int = Field(
        10, ge=1, le=50, description="Maximum context chunks to retrieve"
    )


class QueryResponse(BaseModel):
    """Response to a query."""

    model_config = ConfigDict(from_attributes=True)

    query_id: str
    question: str
    answer: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    citations: list[Citation]
    limitations: str | None = None
    conversation_id: str | None = None
    chunks_retrieved: int
    response_time_ms: int


class ConversationMessage(BaseModel):
    """A message in a conversation thread."""

    role: Literal["user", "assistant"]
    content: str
    timestamp: datetime
    citations: list[Citation] | None = None


class ConversationRequest(BaseModel):
    """Request to continue a conversation."""

    conversation_id: str = Field(..., description="The conversation to continue")
    question: str = Field(
        ..., min_length=3, max_length=2000, description="The follow-up question"
    )
    max_chunks: int = Field(
        10, ge=1, le=50, description="Maximum context chunks to retrieve"
    )


class ConversationResponse(BaseModel):
    """Response with full conversation context."""

    conversation_id: str
    title: str | None = None
    messages: list[ConversationMessage]
    document_filter: list[str] | None = None
    total_tokens: int
    created_at: datetime


class ConversationCreateRequest(BaseModel):
    """Request to create a new conversation."""

    title: str | None = Field(None, max_length=255)
    document_ids: list[str] | None = Field(
        None, description="Documents to scope this conversation to"
    )
    initial_question: str = Field(
        ..., min_length=3, max_length=2000, description="The first question"
    )


class QueryHistoryResponse(BaseModel):
    """Response model for query history entry."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    question: str
    answer: str | None = None
    status: QueryStatusType
    confidence_score: float | None = None
    chunks_retrieved: int
    input_tokens: int
    output_tokens: int
    response_time_ms: int | None = None
    conversation_id: str | None = None
    created_at: datetime


class QueryHistoryListResponse(BaseModel):
    """Paginated list of query history."""

    data: list[QueryHistoryResponse]
    total: int
    page: int
    limit: int


class ConversationListResponse(BaseModel):
    """Paginated list of conversations."""

    data: list[ConversationResponse]
    total: int
    page: int
    limit: int
