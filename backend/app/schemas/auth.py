"""Pydantic schemas for authentication."""

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    full_name: str | None = None


class UserCreate(UserBase):
    """Schema for creating a new user."""

    password: str = Field(..., min_length=8, max_length=128)
    organization_name: str = Field(..., min_length=2, max_length=255)

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password complexity."""
        if not any(c.isupper() for c in v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not any(c.islower() for c in v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        return v


class UserLogin(BaseModel):
    """Schema for user login."""

    email: EmailStr
    password: str


class UserResponse(UserBase):
    """Schema for user response."""

    id: str
    role: str
    is_active: bool
    organization_id: str
    mfa_enabled: bool
    last_login: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    full_name: str | None = None
    email: EmailStr | None = None


class PasswordChange(BaseModel):
    """Schema for changing password."""

    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Schema for token response."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenRefresh(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str


class OrganizationBase(BaseModel):
    """Base organization schema."""

    name: str = Field(..., min_length=2, max_length=255)


class OrganizationResponse(OrganizationBase):
    """Schema for organization response."""

    id: str
    slug: str
    subscription_tier: str
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    """Schema for registration response."""

    user: UserResponse
    organization: OrganizationResponse
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


# MFA Schemas
class MFAEnableResponse(BaseModel):
    """Schema for MFA enable response with secret and provisioning URI."""

    secret: str
    provisioning_uri: str
    backup_codes: list[str]


class MFAVerifyRequest(BaseModel):
    """Schema for verifying TOTP code during MFA setup."""

    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class MFAValidateRequest(BaseModel):
    """Schema for validating TOTP code during login."""

    code: str = Field(..., min_length=6, max_length=6, pattern=r"^\d{6}$")


class MFAStatusResponse(BaseModel):
    """Schema for MFA status response."""

    mfa_enabled: bool
    message: str


class LoginResponse(BaseModel):
    """Schema for login response that may require MFA."""

    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int | None = None
    mfa_required: bool = False
    mfa_token: str | None = None  # Temporary token for MFA validation
