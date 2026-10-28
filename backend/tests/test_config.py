"""Typed settings and SQLite connection behavior tests."""

from pathlib import Path

import pytest
from pydantic import ValidationError
from sqlalchemy import text
from sqlmodel import Session

from app.config import Settings
from app.db import create_db_engine


def test_settings_ignore_unknown_environment_fields(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("UNRELATED_HOST_SETTING", "ignored")

    settings = Settings(_env_file=None)

    assert settings.app_name == "Revenant AI"


def test_invalid_provider_fails_configuration() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, ai_provider="unsupported")


def test_empty_provider_secret_is_not_configured() -> None:
    settings = Settings(_env_file=None, gemini_api_key="   ")

    assert settings.provider_is_configured() is False


def test_sqlite_foreign_keys_are_enabled(tmp_path: Path) -> None:
    engine = create_db_engine(f"sqlite:///{tmp_path / 'foreign-keys.db'}")

    with Session(engine) as session:
        enabled = session.exec(text("PRAGMA foreign_keys")).one()

    assert enabled[0] == 1
    engine.dispose()
