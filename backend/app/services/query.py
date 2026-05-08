"""Query service for natural language document Q&A."""

import json
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.query import ConversationThread, QueryHistory, QueryStatus
from app.services.llm import get_llm_service
from app.services.search import SearchResult, get_search_service


@dataclass
class QueryResult:
    """Result from a query operation."""

    answer: str
    confidence: float
    citations: list[dict] = field(default_factory=list)
    limitations: str | None = None
    chunks_retrieved: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class QueryService:
    """Service for handling natural language queries on documents.

    Uses semantic search to find relevant context and Claude to generate
    answers with citations.
    """

    def __init__(self):
        """Initialize the query service."""
        self.search_service = get_search_service()
        self.llm_service = get_llm_service()

    async def ask_question(
        self,
        db: AsyncSession,
        question: str,
        org_id: str,
        user_id: str,
        document_ids: list[str] | None = None,
        conversation_id: str | None = None,
        max_chunks: int = 10,
    ) -> tuple[QueryHistory, QueryResult]:
        """Ask a question about the documents.

        Args:
            db: Database session
            question: The user's question
            org_id: Organization ID for multi-tenant isolation
            user_id: User ID who asked the question
            document_ids: Optional list of document IDs to search within
            conversation_id: Optional conversation for context
            max_chunks: Maximum chunks to retrieve for context

        Returns:
            Tuple of (QueryHistory record, QueryResult)
        """
        start_time = time.time()

        # Create query history record
        query = QueryHistory(
            organization_id=org_id,
            user_id=user_id,
            question=question,
            conversation_id=conversation_id,
            document_ids=json.dumps(document_ids) if document_ids else None,
            status=QueryStatus.PROCESSING.value,
            processing_started_at=datetime.now(UTC),
        )
        db.add(query)
        await db.flush()

        try:
            # Get conversation context if continuing a conversation
            conversation_context = []
            if conversation_id:
                conversation_context = await self._get_conversation_context(
                    db, conversation_id
                )

            # Search for relevant chunks
            search_results = await self.search_service.hybrid_search(
                db=db,
                query=question,
                org_id=org_id,
                document_ids=document_ids,
                limit=max_chunks,
            )

            # Build context from search results
            context_chunks = self._build_context_chunks(search_results)

            # Generate answer using LLM
            result = await self._generate_answer(
                question=question,
                context_chunks=context_chunks,
                conversation_context=conversation_context,
            )

            # Calculate response time
            response_time_ms = int((time.time() - start_time) * 1000)

            # Update query record with results
            query.answer = result.answer
            query.citations = json.dumps(result.citations)
            query.confidence_score = result.confidence
            query.chunks_retrieved = len(search_results)
            query.input_tokens = result.input_tokens
            query.output_tokens = result.output_tokens
            query.response_time_ms = response_time_ms
            query.status = QueryStatus.COMPLETED.value
            query.completed_at = datetime.now(UTC)

            # Update conversation thread if applicable
            if conversation_id:
                await self._update_conversation(
                    db,
                    conversation_id,
                    result.input_tokens + result.output_tokens,
                )

            await db.commit()
            await db.refresh(query)

            return query, result

        except Exception as e:
            query.status = QueryStatus.FAILED.value
            query.error_message = str(e)
            await db.commit()
            raise

    async def create_conversation(
        self,
        db: AsyncSession,
        org_id: str,
        user_id: str,
        title: str | None = None,
        document_ids: list[str] | None = None,
    ) -> ConversationThread:
        """Create a new conversation thread.

        Args:
            db: Database session
            org_id: Organization ID
            user_id: User ID
            title: Optional conversation title
            document_ids: Optional document filter

        Returns:
            Created ConversationThread
        """
        conversation = ConversationThread(
            organization_id=org_id,
            user_id=user_id,
            title=title,
            document_filter=json.dumps(document_ids) if document_ids else None,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)
        return conversation

    async def get_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
        org_id: str,
    ) -> ConversationThread | None:
        """Get a conversation thread by ID.

        Args:
            db: Database session
            conversation_id: Conversation ID
            org_id: Organization ID for multi-tenant check

        Returns:
            ConversationThread or None if not found
        """
        stmt = select(ConversationThread).where(
            ConversationThread.id == conversation_id,
            ConversationThread.organization_id == org_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_query(
        self,
        db: AsyncSession,
        query_id: str,
        org_id: str,
    ) -> QueryHistory | None:
        """Get a query by ID.

        Args:
            db: Database session
            query_id: Query ID
            org_id: Organization ID for multi-tenant check

        Returns:
            QueryHistory or None if not found
        """
        stmt = select(QueryHistory).where(
            QueryHistory.id == query_id,
            QueryHistory.organization_id == org_id,
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_query_history(
        self,
        db: AsyncSession,
        org_id: str,
        user_id: str | None = None,
        conversation_id: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[QueryHistory], int]:
        """Get query history for an organization.

        Args:
            db: Database session
            org_id: Organization ID
            user_id: Optional user filter
            conversation_id: Optional conversation filter
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (queries, total_count)
        """
        # Build base query
        base_query = select(QueryHistory).where(
            QueryHistory.organization_id == org_id
        )

        if user_id:
            base_query = base_query.where(QueryHistory.user_id == user_id)

        if conversation_id:
            base_query = base_query.where(
                QueryHistory.conversation_id == conversation_id
            )

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * limit
        stmt = (
            base_query
            .order_by(QueryHistory.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        queries = list(result.scalars().all())

        return queries, total

    async def get_conversations(
        self,
        db: AsyncSession,
        org_id: str,
        user_id: str | None = None,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[ConversationThread], int]:
        """Get conversation threads for an organization.

        Args:
            db: Database session
            org_id: Organization ID
            user_id: Optional user filter
            page: Page number (1-indexed)
            limit: Items per page

        Returns:
            Tuple of (conversations, total_count)
        """
        base_query = select(ConversationThread).where(
            ConversationThread.organization_id == org_id
        )

        if user_id:
            base_query = base_query.where(ConversationThread.user_id == user_id)

        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Get paginated results
        offset = (page - 1) * limit
        stmt = (
            base_query
            .order_by(ConversationThread.updated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await db.execute(stmt)
        conversations = list(result.scalars().all())

        return conversations, total

    async def _get_conversation_context(
        self,
        db: AsyncSession,
        conversation_id: str,
        max_messages: int = 10,
    ) -> list[dict]:
        """Get recent messages from a conversation for context.

        Args:
            db: Database session
            conversation_id: Conversation ID
            max_messages: Maximum messages to retrieve

        Returns:
            List of message dicts with role and content
        """
        stmt = (
            select(QueryHistory)
            .where(
                QueryHistory.conversation_id == conversation_id,
                QueryHistory.status == QueryStatus.COMPLETED.value,
            )
            .order_by(QueryHistory.created_at.desc())
            .limit(max_messages)
        )
        result = await db.execute(stmt)
        queries = list(result.scalars().all())

        # Reverse to get chronological order
        queries.reverse()

        context = []
        for q in queries:
            context.append({"role": "user", "content": q.question})
            if q.answer:
                context.append({"role": "assistant", "content": q.answer})

        return context

    async def _update_conversation(
        self,
        db: AsyncSession,
        conversation_id: str,
        tokens_used: int,
    ) -> None:
        """Update conversation statistics.

        Args:
            db: Database session
            conversation_id: Conversation ID
            tokens_used: Tokens used in this exchange
        """
        stmt = select(ConversationThread).where(
            ConversationThread.id == conversation_id
        )
        result = await db.execute(stmt)
        conversation = result.scalar_one_or_none()

        if conversation:
            conversation.message_count += 1
            conversation.total_tokens += tokens_used

    def _build_context_chunks(
        self,
        search_results: list[SearchResult],
    ) -> list[dict]:
        """Convert search results to context chunks for LLM.

        Args:
            search_results: List of search results

        Returns:
            List of chunk dicts for LLM context
        """
        chunks = []
        for result in search_results:
            chunk = result.chunk
            chunks.append({
                "content": chunk.content,
                "section_header": chunk.section_header,
                "page_number": chunk.page_number,
                "document_id": result.document_id,
                "document_filename": result.document_filename,
                "chunk_id": chunk.id,
                "relevance_score": result.score,
            })
        return chunks

    async def _generate_answer(
        self,
        question: str,
        context_chunks: list[dict],
        conversation_context: list[dict] | None = None,
    ) -> QueryResult:
        """Generate an answer using the LLM.

        Args:
            question: User's question
            context_chunks: Relevant document chunks
            conversation_context: Previous conversation messages

        Returns:
            QueryResult with answer and metadata
        """
        if not self.llm_service.is_configured:
            return QueryResult(
                answer="LLM service not configured. Please set GEMINI_API_KEY.",
                confidence=0.0,
                citations=[],
                limitations="Service unavailable",
            )

        if not context_chunks:
            return QueryResult(
                answer="I couldn't find any relevant information in the documents to answer your question.",
                confidence=0.0,
                citations=[],
                limitations="No relevant context found",
            )

        # Use the existing answer_query method
        response = await self.llm_service.answer_query(
            query=question,
            context_chunks=context_chunks,
        )

        # Build citations from response
        citations = []
        raw_citations = response.get("citations", [])
        for i, cite in enumerate(raw_citations):
            chunk_index = cite.get("chunk_index", i)
            if chunk_index < len(context_chunks):
                chunk = context_chunks[chunk_index]
                citations.append({
                    "document_id": chunk.get("document_id"),
                    "document_filename": chunk.get("document_filename"),
                    "chunk_id": chunk.get("chunk_id"),
                    "page_number": chunk.get("page_number"),
                    "section_header": chunk.get("section_header"),
                    "excerpt": cite.get("excerpt", ""),
                    "relevance_score": chunk.get("relevance_score", 0.0),
                })

        return QueryResult(
            answer=response.get("answer", "Unable to generate answer."),
            confidence=response.get("confidence", 0.0),
            citations=citations,
            limitations=response.get("limitations"),
            chunks_retrieved=len(context_chunks),
        )


# Default service instance
_query_service: QueryService | None = None


def get_query_service() -> QueryService:
    """Get or create the default query service."""
    global _query_service
    if _query_service is None:
        _query_service = QueryService()
    return _query_service
