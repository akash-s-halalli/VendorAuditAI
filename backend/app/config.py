"""Configuration management using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    app_name: str = "VendorAuditAI"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "change-me-in-production-use-secrets-generate"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./vendorauditai.db"
    database_echo: bool = False
    database_pool_size: int = 20

    # Storage
    storage_backend: str = "local"  # "local" or "minio"
    local_storage_path: str = "./uploads"
    minio_endpoint: str | None = None
    minio_access_key: str | None = None
    minio_secret_key: str | None = None
    minio_bucket: str = "documents"
    minio_secure: bool = False

    # AI/ML - Provider Selection
    llm_provider: str = "anthropic"  # "anthropic" or "gemini"
    embedding_provider: str = "openai"  # "openai" or "gemini"

    # Anthropic (Claude)
    anthropic_api_key: str | None = None
    claude_model: str = "claude-sonnet-4-20250514"

    # OpenAI
    openai_api_key: str | None = None
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072

    # Google Gemini
    google_api_key: str | None = None
    gemini_model: str = "gemini-2.0-flash"
    gemini_embedding_model: str = "text-embedding-004"

    # Document Processing
    azure_doc_intel_endpoint: str | None = None
    azure_doc_intel_key: str | None = None
    use_azure_doc_intel: bool = False

    # Security - JWT
    jwt_secret_key: str = "jwt-secret-change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["*"]
    cors_allow_headers: list[str] = ["*"]

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60

    # Celery (optional - for async task processing)
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None
    use_celery: bool = False

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"

    @property
    def database_is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return "sqlite" in self.database_url.lower()


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
