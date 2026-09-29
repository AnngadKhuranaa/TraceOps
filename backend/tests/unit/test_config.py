"""Unit tests for configuration management."""

import pytest
from pydantic import ValidationError

from traceops.infrastructure.config import Settings


def test_default_settings() -> None:
    """Verify default configuration values."""
    settings = Settings()
    assert settings.app_name == "TraceOps API"
    assert settings.app_env in {"development", "test", "production"}
    assert settings.log_level in {"DEBUG", "INFO", "WARNING", "ERROR"}
    assert settings.database_url.startswith("postgresql+asyncpg://")


def test_custom_settings_override() -> None:
    """Verify that settings can be cleanly customized."""
    settings = Settings(
        app_name="Custom TraceOps",
        app_env="test",
        debug=True,
        log_level="DEBUG",
        port=9000,
    )
    assert settings.app_name == "Custom TraceOps"
    assert settings.app_env == "test"
    assert settings.debug is True
    assert settings.log_level == "DEBUG"
    assert settings.port == 9000


def test_invalid_log_level_raises_validation_error() -> None:
    """Verify that an invalid log level fails validation."""
    with pytest.raises(ValidationError):
        Settings(log_level="INVALID_LEVEL")


def test_invalid_app_env_raises_validation_error() -> None:
    """Verify that an invalid app environment fails validation."""
    with pytest.raises(ValidationError):
        Settings(app_env="staging")  # type: ignore[arg-type]
