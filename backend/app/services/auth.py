"""Authentication service layer."""

import re
import secrets
from datetime import UTC, datetime, timedelta

import pyotp
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
    LoginResponse,
    MFAEnableResponse,
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


# MFA Service Functions


def generate_backup_codes(count: int = 10) -> list[str]:
    """Generate a list of backup codes for MFA recovery.

    Args:
        count: Number of backup codes to generate

    Returns:
        List of backup codes (8-character alphanumeric)
    """
    return [secrets.token_hex(4).upper() for _ in range(count)]


def generate_mfa_secret() -> str:
    """Generate a random base32 secret for TOTP.

    Returns:
        Base32-encoded secret string
    """
    return pyotp.random_base32()


def get_provisioning_uri(secret: str, email: str, issuer: str = "VendorAuditAI") -> str:
    """Generate a provisioning URI for authenticator apps.

    Args:
        secret: The TOTP secret
        email: User's email address
        issuer: The issuer name (app name)

    Returns:
        OTPAuth URI for QR code generation
    """
    totp = pyotp.TOTP(secret)
    return totp.provisioning_uri(name=email, issuer_name=issuer)


def verify_totp_code(secret: str, code: str, valid_window: int = 1) -> bool:
    """Verify a TOTP code against a secret.

    Args:
        secret: The TOTP secret
        code: The 6-digit code to verify
        valid_window: Number of time steps to allow (for clock drift)

    Returns:
        True if the code is valid, False otherwise
    """
    totp = pyotp.TOTP(secret)
    return totp.verify(code, valid_window=valid_window)


async def enable_mfa_setup(user: User) -> MFAEnableResponse:
    """Generate MFA setup data for a user.

    This generates a new secret and provisioning URI but does NOT
    enable MFA yet. The user must verify a code first.

    Args:
        user: The user enabling MFA

    Returns:
        MFAEnableResponse with secret, URI, and backup codes
    """
    secret = generate_mfa_secret()
    provisioning_uri = get_provisioning_uri(secret, user.email)
    backup_codes = generate_backup_codes()

    return MFAEnableResponse(
        secret=secret,
        provisioning_uri=provisioning_uri,
        backup_codes=backup_codes,
    )


async def verify_and_enable_mfa(
    db: AsyncSession,
    user: User,
    secret: str,
    code: str,
) -> bool:
    """Verify TOTP code and enable MFA for a user.

    Args:
        db: Database session
        user: The user to enable MFA for
        secret: The TOTP secret to verify against
        code: The TOTP code from the user's authenticator

    Returns:
        True if MFA was enabled successfully, False otherwise
    """
    if not verify_totp_code(secret, code):
        return False

    # Enable MFA and store the secret
    user.mfa_enabled = True
    user.mfa_secret = secret
    await db.commit()
    return True


async def disable_mfa(
    db: AsyncSession,
    user: User,
    code: str,
) -> bool:
    """Disable MFA for a user after verifying their current TOTP code.

    Args:
        db: Database session
        user: The user to disable MFA for
        code: The TOTP code from the user's authenticator

    Returns:
        True if MFA was disabled successfully, False otherwise
    """
    if not user.mfa_enabled or not user.mfa_secret:
        return False

    if not verify_totp_code(user.mfa_secret, code):
        return False

    # Disable MFA and clear the secret
    user.mfa_enabled = False
    user.mfa_secret = None
    await db.commit()
    return True


def create_mfa_token(user_id: str) -> str:
    """Create a temporary token for MFA validation during login.

    This token is short-lived and used only to complete the MFA step.

    Args:
        user_id: The user's ID

    Returns:
        JWT token for MFA validation
    """
    return create_access_token(
        subject=user_id,
        expires_delta=timedelta(minutes=5),
        additional_claims={"type": "mfa_pending"},
    )


def verify_mfa_token(token: str) -> str | None:
    """Verify an MFA pending token and return the user ID.

    Args:
        token: The MFA pending token

    Returns:
        User ID if valid, None otherwise
    """
    from app.core.security import decode_token

    payload = decode_token(token)
    if payload is None:
        return None

    # Verify this is an MFA pending token
    if payload.get("type") != "mfa_pending":
        return None

    return payload.get("sub")


async def login_user_with_mfa(
    db: AsyncSession,
    email: str,
    password: str,
) -> LoginResponse | None:
    """Login a user and handle MFA if enabled.

    Args:
        db: Database session
        email: User email
        password: User password

    Returns:
        LoginResponse with tokens or MFA requirement, None if auth fails
    """
    user = await authenticate_user(db, email, password)
    if not user:
        return None

    # If MFA is enabled, return MFA token instead of full tokens
    if user.mfa_enabled:
        mfa_token = create_mfa_token(user.id)
        return LoginResponse(
            mfa_required=True,
            mfa_token=mfa_token,
        )

    # No MFA - proceed with normal login
    await update_last_login(db, user)

    access_token = create_access_token(
        subject=user.id,
        additional_claims={
            "org_id": user.organization_id,
            "role": user.role,
        },
    )
    refresh_token = create_refresh_token(subject=user.id)

    await db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def validate_mfa_login(
    db: AsyncSession,
    mfa_token: str,
    code: str,
) -> TokenResponse | None:
    """Complete login by validating MFA code.

    Args:
        db: Database session
        mfa_token: The temporary MFA token from login
        code: The TOTP code from the user's authenticator

    Returns:
        TokenResponse with access/refresh tokens, None if validation fails
    """
    user_id = verify_mfa_token(mfa_token)
    if not user_id:
        return None

    user = await get_user_by_id(db, user_id)
    if not user or not user.is_active or not user.mfa_enabled:
        return None

    if not user.mfa_secret or not verify_totp_code(user.mfa_secret, code):
        return None

    # MFA validated - issue full tokens
    await update_last_login(db, user)

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
