"""Semantic search service for document chunks."""

from dataclasses import dataclass

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.chunk import DocumentChunk
from app.models.document import Document
from app.services.embedding import (
    cosine_similarity,
    get_embedding_service,
    json_to_embedding,
)


@dataclass
class SearchResult:
    """Represents a search result with relevance score."""

    chunk: DocumentChunk
    score: float
    document_id: str
    document_filename: str | None = None


class ChunkSearchService:
    """Service for searching document chunks.

    Supports both semantic search (using embeddings) and keyword search.
    Falls back to keyword search if embeddings are not available.
    """

    def __init__(self):
        """Initialize the search service."""
        self.embedding_service = get_embedding_service()

    async def semantic_search(
        self,
        db: AsyncSession,
        query: str,
        org_id: str,
        document_ids: list[str] | None = None,
        limit: int = 10,
        min_score: float = 0.5,
    ) -> list[SearchResult]:
        """Search chunks using semantic similarity.

        Args:
            db: Database session
            query: Search query text
            org_id: Organization ID for multi-tenant isolation
            document_ids: Optional list of document IDs to search within
            limit: Maximum number of results
            min_score: Minimum similarity score (0-1)

        Returns:
            List of SearchResult objects sorted by relevance
        """
        # Generate query embedding
        if not self.embedding_service.is_configured:
            # Fall back to keyword search
            return await self.keyword_search(
                db, query, org_id, document_ids, limit
            )

        try:
            query_embedding = await self.embedding_service.embed_text(query)
        except ValueError:
            # Fall back to keyword search if embedding fails
            return await self.keyword_search(
                db, query, org_id, document_ids, limit
            )

        # Get all chunks with embeddings for the organization
        # Note: This is a simple implementation. For production with many chunks,
        # consider using pgvector for native vector similarity search.
        chunks_with_docs = await self._get_chunks_with_embeddings(
            db, org_id, document_ids
        )

        # Calculate similarities
        results = []
        for chunk, doc_filename in chunks_with_docs:
            if not chunk.embedding:
                continue

            chunk_embedding = json_to_embedding(chunk.embedding)
            score = cosine_similarity(query_embedding, chunk_embedding)

            if score >= min_score:
                results.append(SearchResult(
                    chunk=chunk,
                    score=score,
                    document_id=chunk.document_id,
                    document_filename=doc_filename,
                ))

        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    async def keyword_search(
        self,
        db: AsyncSession,
        query: str,
        org_id: str,
        document_ids: list[str] | None = None,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Search chunks using keyword matching.

        Args:
            db: Database session
            query: Search query text
            org_id: Organization ID for multi-tenant isolation
            document_ids: Optional list of document IDs to search within
            limit: Maximum number of results

        Returns:
            List of SearchResult objects
        """
        # Build query for chunks with their documents
        stmt = (
            select(DocumentChunk, Document.filename)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.organization_id == org_id)
        )

        # Filter by document IDs if specified
        if document_ids:
            stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))

        # Search in content and section headers
        search_terms = query.lower().split()
        search_conditions = []
        for term in search_terms:
            search_conditions.append(
                func.lower(DocumentChunk.content).contains(term)
            )
            search_conditions.append(
                func.lower(DocumentChunk.section_header).contains(term)
            )

        if search_conditions:
            stmt = stmt.where(or_(*search_conditions))

        stmt = stmt.limit(limit * 2)  # Get more for scoring

        result = await db.execute(stmt)
        rows = result.all()

        # Score results based on term frequency
        results = []
        for chunk, doc_filename in rows:
            score = self._calculate_keyword_score(query, chunk.content)
            results.append(SearchResult(
                chunk=chunk,
                score=score,
                document_id=chunk.document_id,
                document_filename=doc_filename,
            ))

        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    async def hybrid_search(
        self,
        db: AsyncSession,
        query: str,
        org_id: str,
        document_ids: list[str] | None = None,
        limit: int = 10,
        semantic_weight: float = 0.7,
    ) -> list[SearchResult]:
        """Combine semantic and keyword search.

        Args:
            db: Database session
            query: Search query text
            org_id: Organization ID
            document_ids: Optional document ID filter
            limit: Maximum results
            semantic_weight: Weight for semantic scores (0-1)

        Returns:
            Combined and re-ranked results
        """
        # Get results from both methods
        semantic_results = await self.semantic_search(
            db, query, org_id, document_ids, limit * 2, min_score=0.3
        )
        keyword_results = await self.keyword_search(
            db, query, org_id, document_ids, limit * 2
        )

        # Combine scores
        chunk_scores: dict[str, tuple[DocumentChunk, float, str | None]] = {}

        for result in semantic_results:
            chunk_scores[result.chunk.id] = (
                result.chunk,
                result.score * semantic_weight,
                result.document_filename,
            )

        keyword_weight = 1 - semantic_weight
        for result in keyword_results:
            if result.chunk.id in chunk_scores:
                chunk, existing_score, filename = chunk_scores[result.chunk.id]
                chunk_scores[result.chunk.id] = (
                    chunk,
                    existing_score + result.score * keyword_weight,
                    filename,
                )
            else:
                chunk_scores[result.chunk.id] = (
                    result.chunk,
                    result.score * keyword_weight,
                    result.document_filename,
                )

        # Convert to results and sort
        results = [
            SearchResult(
                chunk=chunk,
                score=score,
                document_id=chunk.document_id,
                document_filename=filename,
            )
            for chunk, score, filename in chunk_scores.values()
        ]
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:limit]

    async def _get_chunks_with_embeddings(
        self,
        db: AsyncSession,
        org_id: str,
        document_ids: list[str] | None = None,
    ) -> list[tuple[DocumentChunk, str | None]]:
        """Get all chunks with embeddings for an organization.

        Args:
            db: Database session
            org_id: Organization ID
            document_ids: Optional document ID filter

        Returns:
            List of (chunk, filename) tuples
        """
        stmt = (
            select(DocumentChunk, Document.filename)
            .join(Document, DocumentChunk.document_id == Document.id)
            .where(Document.organization_id == org_id)
            .where(DocumentChunk.embedding.is_not(None))
        )

        if document_ids:
            stmt = stmt.where(DocumentChunk.document_id.in_(document_ids))

        result = await db.execute(stmt)
        return list(result.all())

    def _calculate_keyword_score(self, query: str, content: str) -> float:
        """Calculate a simple keyword relevance score.

        Args:
            query: Search query
            content: Chunk content

        Returns:
            Score from 0 to 1
        """
        query_terms = set(query.lower().split())
        content_lower = content.lower()

        if not query_terms:
            return 0.0

        matches = sum(1 for term in query_terms if term in content_lower)
        return matches / len(query_terms)


# Default service instance
_search_service: ChunkSearchService | None = None


def get_search_service() -> ChunkSearchService:
    """Get or create the default search service."""
    global _search_service
    if _search_service is None:
        _search_service = ChunkSearchService()
    return _search_service
