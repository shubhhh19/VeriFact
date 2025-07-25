"""
Database Utilities

This module provides database connection management, session handling,
and other database-related utilities using SQLAlchemy with async support.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from ..config import settings

# Configure logger
logger = logging.getLogger(__name__)

# Create base class for SQLAlchemy models
Base = declarative_base()

class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str, **engine_options: Any) -> None:
        """Initialize the database manager.
        
        Args:
            database_url: The database connection URL
            **engine_options: Additional options to pass to create_async_engine
        """
        self.database_url = database_url
        self._engine: Optional[AsyncEngine] = None
        self._session_factory: Optional[async_sessionmaker] = None
        self.engine_options = engine_options
        self._initialized = False
        
        # Set default engine options if not provided
        self.engine_options.setdefault("echo", settings.DEBUG)
        self.engine_options.setdefault("future", True)
        self.engine_options.setdefault("pool_pre_ping", True)
        self.engine_options.setdefault("pool_recycle", 300)
        
        # For testing with SQLite in-memory
        if ":memory:" in database_url or "sqlite" in database_url:
            self.engine_options["connect_args"] = {"check_same_thread": False}
            self.engine_options["poolclass"] = StaticPool

    async def init_engine(self) -> None:
        """Initialize the database engine and session factory."""
        if self._initialized:
            return
            
        self._engine = create_async_engine(
            self.database_url,
            **self.engine_options
        )
        
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        self._initialized = True

    @property
    def engine(self) -> AsyncEngine:
        """Get the database engine."""
        if self._engine is None:
            raise RuntimeError("Database engine is not initialized. Call init_engine() first.")
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker:
        """Get the session factory."""
        if self._session_factory is None:
            raise RuntimeError("Session factory is not initialized. Call init_engine() first.")
        return self._session_factory

    async def create_all(self) -> None:
        """Create all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda c: Base.metadata.create_all(bind=c))

    async def drop_all(self) -> None:
        """Drop all database tables."""
        async with self.engine.begin() as conn:
            await conn.run_sync(lambda c: Base.metadata.drop_all(bind=c))

    async def close(self) -> None:
        """Close the database connection."""
        if self._engine:
            await self._engine.dispose()
            self._engine = None
            self._session_factory = None
            self._initialized = False

# Create a global database manager instance
db_manager = DatabaseManager(settings.DATABASE_URL)

# Initialize the database
async def init_db() -> None:
    """Initialize the database by creating all tables."""
    await db_manager.init_engine()
    await db_manager.create_all()

# Close the database connection
async def close_db() -> None:
    """Close the database connection."""
    await db_manager.close()

# Dependency to get database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that yields database sessions."""
    if db_manager._session_factory is None:
        await db_manager.init_engine()
    
    session = db_manager.session_factory()
    try:
        yield session
    finally:
        await session.close()
