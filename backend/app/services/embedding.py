"""Embedding service for generating vector representations of text.

Supports multiple embedding providers:
- OpenAI (text-embedding-3-large, 3072 dimensions by default)
- Google Gemini (text-embedding-004, 768 dimensions by default)
"""

import json
from abc import ABC, abstractmethod

from openai import AsyncOpenAI

from app.config import get_settings


class BaseEmbeddingService(ABC):
    """Abstract base class for embedding services.

    Defines the interface that all embedding providers must implement.
    """

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if the service has valid API credentials."""
        pass

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return the embedding dimensions for this provider."""
        pass

    @abstractmethod
    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of float values representing the embedding

        Raises:
            ValueError: If service is not configured or API call fails
        """
        pass

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (one per input text)

        Raises:
            ValueError: If service is not configured or API call fails
        """
        pass

    async def embed_chunks_batch(
        self,
        texts: list[str],
        batch_size: int = 100,
    ) -> list[list[float]]:
        """Generate embeddings for many texts in batches.

        Handles large numbers of texts by processing in batches
        to avoid API rate limits and payload size limits.

        Args:
            texts: List of texts to embed
            batch_size: Number of texts per API call

        Returns:
            List of embeddings (one per input text)
        """
        if not texts:
            return []

        all_embeddings = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = await self.embed_texts(batch)
            all_embeddings.extend(batch_embeddings)

        return all_embeddings


class OpenAIEmbeddingService(BaseEmbeddingService):
    """Embedding service using OpenAI's text-embedding models.

    Uses the text-embedding-3-large model by default for high-quality
    semantic representations suitable for RAG retrieval.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        dimensions: int | None = None,
    ):
        """Initialize the OpenAI embedding service.

        Args:
            api_key: OpenAI API key (uses settings if not provided)
            model: Model name (uses settings if not provided)
            dimensions: Embedding dimensions (uses settings if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.embedding_model
        self._dimensions = dimensions or settings.embedding_dimensions

        if not self.api_key:
            self._client = None
        else:
            self._client = AsyncOpenAI(api_key=self.api_key)

    @property
    def is_configured(self) -> bool:
        """Check if the service has valid API credentials."""
        return self._client is not None

    @property
    def dimensions(self) -> int:
        """Return the embedding dimensions."""
        return self._dimensions

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of float values representing the embedding

        Raises:
            ValueError: If service is not configured or API call fails
        """
        if not self.is_configured:
            raise ValueError("OpenAI API key not configured")

        try:
            response = await self._client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self._dimensions,
            )
            return response.data[0].embedding
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {e!s}") from e

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (one per input text)

        Raises:
            ValueError: If service is not configured or API call fails
        """
        if not self.is_configured:
            raise ValueError("OpenAI API key not configured")

        if not texts:
            return []

        try:
            response = await self._client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self._dimensions,
            )
            # Sort by index to maintain order
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            raise ValueError(f"Failed to generate embeddings: {e!s}") from e


class GeminiEmbeddingService(BaseEmbeddingService):
    """Embedding service using Google Gemini's text-embedding models.

    Uses the text-embedding-004 model by default, which produces
    768-dimensional embeddings suitable for semantic search.
    """

    # Default dimensions for Gemini text-embedding-004
    DEFAULT_DIMENSIONS = 768

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ):
        """Initialize the Gemini embedding service.

        Args:
            api_key: Google API key (uses settings if not provided)
            model: Model name (uses settings if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.google_api_key
        self.model = model or settings.gemini_embedding_model
        self._dimensions = self.DEFAULT_DIMENSIONS

        self._client = None
        if self.api_key:
            try:
                from google import genai

                self._client = genai.Client(api_key=self.api_key)
            except ImportError:
                # google-genai not installed
                pass

    @property
    def is_configured(self) -> bool:
        """Check if the service has valid API credentials."""
        return self._client is not None

    @property
    def dimensions(self) -> int:
        """Return the embedding dimensions (768 for Gemini)."""
        return self._dimensions

    async def embed_text(self, text: str) -> list[float]:
        """Generate embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            List of float values representing the embedding

        Raises:
            ValueError: If service is not configured or API call fails
        """
        if not self.is_configured:
            raise ValueError("Google API key not configured or google-genai not installed")

        try:
            # google-genai uses synchronous API, run in executor for async context
            import asyncio

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._client.models.embed_content(
                    model=self.model,
                    contents=text,
                ),
            )
            return list(result.embeddings[0].values)
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {e!s}") from e

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in a batch.

        Args:
            texts: List of texts to embed

        Returns:
            List of embeddings (one per input text)

        Raises:
            ValueError: If service is not configured or API call fails
        """
        if not self.is_configured:
            raise ValueError("Google API key not configured or google-genai not installed")

        if not texts:
            return []

        try:
            import asyncio

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._client.models.embed_content(
                    model=self.model,
                    contents=texts,
                ),
            )
            return [list(emb.values) for emb in result.embeddings]
        except Exception as e:
            raise ValueError(f"Failed to generate embeddings: {e!s}") from e


# Backwards compatibility alias
class EmbeddingService(OpenAIEmbeddingService):
    """Alias for OpenAIEmbeddingService for backwards compatibility.

    New code should use get_embedding_service() factory function instead,
    which respects the embedding_provider setting.
    """

    pass


def create_embedding_service(
    provider: str | None = None,
) -> BaseEmbeddingService:
    """Factory function to create the appropriate embedding service.

    Args:
        provider: Provider name ("openai" or "gemini"). Uses settings if not provided.

    Returns:
        Configured embedding service instance

    Raises:
        ValueError: If provider is not supported
    """
    settings = get_settings()
    provider = provider or settings.embedding_provider

    if provider == "openai":
        return OpenAIEmbeddingService()
    elif provider == "gemini":
        return GeminiEmbeddingService()
    else:
        raise ValueError(f"Unsupported embedding provider: {provider}")


def embedding_to_json(embedding: list[float]) -> str:
    """Convert embedding to JSON string for storage.

    Args:
        embedding: List of float values

    Returns:
        JSON string representation
    """
    return json.dumps(embedding)


def json_to_embedding(json_str: str) -> list[float]:
    """Parse embedding from JSON string.

    Args:
        json_str: JSON string representation

    Returns:
        List of float values
    """
    return json.loads(json_str)


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score (0-1, higher is more similar)
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same dimensions")

    dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=True))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


# Default service instance (cached)
_embedding_service: BaseEmbeddingService | None = None


def get_embedding_service() -> BaseEmbeddingService:
    """Get or create the default embedding service.

    Uses the embedding_provider setting to determine which provider to use.
    The service is cached for reuse across calls.

    Returns:
        Configured embedding service instance
    """
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = create_embedding_service()
    return _embedding_service


def reset_embedding_service() -> None:
    """Reset the cached embedding service.

    Useful for testing or when settings change at runtime.
    """
    global _embedding_service
    _embedding_service = None
