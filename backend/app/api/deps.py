"""
FastAPI dependencies for authentication and authorization.
"""

from typing import Annotated, List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.core.security import verify_token
from app.models import User, UserRole
from app.services.auth import get_user_by_id

# OAuth2 scheme for JWT token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Extract and validate JWT from Authorization header.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        User: The authenticated user

    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the token and extract user ID
    user_id = verify_token(token, token_type="access")
    if user_id is None:
        raise credentials_exception

    # Fetch user from database
    user = await get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """
    Ensure the current user is active.

    Args:
        current_user: The authenticated user from get_current_user

    Returns:
        User: The active authenticated user

    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )
    return current_user


async def get_current_admin_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> User:
    """
    Ensure the current user has admin role.

    Args:
        current_user: The active authenticated user

    Returns:
        User: The admin user

    Raises:
        HTTPException: 403 if user is not an admin
    """
    if current_user.role != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required",
        )
    return current_user


class RoleChecker:
    """
    Dependency class for role-based authorization.

    Usage:
        @router.get("/endpoint")
        async def endpoint(
            user: Annotated[User, Depends(RoleChecker([UserRole.ADMIN, UserRole.MANAGER]))]
        ):
            ...
    """

    def __init__(self, allowed_roles: List[UserRole]):
        """
        Initialize RoleChecker with allowed roles.

        Args:
            allowed_roles: List of UserRole values that are permitted access
        """
        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        """
        Check if the current user has one of the allowed roles.

        Args:
            current_user: The active authenticated user

        Returns:
            User: The authorized user

        Raises:
            HTTPException: 403 if user role is not in allowed_roles
        """
        allowed_role_values = [role.value for role in self.allowed_roles]
        if current_user.role not in allowed_role_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {allowed_role_values}",
            )
        return current_user
