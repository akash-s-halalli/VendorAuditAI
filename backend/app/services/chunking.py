"""Text chunking service for splitting documents into semantic chunks."""

import re
from dataclasses import dataclass, field
from typing import List

import tiktoken


@dataclass
class Chunk:
    """Represents a text chunk with metadata."""

    content: str
    token_count: int
    chunk_index: int
    page_number: int | None = None
    section_header: str | None = None
    metadata: dict = field(default_factory=dict)


class TextChunker:
    """Splits text into semantic chunks suitable for embedding and retrieval.

    Uses a sliding window approach with overlap to maintain context across chunks.
    Attempts to split at natural boundaries (paragraphs, sentences) when possible.
    """

    # Section header patterns for common document formats
    SECTION_PATTERNS = [
        r"^#+\s+(.+)$",  # Markdown headers
        r"^(\d+\.)+\s+(.+)$",  # Numbered sections (1. 1.1 1.1.1)
        r"^[A-Z][A-Z\s]{2,}:?\s*$",  # ALL CAPS headers
        r"^(Section|Chapter|Part)\s+\d+[:.]\s*(.+)$",  # Section X: Title
    ]

    def __init__(
        self,
        target_chunk_size: int = 500,
        max_chunk_size: int = 1000,
        overlap_size: int = 100,
        encoding_name: str = "cl100k_base",
    ):
        """Initialize the text chunker.

        Args:
            target_chunk_size: Target number of tokens per chunk
            max_chunk_size: Maximum tokens per chunk
            overlap_size: Number of tokens to overlap between chunks
            encoding_name: Tiktoken encoding to use for token counting
        """
        self.target_chunk_size = target_chunk_size
        self.max_chunk_size = max_chunk_size
        self.overlap_size = overlap_size
        self.encoding = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count the number of tokens in a text string.

        Args:
            text: Input text

        Returns:
            Number of tokens
        """
        return len(self.encoding.encode(text))

    def chunk_text(
        self,
        text: str,
        page_numbers: List[int] | None = None,
    ) -> List[Chunk]:
        """Split text into semantic chunks.

        Args:
            text: Full text to chunk
            page_numbers: Optional list mapping text positions to page numbers

        Returns:
            List of Chunk objects
        """
        if not text.strip():
            return []

        # Split into paragraphs first
        paragraphs = self._split_into_paragraphs(text)

        chunks = []
        current_chunk_parts = []
        current_tokens = 0
        current_section = None
        chunk_index = 0

        for para in paragraphs:
            para_text = para.strip()
            if not para_text:
                continue

            # Check if this paragraph is a section header
            section_match = self._extract_section_header(para_text)
            if section_match:
                current_section = section_match

            para_tokens = self.count_tokens(para_text)

            # If single paragraph exceeds max, split it by sentences
            if para_tokens > self.max_chunk_size:
                # Flush current chunk first
                if current_chunk_parts:
                    chunk = self._create_chunk(
                        current_chunk_parts,
                        chunk_index,
                        current_section,
                    )
                    chunks.append(chunk)
                    chunk_index += 1
                    current_chunk_parts = []
                    current_tokens = 0

                # Split large paragraph into sentence chunks
                sentence_chunks = self._chunk_by_sentences(para_text, chunk_index)
                for sc in sentence_chunks:
                    sc.section_header = current_section
                chunks.extend(sentence_chunks)
                chunk_index += len(sentence_chunks)
                continue

            # Check if adding this paragraph exceeds target
            if current_tokens + para_tokens > self.target_chunk_size and current_chunk_parts:
                # Create chunk from accumulated parts
                chunk = self._create_chunk(
                    current_chunk_parts,
                    chunk_index,
                    current_section,
                )
                chunks.append(chunk)
                chunk_index += 1

                # Start new chunk with overlap
                overlap_parts = self._get_overlap_parts(current_chunk_parts)
                current_chunk_parts = overlap_parts + [para_text]
                current_tokens = sum(self.count_tokens(p) for p in current_chunk_parts)
            else:
                current_chunk_parts.append(para_text)
                current_tokens += para_tokens

        # Don't forget the last chunk
        if current_chunk_parts:
            chunk = self._create_chunk(
                current_chunk_parts,
                chunk_index,
                current_section,
            )
            chunks.append(chunk)

        return chunks

    def _split_into_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs.

        Args:
            text: Input text

        Returns:
            List of paragraph strings
        """
        # Split on double newlines or more
        paragraphs = re.split(r"\n\s*\n", text)
        return [p.strip() for p in paragraphs if p.strip()]

    def _chunk_by_sentences(self, text: str, start_index: int) -> List[Chunk]:
        """Split a large text block by sentences.

        Args:
            text: Text to split
            start_index: Starting chunk index

        Returns:
            List of Chunk objects
        """
        # Simple sentence splitting (could be improved with nltk/spacy)
        sentences = re.split(r"(?<=[.!?])\s+", text)

        chunks = []
        current_parts = []
        current_tokens = 0
        chunk_index = start_index

        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sent_tokens = self.count_tokens(sentence)

            if current_tokens + sent_tokens > self.target_chunk_size and current_parts:
                chunk = self._create_chunk(current_parts, chunk_index, None)
                chunks.append(chunk)
                chunk_index += 1

                # Start with overlap
                overlap_parts = self._get_overlap_parts(current_parts)
                current_parts = overlap_parts + [sentence]
                current_tokens = sum(self.count_tokens(p) for p in current_parts)
            else:
                current_parts.append(sentence)
                current_tokens += sent_tokens

        if current_parts:
            chunk = self._create_chunk(current_parts, chunk_index, None)
            chunks.append(chunk)

        return chunks

    def _create_chunk(
        self,
        parts: List[str],
        index: int,
        section: str | None,
    ) -> Chunk:
        """Create a Chunk object from text parts.

        Args:
            parts: List of text parts to join
            index: Chunk index
            section: Current section header

        Returns:
            Chunk object
        """
        content = "\n\n".join(parts)
        return Chunk(
            content=content,
            token_count=self.count_tokens(content),
            chunk_index=index,
            section_header=section,
        )

    def _get_overlap_parts(self, parts: List[str]) -> List[str]:
        """Get the trailing parts for overlap.

        Args:
            parts: Current chunk parts

        Returns:
            Parts to include in overlap
        """
        if not parts:
            return []

        overlap_parts = []
        overlap_tokens = 0

        # Work backwards to accumulate overlap
        for part in reversed(parts):
            part_tokens = self.count_tokens(part)
            if overlap_tokens + part_tokens <= self.overlap_size:
                overlap_parts.insert(0, part)
                overlap_tokens += part_tokens
            else:
                break

        return overlap_parts

    def _extract_section_header(self, text: str) -> str | None:
        """Extract section header if text matches a header pattern.

        Args:
            text: Text to check

        Returns:
            Section header string or None
        """
        for pattern in self.SECTION_PATTERNS:
            match = re.match(pattern, text, re.MULTILINE)
            if match:
                # Return the full match, cleaned up
                return text.strip()[:200]  # Limit header length

        return None


# Default chunker instance
default_chunker = TextChunker()


def chunk_document(
    text: str,
    target_size: int = 500,
    max_size: int = 1000,
    overlap: int = 100,
) -> List[Chunk]:
    """Convenience function to chunk a document.

    Args:
        text: Document text
        target_size: Target tokens per chunk
        max_size: Maximum tokens per chunk
        overlap: Overlap tokens between chunks

    Returns:
        List of Chunk objects
    """
    chunker = TextChunker(
        target_chunk_size=target_size,
        max_chunk_size=max_size,
        overlap_size=overlap,
    )
    return chunker.chunk_text(text)
