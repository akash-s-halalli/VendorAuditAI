"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.models import User
from app.schemas import (
    RegisterResponse,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services import auth as auth_service

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> RegisterResponse:
    """
    Register a new user with organization.

    Creates a new user account and associates it with the specified organization.
    """
    try:
        result = await auth_service.register_user(db, user_data)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login with email and password.

    Returns access and refresh tokens upon successful authentication.
    """
    tokens = await auth_service.login_user(
        db, email=form_data.username, password=form_data.password
    )
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    token_data: TokenRefresh,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Refresh access token using a valid refresh token.

    Returns new access and refresh tokens.
    """
    tokens = await auth_service.refresh_tokens(db, token_data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return tokens


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """
    Get current authenticated user's profile.

    Requires a valid access token.
    """
    return current_user


@router.post("/logout")
async def logout(
    current_user: User = Depends(get_current_active_user),
) -> dict:
    """
    Logout the current user.

    Placeholder endpoint - returns success message.
    In production, this would invalidate the token.
    """
    return {"message": "Successfully logged out"}
