"""Typed application configuration management using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """TraceOps application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Core Application Settings
    app_name: str = Field(default="TraceOps API", description="Application service name")
    app_env: Literal["development", "test", "production"] = Field(
        default="development",
        description="Current runtime environment",
    )
    debug: bool = Field(default=False, description="Enable debug mode and detailed logs")
    log_level: str = Field(default="INFO", description="Log level: DEBUG, INFO, WARNING, ERROR")

    # Server Settings
    host: str = Field(default="0.0.0.0", description="Bind host address")
    port: int = Field(default=8000, description="Bind port")

    # Database Settings
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/traceops",
        description="Async PostgreSQL connection string",
    )
    database_pool_size: int = Field(default=5, description="Connection pool size")
    database_max_overflow: int = Field(default=10, description="Max overflow connections")
    database_pool_timeout: float = Field(
        default=30.0, description="Pool connection timeout in seconds"
    )

    # CORS Settings
    cors_origins: list[str] = Field(
        default=["http://localhost:3000"],
        description="Allowed CORS origin URLs",
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        upper = value.upper()
        if upper not in valid_levels:
            raise ValueError(f"Invalid LOG_LEVEL '{value}'. Must be one of: {sorted(valid_levels)}")
        return upper


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton instance of application settings."""
    return Settings()
