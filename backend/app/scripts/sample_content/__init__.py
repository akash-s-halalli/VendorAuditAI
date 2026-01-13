"""Sample document content for demo data seeding.

This module provides realistic compliance document content that can be
chunked and used for analysis, query, and other AI features.
"""

from app.scripts.sample_content.soc2 import SOC2_CONTENT
from app.scripts.sample_content.iso27001 import ISO27001_CONTENT
from app.scripts.sample_content.pentest import PENTEST_CONTENT
from app.scripts.sample_content.sig import SIG_CONTENT


def get_document_content(doc_type: str, vendor_name: str = "Vendor") -> list[dict]:
    """Get document content based on document type.

    Args:
        doc_type: Type of document (soc2, iso27001, pentest, sig_core, sig_lite)
        vendor_name: Name of the vendor to personalize content

    Returns:
        List of dicts with 'content', 'section_header', and 'page_number'
    """
    content_map = {
        "soc2": SOC2_CONTENT,
        "iso27001": ISO27001_CONTENT,
        "pentest": PENTEST_CONTENT,
        "sig_core": SIG_CONTENT,
        "sig_lite": SIG_CONTENT,  # Same structure, just shorter
    }

    base_content = content_map.get(doc_type, SOC2_CONTENT)

    # Personalize content with vendor name
    result = []
    for item in base_content:
        personalized = {
            "content": item["content"].replace("{VENDOR}", vendor_name),
            "section_header": item["section_header"],
            "page_number": item["page_number"],
        }
        result.append(personalized)

    return result


def chunk_content(content: str, target_size: int = 500) -> list[str]:
    """Split content into chunks of approximately target_size words.

    Args:
        content: Text content to chunk
        target_size: Target number of words per chunk

    Returns:
        List of text chunks
    """
    words = content.split()
    chunks = []
    current_chunk = []
    current_size = 0

    for word in words:
        current_chunk.append(word)
        current_size += 1

        if current_size >= target_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


__all__ = [
    "get_document_content",
    "chunk_content",
    "SOC2_CONTENT",
    "ISO27001_CONTENT",
    "PENTEST_CONTENT",
    "SIG_CONTENT",
]
