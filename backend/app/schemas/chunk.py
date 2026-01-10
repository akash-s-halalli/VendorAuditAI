"""Pydantic schemas for document chunks."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ChunkResponse(BaseModel):
    """Response model for a document chunk."""

    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    content: str
    token_count: int
    chunk_index: int
    page_number: int | None = None
    section_header: str | None = None
    has_embedding: bool = False
    created_at: datetime
    updated_at: datetime


class ChunkListResponse(BaseModel):
    """Paginated list of chunks."""

    data: list[ChunkResponse]
    total: int
    page: int
    limit: int


class SearchQuery(BaseModel):
    """Search query parameters."""

    query: str = Field(..., min_length=1, max_length=1000, description="Search query text")
    document_ids: list[str] | None = Field(None, description="Optional document IDs to search within")
    limit: int = Field(10, ge=1, le=50, description="Maximum number of results")
    min_score: float = Field(0.5, ge=0.0, le=1.0, description="Minimum relevance score")
    search_type: str = Field("hybrid", description="Search type: semantic, keyword, or hybrid")


class SearchResultResponse(BaseModel):
    """Response model for a search result."""

    chunk_id: str
    document_id: str
    document_filename: str | None
    content: str
    section_header: str | None
    page_number: int | None
    score: float
    chunk_index: int


class SearchResponse(BaseModel):
    """Search results response."""

    results: list[SearchResultResponse]
    query: str
    total_results: int
