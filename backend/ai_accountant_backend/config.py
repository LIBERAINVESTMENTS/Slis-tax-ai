"""Application configuration.

All values are environment-driven; nothing here is hardcoded so the platform can be
reconfigured per deployment without code changes. See `.env.example` at the repo root.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Core ---
    app_name: str = "AI Accountant"
    api_prefix: str = "/api"
    environment: str = "development"  # development | test | production
    debug: bool = True

    # --- Security ---
    secret_key: str = Field(
        default="CHANGE_ME__insecure_dev_secret_key_min_32_chars",
        description="JWT signing key. Must be overridden in production.",
    )
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14
    # Fernet key (urlsafe base64 of 32 bytes) for encrypting integration secrets + sensitive financial fields at rest.
    encryption_key: str = Field(
        default="",
        description="Fernet key for at-rest secret encryption; auto-generated in-memory if empty.",
    )
    allowed_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    # --- MFA ---
    mfa_issuer: str = "AI Accountant"
    mfa_window: int = 1  # TOTP validation window

    # --- Database ---
    database_url: str = "sqlite:///./ai-accountant.db"  # overridden by docker/.env to postgresql+psycopg2
    test_database_url: str = ""

    # --- LLM provider (provider-agnostic) ---
    llm_provider: str = "mock"  # mock | openrouter | openai | anthropic | moonshot | deepseek | ollama
    openrouter_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""
    moonshot_api_key: str = ""
    deepseek_api_key: str = ""
    ollama_base_url: str = "http://127.0.0.1:11434"
    # Comma-separated model tier map: light=...,standard=...,heavy=...
    model_light: str = ""
    model_standard: str = ""
    model_heavy: str = ""
    # Price per 1M tokens for the active models, as "model:prompt_price:completion_price" pairs separated by "|"
    model_pricing: str = ""
    default_monthly_ai_budget_usd: float = 50.0
    llm_timeout_seconds: float = 60.0
    llm_max_retries: int = 2

    # --- Embeddings ---
    embedding_provider: str = "hashing"  # hashing | openai_compat
    embedding_dim: int = 384
    openai_compat_embedding_model: str = ""

    # --- Jobs ---
    scheduler_enabled: bool = True

    # --- Document storage ---
    document_storage_path: str = "./data/documents"

    @property
    def cors_origins(self) -> list[str]:
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
