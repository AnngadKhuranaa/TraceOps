"""SQLAlchemy async database engine and session management."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from traceops.infrastructure.config import Settings
from traceops.infrastructure.logging import get_logger

logger = get_logger(__name__)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

    pass


class DatabaseSessionManager:
    """Manages SQLAlchemy async engine and session lifecycle."""

    def __init__(self) -> None:
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def init(self, settings: Settings) -> None:
        """Initialize the engine and sessionmaker from application settings."""
        self._engine = create_async_engine(
            settings.database_url,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_pre_ping=True,
            echo=settings.debug,
        )
        self._sessionmaker = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
        logger.info("Database session manager initialized.")

    async def close(self) -> None:
        """Dispose of the database engine pool."""
        if self._engine is not None:
            await self._engine.dispose()
            self._engine = None
            self._sessionmaker = None
            logger.info("Database session manager closed.")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional async session context."""
        if self._sessionmaker is None:
            raise RuntimeError("DatabaseSessionManager is not initialized. Call init() first.")

        session: AsyncSession = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def ping(self) -> bool:
        """Execute a lightweight probe query to verify connectivity."""
        if self._engine is None:
            return False

        try:
            async with self._engine.connect() as conn:
                result = await conn.execute(text("SELECT 1"))
                row = result.scalar()
                return row == 1
        except Exception as exc:
            logger.warning(f"Database health probe failed: {exc}")
            return False


# Global singleton instance
db_manager = DatabaseSessionManager()


def get_db_manager() -> DatabaseSessionManager:
    """Return the global DatabaseSessionManager instance."""
    return db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency for yielding database sessions."""
    async with db_manager.session() as session:
        yield session
