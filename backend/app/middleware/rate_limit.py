"""Rate limiting middleware using SlowAPI.

This module provides rate limiting functionality for the VendorAuditAI API
using SlowAPI with Redis fallback to in-memory storage.

Rate Limits by Endpoint Type:
    - Auth endpoints (/auth/login, /auth/register): 5/minute (prevent brute force)
    - Analysis/LLM endpoints (/analysis/run): 10/hour (expensive operations)
    - Export endpoints (/export/*): 5/minute (resource intensive)
    - Standard API: 100/minute (default from config)
"""

import logging
from typing import Callable

from fastapi import Request, Response
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address as slowapi_get_remote_address
from starlette.responses import JSONResponse

from app.config import get_settings

logger = logging.getLogger(__name__)


def get_remote_address(request: Request) -> str:
    """Get the client's IP address for rate limiting.

    Checks for X-Forwarded-For header first (for reverse proxy scenarios),
    then falls back to the direct client IP.

    Args:
        request: The incoming FastAPI request.

    Returns:
        The client's IP address as a string.
    """
    # Check for X-Forwarded-For header (common in reverse proxy setups)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For may contain multiple IPs; the first is the client's
        return forwarded_for.split(",")[0].strip()

    # Check for X-Real-IP header (nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fall back to slowapi's default implementation
    return slowapi_get_remote_address(request)


def _get_storage_uri() -> str | None:
    """Get Redis URI for rate limiting storage if available.

    Returns:
        Redis URI string if configured, None for in-memory storage.
    """
    settings = get_settings()

    # Check for Redis configuration (commonly from Celery settings)
    if settings.celery_broker_url and settings.celery_broker_url.startswith("redis://"):
        return settings.celery_broker_url

    # Could also check for explicit rate limit Redis config here
    # For now, fall back to in-memory storage
    return None


def _create_limiter() -> Limiter:
    """Create and configure the SlowAPI Limiter instance.

    Attempts to use Redis for distributed rate limiting,
    falling back to in-memory storage if Redis is unavailable.

    Returns:
        Configured Limiter instance.
    """
    settings = get_settings()
    storage_uri = _get_storage_uri()

    default_limit = f"{settings.rate_limit_requests}/minute"

    if storage_uri:
        try:
            limiter = Limiter(
                key_func=get_remote_address,
                default_limits=[default_limit],
                storage_uri=storage_uri,
                strategy="fixed-window",
            )
            logger.info("Rate limiter initialized with Redis storage")
            return limiter
        except Exception as e:
            logger.warning(
                "Failed to initialize Redis for rate limiting, falling back to in-memory: %s",
                e,
            )

    # Fall back to in-memory storage
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[default_limit],
        strategy="fixed-window",
    )
    logger.info("Rate limiter initialized with in-memory storage")
    return limiter


# Create the global limiter instance
limiter = _create_limiter()


# Rate limit decorators for different endpoint types
# These can be imported and applied to specific endpoints


def auth_rate_limit() -> Callable:
    """Rate limit decorator for authentication endpoints.

    Limits: 5 requests per minute to prevent brute force attacks.
    """
    return limiter.limit("5/minute")


def analysis_rate_limit() -> Callable:
    """Rate limit decorator for analysis/LLM endpoints.

    Limits: 10 requests per hour for expensive AI operations.
    """
    return limiter.limit("10/hour")


def export_rate_limit() -> Callable:
    """Rate limit decorator for export endpoints.

    Limits: 5 requests per minute for resource-intensive exports.
    """
    return limiter.limit("5/minute")


def standard_rate_limit() -> Callable:
    """Rate limit decorator using default configuration.

    Limits: Based on config (default 100 requests per minute).
    """
    settings = get_settings()
    window = settings.rate_limit_window_seconds
    requests = settings.rate_limit_requests

    # Convert seconds to appropriate time unit
    if window == 60:
        return limiter.limit(f"{requests}/minute")
    elif window == 3600:
        return limiter.limit(f"{requests}/hour")
    else:
        return limiter.limit(f"{requests}/{window}seconds")


async def rate_limit_exceeded_handler(
    request: Request,
    exc: RateLimitExceeded,
) -> Response:
    """Exception handler for rate limit exceeded errors.

    Returns a JSON response with appropriate error details and retry information.

    Args:
        request: The incoming request that exceeded the rate limit.
        exc: The RateLimitExceeded exception.

    Returns:
        JSONResponse with 429 status code and error details.
    """
    # Extract retry-after from the exception detail if available
    retry_after = "60"  # Default to 60 seconds

    # Try to parse the limit info from the exception
    limit_info = str(exc.detail) if hasattr(exc, "detail") else ""

    # Log the rate limit event
    client_ip = get_remote_address(request)
    logger.warning(
        "Rate limit exceeded for IP %s on path %s: %s",
        client_ip,
        request.url.path,
        limit_info,
    )

    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": "Too many requests. Please try again later.",
            "limit": limit_info,
        },
        headers={
            "Retry-After": retry_after,
            "X-RateLimit-Limit": limit_info,
        },
    )


# Export the RateLimitExceeded exception for use in main.py
__all__ = [
    "RateLimitExceeded",
    "analysis_rate_limit",
    "auth_rate_limit",
    "export_rate_limit",
    "get_remote_address",
    "limiter",
    "rate_limit_exceeded_handler",
    "standard_rate_limit",
]
