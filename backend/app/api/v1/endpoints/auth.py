"""Authentication API endpoints."""

from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_active_user
from app.db import get_db
from app.middleware.rate_limit import limiter
from app.models import User
from app.models.audit_log import AuditAction
from app.schemas import (
    LoginResponse,
    MFAEnableResponse,
    MFAStatusResponse,
    MFAValidateRequest,
    MFAVerifyRequest,
    RegisterResponse,
    TokenRefresh,
    TokenResponse,
    UserCreate,
    UserResponse,
)
from app.services import auth as auth_service
from app.services.audit import get_audit_service

router = APIRouter(tags=["Authentication"])

# MFA state storage (in production, use Redis or database)
# This temporarily stores the secret during MFA setup before verification
_mfa_setup_secrets: dict[str, str] = {}


def _get_client_ip(request: Request) -> str | None:
    """Extract client IP address from request."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    if request.client:
        return request.client.host
    return None


def _get_user_agent(request: Request) -> str | None:
    """Extract user agent from request."""
    return request.headers.get("User-Agent")


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(
    request: Request,
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
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Login with email and password.

    Returns access and refresh tokens upon successful authentication.
    """
    # Get user for audit logging
    user = await auth_service.get_user_by_email(db, form_data.username)
    audit_service = get_audit_service(db)

    tokens = await auth_service.login_user(
        db, email=form_data.username, password=form_data.password
    )
    if not tokens:
        # Log failed login attempt
        if user:
            await audit_service.log_action(
                organization_id=user.organization_id,
                user_id=user.id,
                action=AuditAction.LOGIN_FAILED,
                resource_type="session",
                ip_address=_get_client_ip(request),
                user_agent=_get_user_agent(request),
                details="Failed login attempt - invalid credentials",
            )
            await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Log successful login
    if user:
        await audit_service.log_action(
            organization_id=user.organization_id,
            user_id=user.id,
            action=AuditAction.LOGIN,
            resource_type="session",
            ip_address=_get_client_ip(request),
            user_agent=_get_user_agent(request),
            details="User logged in successfully",
        )
        await db.commit()

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
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Logout the current user.

    Logs the logout event for audit trail.
    In production, this would also invalidate the token.
    """
    # Log the logout
    audit_service = get_audit_service(db)
    await audit_service.log_action(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        action=AuditAction.LOGOUT,
        resource_type="session",
        ip_address=_get_client_ip(request),
        user_agent=_get_user_agent(request),
        details="User logged out",
    )
    await db.commit()

    return {"message": "Successfully logged out"}


# MFA Endpoints


@router.post("/mfa/enable", response_model=MFAEnableResponse)
async def mfa_enable(
    current_user: User = Depends(get_current_active_user),
) -> MFAEnableResponse:
    """
    Generate TOTP secret and provisioning URI for MFA setup.

    Returns the secret, provisioning URI (for QR codes), and backup codes.
    The user must verify the setup with a valid TOTP code before MFA is activated.
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled for this account",
        )

    # Generate MFA setup data
    mfa_data = await auth_service.enable_mfa_setup(current_user)

    # Store the secret temporarily for verification
    _mfa_setup_secrets[current_user.id] = mfa_data.secret

    return mfa_data


@router.post("/mfa/verify", response_model=MFAStatusResponse)
async def mfa_verify(
    verify_data: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    """
    Verify TOTP code and activate MFA for the account.

    Requires a valid 6-digit TOTP code from the authenticator app.
    """
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled for this account",
        )

    # Get the secret from setup
    secret = _mfa_setup_secrets.get(current_user.id)
    if not secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA setup not initiated. Call /mfa/enable first.",
        )

    # Verify and enable MFA
    success = await auth_service.verify_and_enable_mfa(
        db, current_user, secret, verify_data.code
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code",
        )

    # Clean up the temporary secret
    del _mfa_setup_secrets[current_user.id]

    return MFAStatusResponse(
        mfa_enabled=True,
        message="MFA has been successfully enabled",
    )


@router.post("/mfa/disable", response_model=MFAStatusResponse)
async def mfa_disable(
    verify_data: MFAVerifyRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> MFAStatusResponse:
    """
    Disable MFA for the account.

    Requires a valid 6-digit TOTP code to confirm the action.
    """
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled for this account",
        )

    success = await auth_service.disable_mfa(db, current_user, verify_data.code)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid TOTP code",
        )

    return MFAStatusResponse(
        mfa_enabled=False,
        message="MFA has been successfully disabled",
    )


@router.post("/mfa/validate", response_model=TokenResponse)
@limiter.limit("5/minute")
async def mfa_validate(
    request: Request,
    validate_data: MFAValidateRequest,
    x_mfa_token: str = Header(..., alias="X-MFA-Token"),
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """
    Validate TOTP code during login for MFA-enabled accounts.

    Requires the MFA token from the login response and a valid TOTP code.
    Returns full access and refresh tokens upon successful validation.
    """
    tokens = await auth_service.validate_mfa_login(
        db, x_mfa_token, validate_data.code
    )

    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA token or TOTP code",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return tokens


@router.post("/login-mfa", response_model=LoginResponse)
@limiter.limit("5/minute")
async def login_with_mfa(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
) -> LoginResponse:
    """
    Login with email and password, handling MFA if enabled.

    If MFA is enabled, returns mfa_required=True with a temporary mfa_token.
    The client should then call /mfa/validate with the token and TOTP code.

    If MFA is not enabled, returns full access and refresh tokens.
    """
    result = await auth_service.login_user_with_mfa(
        db, email=form_data.username, password=form_data.password
    )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result
