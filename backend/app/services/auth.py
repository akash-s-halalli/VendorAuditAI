"""Authentication service layer."""

import re
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    verify_password,
    verify_token,
)
from app.models import Organization, User, UserRole
from app.schemas import (
    OrganizationResponse,
    RegisterResponse,
    TokenResponse,
    UserCreate,
    UserResponse,
)

settings = get_settings()


def generate_slug(name: str) -> str:
    """Generate a URL-friendly slug from a name."""
    # Convert to lowercase and replace spaces with hyphens
    slug = name.lower().strip()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"[-\s]+", "-", slug)
    return slug


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Get a user by email address."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: str) -> User | None:
    """Get a user by ID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_organization_by_slug(db: AsyncSession, slug: str) -> Organization | None:
    """Get an organization by slug."""
    result = await db.execute(select(Organization).where(Organization.slug == slug))
    return result.scalar_one_or_none()


async def create_organization(db: AsyncSession, name: str) -> Organization:
    """Create a new organization."""
    base_slug = generate_slug(name)
    slug = base_slug

    # Ensure unique slug
    counter = 1
    while await get_organization_by_slug(db, slug):
        slug = f"{base_slug}-{counter}"
        counter += 1

    organization = Organization(
        name=name,
        slug=slug,
        subscription_tier="free",
    )
    db.add(organization)
    await db.flush()
    return organization


async def create_user(
    db: AsyncSession,
    email: str,
    password: str,
    organization_id: str,
    full_name: str | None = None,
    role: UserRole = UserRole.ADMIN,
) -> User:
    """Create a new user."""
    user = User(
        email=email,
        password_hash=hash_password(password),
        full_name=full_name,
        organization_id=organization_id,
        role=role.value,
        is_active=True,
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> User | None:
    """Authenticate a user by email and password."""
    user = await get_user_by_email(db, email)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    if not user.is_active:
        return None
    return user


async def update_last_login(db: AsyncSession, user: User) -> None:
    """Update user's last login timestamp."""
    user.last_login = datetime.now(UTC)
    await db.flush()


async def register_user(
    db: AsyncSession,
    user_data: UserCreate,
) -> RegisterResponse:
    """Register a new user with a new organization.

    Args:
        db: Database session
        user_data: User registration data

    Returns:
        RegisterResponse with user, organization, and tokens

    Raises:
        ValueError: If email already exists
    """
    # Check if email already exists
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user:
        raise ValueError("Email already registered")

    # Create organization
    organization = await create_organization(db, user_data.organization_name)

    # Create user as admin of the organization
    user = await create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        organization_id=organization.id,
        full_name=user_data.full_name,
        role=UserRole.ADMIN,
    )

    # Generate tokens
    access_token = create_access_token(
        subject=user.id,
        additional_claims={
            "org_id": organization.id,
            "role": user.role,
        },
    )
    refresh_token = create_refresh_token(subject=user.id)

    # Commit the transaction
    await db.commit()

    return RegisterResponse(
        user=UserResponse.model_validate(user),
        organization=OrganizationResponse.model_validate(organization),
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def login_user(
    db: AsyncSession,
    email: str,
    password: str,
) -> TokenResponse | None:
    """Login a user and return tokens.

    Args:
        db: Database session
        email: User email
        password: User password

    Returns:
        TokenResponse with tokens or None if authentication fails
    """
    user = await authenticate_user(db, email, password)
    if not user:
        return None

    # Update last login
    await update_last_login(db, user)

    # Generate tokens
    access_token = create_access_token(
        subject=user.id,
        additional_claims={
            "org_id": user.organization_id,
            "role": user.role,
        },
    )
    refresh_token = create_refresh_token(subject=user.id)

    await db.commit()

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def refresh_tokens(
    db: AsyncSession,
    refresh_token: str,
) -> TokenResponse | None:
    """Refresh access token using refresh token.

    Args:
        db: Database session
        refresh_token: The refresh token

    Returns:
        New TokenResponse or None if refresh token is invalid
    """
    user_id = verify_token(refresh_token, token_type="refresh")
    if not user_id:
        return None

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active:
        return None

    # Generate new tokens
    new_access_token = create_access_token(
        subject=user.id,
        additional_claims={
            "org_id": user.organization_id,
            "role": user.role,
        },
    )
    new_refresh_token = create_refresh_token(subject=user.id)

    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )
