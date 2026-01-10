"""Pydantic schemas for document management."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# Define document type literal for reuse
DocumentType = Literal["soc2", "sig_lite", "sig_core", "hecvat", "iso27001", "other"]


class DocumentBase(BaseModel):
    """Base document schema with common fields."""

    filename: str = Field(..., min_length=1, max_length=500)
    document_type: DocumentType | None = None


class DocumentCreate(BaseModel):
    """Schema for creating a new document (metadata only, file handled via UploadFile)."""

    vendor_id: str | None = None
    document_type: DocumentType = "other"


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata (partial updates)."""

    vendor_id: str | None = None
    document_type: DocumentType | None = None


class DocumentResponse(BaseModel):
    """Schema for document response."""

    id: str
    organization_id: str
    vendor_id: str | None = None
    filename: str
    storage_path: str
    file_size: int
    mime_type: str
    document_type: str
    status: str
    processing_stage: str
    page_count: int | None = None
    error_message: str | None = None
    processed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentListResponse(BaseModel):
    """Schema for paginated document list response."""

    data: list[DocumentResponse]
    total: int
    page: int
    limit: int
