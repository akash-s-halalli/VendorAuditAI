"""Query API endpoints for natural language document Q&A."""

import json
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.query import (
    QueryRequest,
    QueryResponse,
    ConversationRequest,
    ConversationResponse,
    ConversationCreateRequest,
    ConversationMessage,
    QueryHistoryResponse,
    QueryHistoryListResponse,
    ConversationListResponse,
    Citation,
)
from app.services.query import get_query_service

router = APIRouter()


@router.post(
    "",
    response_model=QueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask a question",
    description="Ask a natural language question about your documents",
)
async def ask_question(
    request: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryResponse:
    """Submit a natural language question about documents.

    The system will:
    1. Search for relevant document chunks
    2. Generate an answer using AI with citations
    3. Store the query in history
    """
    query_service = get_query_service()

    query, result = await query_service.ask_question(
        db=db,
        question=request.question,
        org_id=current_user.organization_id,
        user_id=current_user.id,
        document_ids=request.document_ids,
        conversation_id=request.conversation_id,
        max_chunks=request.max_chunks,
    )

    # Convert citations to schema format
    citations = [
        Citation(**cite) for cite in result.citations
    ]

    return QueryResponse(
        query_id=query.id,
        question=query.question,
        answer=result.answer,
        confidence_score=result.confidence,
        citations=citations,
        limitations=result.limitations,
        conversation_id=query.conversation_id,
        chunks_retrieved=result.chunks_retrieved,
        response_time_ms=query.response_time_ms or 0,
    )


@router.post(
    "/conversation",
    response_model=ConversationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a conversation",
    description="Create a new conversation thread with an initial question",
)
async def create_conversation(
    request: ConversationCreateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationResponse:
    """Start a new conversation thread.

    Creates a conversation and asks the initial question.
    """
    query_service = get_query_service()

    # Create the conversation
    conversation = await query_service.create_conversation(
        db=db,
        org_id=current_user.organization_id,
        user_id=current_user.id,
        title=request.title,
        document_ids=request.document_ids,
    )

    # Ask the initial question
    query, result = await query_service.ask_question(
        db=db,
        question=request.initial_question,
        org_id=current_user.organization_id,
        user_id=current_user.id,
        document_ids=request.document_ids,
        conversation_id=conversation.id,
    )

    # Build messages list
    messages = [
        ConversationMessage(
            role="user",
            content=request.initial_question,
            timestamp=query.created_at,
        ),
        ConversationMessage(
            role="assistant",
            content=result.answer,
            timestamp=query.completed_at or query.created_at,
            citations=[Citation(**cite) for cite in result.citations],
        ),
    ]

    # Parse document filter
    doc_filter = None
    if conversation.document_filter:
        doc_filter = json.loads(conversation.document_filter)

    return ConversationResponse(
        conversation_id=conversation.id,
        title=conversation.title,
        messages=messages,
        document_filter=doc_filter,
        total_tokens=conversation.total_tokens,
        created_at=conversation.created_at,
    )


@router.post(
    "/conversation/{conversation_id}",
    response_model=QueryResponse,
    summary="Continue conversation",
    description="Ask a follow-up question in an existing conversation",
)
async def continue_conversation(
    conversation_id: str,
    request: ConversationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryResponse:
    """Continue an existing conversation with a follow-up question."""
    query_service = get_query_service()

    # Verify conversation exists and belongs to user's org
    conversation = await query_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
        org_id=current_user.organization_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Get document filter from conversation
    document_ids = None
    if conversation.document_filter:
        document_ids = json.loads(conversation.document_filter)

    # Ask the question
    query, result = await query_service.ask_question(
        db=db,
        question=request.question,
        org_id=current_user.organization_id,
        user_id=current_user.id,
        document_ids=document_ids,
        conversation_id=conversation_id,
        max_chunks=request.max_chunks,
    )

    citations = [Citation(**cite) for cite in result.citations]

    return QueryResponse(
        query_id=query.id,
        question=query.question,
        answer=result.answer,
        confidence_score=result.confidence,
        citations=citations,
        limitations=result.limitations,
        conversation_id=conversation_id,
        chunks_retrieved=result.chunks_retrieved,
        response_time_ms=query.response_time_ms or 0,
    )


@router.get(
    "/conversation/{conversation_id}",
    response_model=ConversationResponse,
    summary="Get conversation",
    description="Get full conversation history",
)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationResponse:
    """Get a conversation with all its messages."""
    query_service = get_query_service()

    conversation = await query_service.get_conversation(
        db=db,
        conversation_id=conversation_id,
        org_id=current_user.organization_id,
    )

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Get all queries in this conversation
    queries, _ = await query_service.get_query_history(
        db=db,
        org_id=current_user.organization_id,
        conversation_id=conversation_id,
        limit=100,
    )

    # Build messages
    messages = []
    for q in queries:
        messages.append(
            ConversationMessage(
                role="user",
                content=q.question,
                timestamp=q.created_at,
            )
        )
        if q.answer:
            citations = []
            if q.citations:
                try:
                    cite_data = json.loads(q.citations)
                    citations = [Citation(**c) for c in cite_data]
                except (json.JSONDecodeError, TypeError):
                    pass

            messages.append(
                ConversationMessage(
                    role="assistant",
                    content=q.answer,
                    timestamp=q.completed_at or q.created_at,
                    citations=citations if citations else None,
                )
            )

    # Parse document filter
    doc_filter = None
    if conversation.document_filter:
        doc_filter = json.loads(conversation.document_filter)

    return ConversationResponse(
        conversation_id=conversation.id,
        title=conversation.title,
        messages=messages,
        document_filter=doc_filter,
        total_tokens=conversation.total_tokens,
        created_at=conversation.created_at,
    )


@router.get(
    "/history",
    response_model=QueryHistoryListResponse,
    summary="Get query history",
    description="Get paginated query history",
)
async def get_query_history(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    conversation_id: str | None = Query(None, description="Filter by conversation"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryHistoryListResponse:
    """Get query history for the current user's organization."""
    query_service = get_query_service()

    queries, total = await query_service.get_query_history(
        db=db,
        org_id=current_user.organization_id,
        conversation_id=conversation_id,
        page=page,
        limit=limit,
    )

    return QueryHistoryListResponse(
        data=[QueryHistoryResponse.model_validate(q) for q in queries],
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List conversations",
    description="Get paginated list of conversations",
)
async def list_conversations(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ConversationListResponse:
    """List all conversations for the current user's organization."""
    query_service = get_query_service()

    conversations, total = await query_service.get_conversations(
        db=db,
        org_id=current_user.organization_id,
        page=page,
        limit=limit,
    )

    # Build response with minimal messages (just metadata)
    data = []
    for conv in conversations:
        doc_filter = None
        if conv.document_filter:
            doc_filter = json.loads(conv.document_filter)

        data.append(
            ConversationResponse(
                conversation_id=conv.id,
                title=conv.title,
                messages=[],  # Empty for list view
                document_filter=doc_filter,
                total_tokens=conv.total_tokens,
                created_at=conv.created_at,
            )
        )

    return ConversationListResponse(
        data=data,
        total=total,
        page=page,
        limit=limit,
    )


@router.get(
    "/{query_id}",
    response_model=QueryHistoryResponse,
    summary="Get query details",
    description="Get details of a specific query",
)
async def get_query(
    query_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryHistoryResponse:
    """Get details of a specific query by ID."""
    query_service = get_query_service()

    query = await query_service.get_query(
        db=db,
        query_id=query_id,
        org_id=current_user.organization_id,
    )

    if not query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Query not found",
        )

    return QueryHistoryResponse.model_validate(query)
