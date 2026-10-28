"""Typed application configuration loaded only on the backend."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parents[1]


class Settings(BaseSettings):
    """Runtime settings with safe local defaults and backend-only secrets."""

    model_config = SettingsConfigDict(
        env_file=BACKEND_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Revenant AI"
    app_version: str = "0.1.0"
    database_url: str = "sqlite:///./mirrorheal.db"
    allowed_origin: str = "http://localhost:5173"
    enable_fault_injection: bool = True
    demo_sku: str = "LAPTOP-001"
    demo_initial_stock: int = Field(default=10, ge=1)

    ai_provider: Literal["gemini", "groq"] = "gemini"
    gemini_api_key: SecretStr | None = None
    gemini_model: str = "gemini-3.5-flash-lite"
    groq_api_key: SecretStr | None = None
    groq_model: str = "openai/gpt-oss-20b"

    ml_artifact_path: Path = Field(default=Path("artifacts/isolation_forest.joblib"))
    ml_metadata_path: Path = Field(
        default=Path("artifacts/isolation_forest.metadata.json")
    )

    def provider_is_configured(self) -> bool:
        """Return whether the selected provider has a non-empty local key."""

        secret = (
            self.gemini_api_key
            if self.ai_provider == "gemini"
            else self.groq_api_key
        )
        return bool(secret and secret.get_secret_value().strip())

    def resolve_backend_path(self, path: Path) -> Path:
        """Resolve relative runtime files against the backend directory."""

        return path if path.is_absolute() else BACKEND_DIR / path


@lru_cache
def get_settings() -> Settings:
    """Return the process settings; tests construct Settings directly."""

    return Settings()
