"""Storage backend service for file management."""

import os
import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol, runtime_checkable

import aiofiles
import aiofiles.os

from app.config import get_settings

settings = get_settings()


@runtime_checkable
class StorageBackend(Protocol):
    """Protocol defining the interface for storage backends."""

    async def save(self, file_content: bytes, path: str) -> str:
        """Save file content to the specified path.

        Args:
            file_content: The file content as bytes.
            path: The storage path for the file.

        Returns:
            The full path where the file was saved.
        """
        ...

    async def get(self, path: str) -> bytes:
        """Retrieve file content from the specified path.

        Args:
            path: The storage path of the file.

        Returns:
            The file content as bytes.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        ...

    async def delete(self, path: str) -> bool:
        """Delete the file at the specified path.

        Args:
            path: The storage path of the file.

        Returns:
            True if the file was deleted, False otherwise.
        """
        ...

    async def exists(self, path: str) -> bool:
        """Check if a file exists at the specified path.

        Args:
            path: The storage path to check.

        Returns:
            True if the file exists, False otherwise.
        """
        ...

    def get_url(self, path: str) -> str | None:
        """Get a public URL for the file.

        Args:
            path: The storage path of the file.

        Returns:
            The public URL or None if not available.
        """
        ...


class StorageBackendBase(ABC):
    """Abstract base class for storage backends."""

    @abstractmethod
    async def save(self, file_content: bytes, path: str) -> str:
        """Save file content to the specified path."""
        pass

    @abstractmethod
    async def get(self, path: str) -> bytes:
        """Retrieve file content from the specified path."""
        pass

    @abstractmethod
    async def delete(self, path: str) -> bool:
        """Delete the file at the specified path."""
        pass

    @abstractmethod
    async def exists(self, path: str) -> bool:
        """Check if a file exists at the specified path."""
        pass

    @abstractmethod
    def get_url(self, path: str) -> str | None:
        """Get a public URL for the file."""
        pass


class LocalStorageBackend(StorageBackendBase):
    """Local filesystem storage backend implementation."""

    def __init__(self, base_path: str | None = None) -> None:
        """Initialize the local storage backend.

        Args:
            base_path: The base directory for file storage.
                      Defaults to settings.local_storage_path.
        """
        self.base_path = Path(base_path or settings.local_storage_path).resolve()

    def _get_full_path(self, path: str) -> Path:
        """Get the full filesystem path for a storage path.

        Args:
            path: The relative storage path.

        Returns:
            The full absolute path.
        """
        # Ensure the path doesn't escape the base directory
        full_path = (self.base_path / path).resolve()
        if not str(full_path).startswith(str(self.base_path)):
            raise ValueError("Invalid path: path traversal detected")
        return full_path

    async def save(self, file_content: bytes, path: str) -> str:
        """Save file content to the local filesystem.

        Args:
            file_content: The file content as bytes.
            path: The storage path for the file.

        Returns:
            The full path where the file was saved.
        """
        full_path = self._get_full_path(path)

        # Create directories if they don't exist
        await aiofiles.os.makedirs(full_path.parent, exist_ok=True)

        # Write the file
        async with aiofiles.open(full_path, "wb") as f:
            await f.write(file_content)

        return str(full_path)

    async def get(self, path: str) -> bytes:
        """Retrieve file content from the local filesystem.

        Args:
            path: The storage path of the file.

        Returns:
            The file content as bytes.

        Raises:
            FileNotFoundError: If the file does not exist.
        """
        full_path = self._get_full_path(path)

        if not await aiofiles.os.path.exists(full_path):
            raise FileNotFoundError(f"File not found: {path}")

        async with aiofiles.open(full_path, "rb") as f:
            return await f.read()

    async def delete(self, path: str) -> bool:
        """Delete the file from the local filesystem.

        Args:
            path: The storage path of the file.

        Returns:
            True if the file was deleted, False if it didn't exist.
        """
        full_path = self._get_full_path(path)

        try:
            if await aiofiles.os.path.exists(full_path):
                await aiofiles.os.remove(full_path)
                return True
            return False
        except OSError:
            return False

    async def exists(self, path: str) -> bool:
        """Check if a file exists in the local filesystem.

        Args:
            path: The storage path to check.

        Returns:
            True if the file exists, False otherwise.
        """
        full_path = self._get_full_path(path)
        return await aiofiles.os.path.exists(full_path)

    def get_url(self, path: str) -> str | None:
        """Get a public URL for the file.

        Local files don't have public URLs.

        Args:
            path: The storage path of the file.

        Returns:
            None (local files don't have public URLs).
        """
        return None


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename by removing unsafe characters.

    Args:
        filename: The original filename.

    Returns:
        A sanitized filename safe for filesystem use.
    """
    # Remove path separators and null bytes
    filename = filename.replace("/", "_").replace("\\", "_").replace("\0", "")

    # Remove or replace unsafe characters, keeping alphanumeric, dots, hyphens, underscores
    sanitized = re.sub(r"[^\w.\-]", "_", filename)

    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")

    # Collapse multiple underscores
    sanitized = re.sub(r"_+", "_", sanitized)

    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"

    # Limit length (preserve extension if present)
    max_length = 255
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        if ext:
            name = name[: max_length - len(ext)]
            sanitized = name + ext
        else:
            sanitized = sanitized[:max_length]

    return sanitized


def generate_storage_path(
    org_id: str,
    filename: str,
    document_id: str | None = None,
) -> str:
    """Generate a storage path for a file.

    Format: {org_id}/{YYYY-MM}/{document_id or uuid}_{sanitized_filename}

    Args:
        org_id: The organization ID.
        filename: The original filename.
        document_id: Optional document ID. If not provided, a UUID is generated.

    Returns:
        The generated storage path.
    """
    # Get current date for year-month directory
    now = datetime.now(timezone.utc)
    year_month = now.strftime("%Y-%m")

    # Use provided document_id or generate a UUID
    file_id = document_id or str(uuid.uuid4())

    # Sanitize the filename
    safe_filename = sanitize_filename(filename)

    # Construct the path
    return f"{org_id}/{year_month}/{file_id}_{safe_filename}"


def get_storage_backend() -> StorageBackendBase:
    """Get the configured storage backend.

    Returns:
        The appropriate storage backend based on settings.storage_backend.

    Raises:
        ValueError: If an unsupported storage backend is configured.
    """
    backend_type = settings.storage_backend.lower()

    if backend_type == "local":
        return LocalStorageBackend()
    elif backend_type == "minio":
        # MinIO support can be added here in the future
        raise NotImplementedError(
            "MinIO storage backend is not yet implemented. "
            "Install with 'pip install vendorauditai-backend[minio]' when available."
        )
    else:
        raise ValueError(f"Unsupported storage backend: {backend_type}")


# Convenience instance for direct import
storage_backend = get_storage_backend()
