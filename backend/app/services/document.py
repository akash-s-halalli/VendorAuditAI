"""Document service layer for business logic."""

from datetime import datetime, timezone
from typing import Tuple, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document, DocumentStatus, ProcessingStage
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.services.storage import get_storage_backend, generate_storage_path


async def get_document_by_id(
    db: AsyncSession,
    document_id: str,
    org_id: str,
) -> Document | None:
    """Get a single document by ID with organization isolation.

    Args:
        db: Database session
        document_id: Document UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        Document if found, None otherwise
    """
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == org_id,
        )
    )
    return result.scalar_one_or_none()


async def get_documents(
    db: AsyncSession,
    org_id: str,
    skip: int = 0,
    limit: int = 20,
    vendor_id: str | None = None,
    document_type: str | None = None,
    status: str | None = None,
) -> Tuple[List[Document], int]:
    """List documents with pagination and filtering.

    Args:
        db: Database session
        org_id: Organization ID for multi-tenant isolation
        skip: Number of records to skip
        limit: Maximum number of records to return
        vendor_id: Filter by vendor (optional)
        document_type: Filter by document type (optional)
        status: Filter by status (optional)

    Returns:
        Tuple of (list of documents, total count)
    """
    # Base query
    query = select(Document).where(Document.organization_id == org_id)

    # Apply filters
    if vendor_id:
        query = query.where(Document.vendor_id == vendor_id)
    if document_type:
        query = query.where(Document.document_type == document_type)
    if status:
        query = query.where(Document.status == status)

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and ordering (newest first)
    query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)

    # Execute query
    result = await db.execute(query)
    documents = list(result.scalars().all())

    return documents, total


async def create_document(
    db: AsyncSession,
    org_id: str,
    filename: str,
    file_content: bytes,
    mime_type: str,
    document_data: DocumentCreate,
) -> Document:
    """Create a new document record and save file to storage.

    Args:
        db: Database session
        org_id: Organization ID
        filename: Original filename
        file_content: File bytes
        mime_type: MIME type of file
        document_data: Document creation data

    Returns:
        Created document

    Raises:
        ValueError: If file save fails
    """
    # Generate storage path and save file
    storage = get_storage_backend()
    storage_path = generate_storage_path(org_id, filename)

    try:
        await storage.save(file_content, storage_path)
    except Exception as e:
        raise ValueError(f"Failed to save file: {str(e)}")

    # Create document record
    document = Document(
        organization_id=org_id,
        vendor_id=document_data.vendor_id,
        filename=filename,
        storage_path=storage_path,
        file_size=len(file_content),
        mime_type=mime_type,
        document_type=document_data.document_type or "other",
        status=DocumentStatus.PENDING.value,
        processing_stage=ProcessingStage.UPLOADED.value,
    )
    db.add(document)
    await db.flush()
    await db.refresh(document)
    return document


async def update_document(
    db: AsyncSession,
    document_id: str,
    org_id: str,
    document_data: DocumentUpdate,
) -> Document | None:
    """Update a document's metadata.

    Args:
        db: Database session
        document_id: Document UUID
        org_id: Organization ID for multi-tenant isolation
        document_data: Fields to update

    Returns:
        Updated document or None if not found
    """
    document = await get_document_by_id(db, document_id, org_id)
    if not document:
        return None

    # Get update data, excluding unset fields
    update_data = document_data.model_dump(exclude_unset=True)

    # Apply updates
    for field, value in update_data.items():
        setattr(document, field, value)

    await db.flush()
    await db.refresh(document)
    return document


async def update_document_status(
    db: AsyncSession,
    document_id: str,
    org_id: str,
    status: DocumentStatus,
    processing_stage: ProcessingStage | None = None,
    error_message: str | None = None,
    page_count: int | None = None,
) -> Document | None:
    """Update a document's processing status.

    Args:
        db: Database session
        document_id: Document UUID
        org_id: Organization ID
        status: New status
        processing_stage: New processing stage (optional)
        error_message: Error message if failed (optional)
        page_count: Page count if known (optional)

    Returns:
        Updated document or None if not found
    """
    document = await get_document_by_id(db, document_id, org_id)
    if not document:
        return None

    document.status = status.value
    if processing_stage:
        document.processing_stage = processing_stage.value
    if error_message:
        document.error_message = error_message
    if page_count is not None:
        document.page_count = page_count
    if status == DocumentStatus.PROCESSED:
        document.processed_at = datetime.now(timezone.utc)

    await db.flush()
    await db.refresh(document)
    return document


async def delete_document(
    db: AsyncSession,
    document_id: str,
    org_id: str,
) -> bool:
    """Delete a document and its file from storage.

    Args:
        db: Database session
        document_id: Document UUID
        org_id: Organization ID for multi-tenant isolation

    Returns:
        True if deleted, False if not found
    """
    document = await get_document_by_id(db, document_id, org_id)
    if not document:
        return False

    # Delete file from storage
    storage = get_storage_backend()
    try:
        await storage.delete(document.storage_path)
    except Exception:
        # Log but don't fail if storage delete fails
        pass

    await db.delete(document)
    await db.flush()
    return True


async def get_document_content(
    db: AsyncSession,
    document_id: str,
    org_id: str,
) -> Tuple[Document, bytes] | None:
    """Get document record and file content.

    Args:
        db: Database session
        document_id: Document UUID
        org_id: Organization ID

    Returns:
        Tuple of (document, file_bytes) or None if not found
    """
    document = await get_document_by_id(db, document_id, org_id)
    if not document:
        return None

    storage = get_storage_backend()
    try:
        content = await storage.get(document.storage_path)
        return document, content
    except FileNotFoundError:
        return None
