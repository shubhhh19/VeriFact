"""
News Validator Agent - Database Session
Handles database connections and sessions with SQLAlchemy
"""

from typing import AsyncGenerator, Dict, Any

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    AsyncEngine
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool

from src.config import settings

# Determine if we're using SQLite
is_sqlite = "sqlite" in str(settings.DATABASE_URL).lower()

# Common engine parameters
engine_params: Dict[str, Any] = {
    "echo": settings.DEBUG,
    "future": True,
    "pool_pre_ping": True,
}

# Add pool settings only for PostgreSQL
if not is_sqlite:
    engine_params.update({
        "pool_size": 10,
        "max_overflow": 20,
        "pool_timeout": 30,
        "pool_recycle": 3600,
    })

# For testing, use NullPool
if settings.TESTING:
    engine_params["poolclass"] = NullPool

# For SQLite, add SQLite-specific parameters
if is_sqlite:
    engine_params["connect_args"] = {"check_same_thread": False}
    # SQLite doesn't support some pool settings
    engine_params.pop("pool_size", None)
    engine_params.pop("max_overflow", None)
    engine_params.pop("pool_timeout", None)
    engine_params.pop("pool_recycle", None)

# Create async engine
engine: AsyncEngine = create_async_engine(
    settings.DATABASE_URL,
    **engine_params
)

# Create async session factory
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database session"""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e


async def create_tables() -> None:
    """Create database tables"""
    async with engine.begin() as conn:
        # Create schema if it doesn't exist
        await conn.execute(CreateSchema(settings.POSTGRES_DB, if_not_exists=True))
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)


async def drop_tables() -> None:
    """Drop all database tables (for testing)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
