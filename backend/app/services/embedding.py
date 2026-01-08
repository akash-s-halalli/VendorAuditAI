"""Embedding service for generating vector representations of text."""

import json
from typing import List

from openai import AsyncOpenAI

from app.config import get_settings


class EmbeddingService:
    """Service for generating text embeddings using OpenAI.

    Uses the text-embedding-3-large model by default for high-quality
    semantic representations suitable for RAG retrieval.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        dimensions: int | None = None,
    ):
        """Initialize the embedding service.

        Args:
            api_key: OpenAI API key (uses settings if not provided)
            model: Model name (uses settings if not provided)
            dimensions: Embedding dimensions (uses settings if not provided)
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.embedding_model
        self.dimensions = dimensions or settings.embedding_dimensions

        if not self.api_key:
            self._client = None
        else:
            self._client = AsyncOpenAI(api_key=self.api_key)

    @property
    def is_configured(self) -> bool:
        """Check if the service has valid API credentials."""
        return self._client is not None

    async def embed_text(self, text: str) -> List[float]:
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
                dimensions=self.dimensions,
            )
            return response.data[0].embedding
        except Exception as e:
            raise ValueError(f"Failed to generate embedding: {str(e)}")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
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
                dimensions=self.dimensions,
            )
            # Sort by index to maintain order
            sorted_data = sorted(response.data, key=lambda x: x.index)
            return [item.embedding for item in sorted_data]
        except Exception as e:
            raise ValueError(f"Failed to generate embeddings: {str(e)}")

    async def embed_chunks_batch(
        self,
        texts: List[str],
        batch_size: int = 100,
    ) -> List[List[float]]:
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


def embedding_to_json(embedding: List[float]) -> str:
    """Convert embedding to JSON string for storage.

    Args:
        embedding: List of float values

    Returns:
        JSON string representation
    """
    return json.dumps(embedding)


def json_to_embedding(json_str: str) -> List[float]:
    """Parse embedding from JSON string.

    Args:
        json_str: JSON string representation

    Returns:
        List of float values
    """
    return json.loads(json_str)


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.

    Args:
        vec1: First embedding vector
        vec2: Second embedding vector

    Returns:
        Cosine similarity score (0-1, higher is more similar)
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same dimensions")

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = sum(a * a for a in vec1) ** 0.5
    norm2 = sum(b * b for b in vec2) ** 0.5

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


# Default service instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create the default embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
