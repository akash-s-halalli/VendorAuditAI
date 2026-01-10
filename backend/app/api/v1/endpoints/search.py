"""Search API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas.chunk import (
    SearchQuery,
    SearchResponse,
    SearchResultResponse,
)
from app.services.search import get_search_service

router = APIRouter(tags=["Search"])


@router.post("", response_model=SearchResponse)
async def search_documents(
    search_query: SearchQuery,
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> SearchResponse:
    """
    Search across document chunks using semantic or keyword matching.

    Supports three search types:
    - semantic: Uses vector embeddings for similarity search
    - keyword: Uses text matching
    - hybrid: Combines both approaches (recommended)
    """
    search_service = get_search_service()

    # Perform search based on type
    if search_query.search_type == "semantic":
        results = await search_service.semantic_search(
            db=db,
            query=search_query.query,
            org_id=current_user.organization_id,
            document_ids=search_query.document_ids,
            limit=search_query.limit,
            min_score=search_query.min_score,
        )
    elif search_query.search_type == "keyword":
        results = await search_service.keyword_search(
            db=db,
            query=search_query.query,
            org_id=current_user.organization_id,
            document_ids=search_query.document_ids,
            limit=search_query.limit,
        )
    else:  # hybrid (default)
        results = await search_service.hybrid_search(
            db=db,
            query=search_query.query,
            org_id=current_user.organization_id,
            document_ids=search_query.document_ids,
            limit=search_query.limit,
        )

    # Convert to response format
    response_results = [
        SearchResultResponse(
            chunk_id=r.chunk.id,
            document_id=r.document_id,
            document_filename=r.document_filename,
            content=r.chunk.content,
            section_header=r.chunk.section_header,
            page_number=r.chunk.page_number,
            score=r.score,
            chunk_index=r.chunk.chunk_index,
        )
        for r in results
    ]

    return SearchResponse(
        results=response_results,
        query=search_query.query,
        total_results=len(response_results),
    )


@router.get("/quick", response_model=SearchResponse)
async def quick_search(
    q: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
    current_user: Annotated[User, Depends(get_current_active_user)] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
) -> SearchResponse:
    """
    Quick search endpoint using hybrid search with defaults.

    Use POST /search for more control over search parameters.
    """
    search_service = get_search_service()

    results = await search_service.hybrid_search(
        db=db,
        query=q,
        org_id=current_user.organization_id,
        limit=limit,
    )

    response_results = [
        SearchResultResponse(
            chunk_id=r.chunk.id,
            document_id=r.document_id,
            document_filename=r.document_filename,
            content=r.chunk.content,
            section_header=r.chunk.section_header,
            page_number=r.chunk.page_number,
            score=r.score,
            chunk_index=r.chunk.chunk_index,
        )
        for r in results
    ]

    return SearchResponse(
        results=response_results,
        query=q,
        total_results=len(response_results),
    )
