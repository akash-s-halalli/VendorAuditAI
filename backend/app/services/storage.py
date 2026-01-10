"""Storage backend service for file management."""

import asyncio
import io
import logging
import os
import re
import uuid
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from functools import partial
from pathlib import Path
from typing import Protocol, runtime_checkable

import aiofiles
import aiofiles.os

from app.config import get_settings

logger = logging.getLogger(__name__)

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


class MinIOStorageBackend(StorageBackendBase):
    """MinIO object storage backend implementation.

    This backend uses the MinIO Python SDK to interact with MinIO or
    any S3-compatible object storage service.
    """

    # Thread pool for running sync MinIO operations
    _executor: ThreadPoolExecutor | None = None

    def __init__(
        self,
        endpoint: str | None = None,
        access_key: str | None = None,
        secret_key: str | None = None,
        bucket_name: str | None = None,
        secure: bool | None = None,
    ) -> None:
        """Initialize the MinIO storage backend.

        Args:
            endpoint: MinIO server endpoint (e.g., "localhost:9000").
                     Defaults to settings.minio_endpoint.
            access_key: MinIO access key. Defaults to settings.minio_access_key.
            secret_key: MinIO secret key. Defaults to settings.minio_secret_key.
            bucket_name: Bucket name for storing files. Defaults to settings.minio_bucket.
            secure: Use HTTPS connection. Defaults to settings.minio_secure.

        Raises:
            ImportError: If the minio package is not installed.
            ValueError: If required configuration is missing.
        """
        try:
            from minio import Minio
            from minio.error import S3Error

            self._S3Error = S3Error
        except ImportError as e:
            raise ImportError(
                "MinIO package is not installed. "
                "Install with 'pip install vendorauditai-backend[minio]' or 'pip install minio'"
            ) from e

        # Get configuration from settings or parameters
        self.endpoint = endpoint or settings.minio_endpoint
        self.access_key = access_key or settings.minio_access_key
        self.secret_key = secret_key or settings.minio_secret_key
        self.bucket_name = bucket_name or settings.minio_bucket
        self.secure = secure if secure is not None else settings.minio_secure

        # Validate required configuration
        if not self.endpoint:
            raise ValueError(
                "MinIO endpoint is required. Set MINIO_ENDPOINT environment variable."
            )
        if not self.access_key:
            raise ValueError(
                "MinIO access key is required. Set MINIO_ACCESS_KEY environment variable."
            )
        if not self.secret_key:
            raise ValueError(
                "MinIO secret key is required. Set MINIO_SECRET_KEY environment variable."
            )

        # Initialize MinIO client
        self._client = Minio(
            self.endpoint,
            access_key=self.access_key,
            secret_key=self.secret_key,
            secure=self.secure,
        )

        # Initialize thread pool executor for async operations
        if MinIOStorageBackend._executor is None:
            MinIOStorageBackend._executor = ThreadPoolExecutor(
                max_workers=4, thread_name_prefix="minio-"
            )

        # Ensure bucket exists (done synchronously during initialization)
        self._ensure_bucket_exists()

    def _ensure_bucket_exists(self) -> None:
        """Ensure the storage bucket exists, creating it if necessary."""
        try:
            if not self._client.bucket_exists(self.bucket_name):
                self._client.make_bucket(self.bucket_name)
                logger.info(f"Created MinIO bucket: {self.bucket_name}")
        except self._S3Error as e:
            logger.error(f"Failed to ensure bucket exists: {e}")
            raise RuntimeError(f"Failed to initialize MinIO bucket: {e}") from e

    async def _run_in_executor(self, func, *args, **kwargs):
        """Run a synchronous function in the thread pool executor.

        Args:
            func: The synchronous function to run.
            *args: Positional arguments for the function.
            **kwargs: Keyword arguments for the function.

        Returns:
            The result of the function.
        """
        loop = asyncio.get_event_loop()
        if kwargs:
            func = partial(func, **kwargs)
        return await loop.run_in_executor(self._executor, func, *args)

    async def save(self, file_content: bytes, path: str) -> str:
        """Save file content to MinIO.

        Args:
            file_content: The file content as bytes.
            path: The object path (key) in the bucket.

        Returns:
            The full path (object key) where the file was saved.

        Raises:
            RuntimeError: If the upload fails.
        """
        try:
            # Create a BytesIO stream from the content
            data = io.BytesIO(file_content)
            content_length = len(file_content)

            # Determine content type (default to binary)
            content_type = "application/octet-stream"

            # Try to determine content type from file extension
            ext = os.path.splitext(path)[1].lower()
            content_type_map = {
                ".pdf": "application/pdf",
                ".doc": "application/msword",
                ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                ".xls": "application/vnd.ms-excel",
                ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                ".txt": "text/plain",
                ".json": "application/json",
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
            }
            content_type = content_type_map.get(ext, content_type)

            # Upload the object
            await self._run_in_executor(
                self._client.put_object,
                self.bucket_name,
                path,
                data,
                content_length,
                content_type=content_type,
            )

            logger.debug(f"Saved file to MinIO: {path}")
            return path

        except self._S3Error as e:
            logger.error(f"Failed to save file to MinIO: {e}")
            raise RuntimeError(f"Failed to save file to MinIO: {e}") from e

    async def get(self, path: str) -> bytes:
        """Retrieve file content from MinIO.

        Args:
            path: The object path (key) in the bucket.

        Returns:
            The file content as bytes.

        Raises:
            FileNotFoundError: If the object does not exist.
            RuntimeError: If the download fails.
        """
        try:
            response = await self._run_in_executor(
                self._client.get_object,
                self.bucket_name,
                path,
            )
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()

        except self._S3Error as e:
            if e.code == "NoSuchKey":
                raise FileNotFoundError(f"File not found: {path}") from e
            logger.error(f"Failed to get file from MinIO: {e}")
            raise RuntimeError(f"Failed to get file from MinIO: {e}") from e

    async def delete(self, path: str) -> bool:
        """Delete the object from MinIO.

        Args:
            path: The object path (key) in the bucket.

        Returns:
            True if the object was deleted, False if it didn't exist.
        """
        try:
            # Check if object exists first
            if not await self.exists(path):
                return False

            await self._run_in_executor(
                self._client.remove_object,
                self.bucket_name,
                path,
            )
            logger.debug(f"Deleted file from MinIO: {path}")
            return True

        except self._S3Error as e:
            logger.error(f"Failed to delete file from MinIO: {e}")
            return False

    async def exists(self, path: str) -> bool:
        """Check if an object exists in MinIO.

        Args:
            path: The object path (key) to check.

        Returns:
            True if the object exists, False otherwise.
        """
        try:
            await self._run_in_executor(
                self._client.stat_object,
                self.bucket_name,
                path,
            )
            return True
        except self._S3Error as e:
            if e.code == "NoSuchKey":
                return False
            # Log other errors but return False
            logger.warning(f"Error checking if object exists in MinIO: {e}")
            return False

    def get_url(self, path: str, expires: timedelta | None = None) -> str | None:
        """Get a presigned URL for the object.

        Args:
            path: The object path (key) in the bucket.
            expires: URL expiration time. Defaults to 1 hour.

        Returns:
            A presigned URL for downloading the object, or None on error.
        """
        try:
            if expires is None:
                expires = timedelta(hours=1)

            url = self._client.presigned_get_object(
                self.bucket_name,
                path,
                expires=expires,
            )
            return url

        except self._S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
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
    now = datetime.now(UTC)
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
        ImportError: If the required package for the backend is not installed.
    """
    backend_type = settings.storage_backend.lower()

    if backend_type == "local":
        return LocalStorageBackend()
    elif backend_type == "minio":
        return MinIOStorageBackend()
    else:
        raise ValueError(f"Unsupported storage backend: {backend_type}")


# Convenience instance for direct import
storage_backend = get_storage_backend()
