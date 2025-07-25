"""
Test configuration and fixtures for VeriFact backend tests.
"""

import asyncio
import os
import pytest
from pathlib import Path
from typing import AsyncGenerator, Dict, Any

import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

from src.core.database import DatabaseManager, Base
from src.core.redis import RedisManager
from src.main import create_application

# Set test environment
os.environ["TESTING"] = "True"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"  # Use DB 1 for testing

# Override settings for testing
settings = {
    "DATABASE_URL": os.environ["DATABASE_URL"],
    "REDIS_URL": os.environ["REDIS_URL"],
    "DEBUG": True
}

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def app() -> FastAPI:
    """Create a test FastAPI application."""
    return create_application()

@pytest.fixture(scope="session")
def test_client(app: FastAPI) -> TestClient:
    """Create a test client for the FastAPI application."""
    return TestClient(app)

@pytest_asyncio.fixture(scope="function")
async def db_manager() -> AsyncGenerator[DatabaseManager, None]:
    """Create a test database manager with an in-memory SQLite database."""
    test_db_manager = DatabaseManager(
        settings["DATABASE_URL"],
        echo=settings["DEBUG"],
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    
    # Initialize the engine
    await test_db_manager.init_engine()
    
    # Create all tables
    engine = test_db_manager.engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield test_db_manager
    
    # Drop all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Close the connection
    await test_db_manager.close()

@pytest_asyncio.fixture(scope="function")
async def redis_manager() -> AsyncGenerator[RedisManager, None]:
    """Create a test Redis manager with a test database."""
    test_redis_manager = RedisManager(settings["REDIS_URL"])
    
    # Clear the test database
    redis_client = await test_redis_manager.get_redis()
    await redis_client.flushdb()
    
    yield test_redis_manager
    
    # Clean up
    await redis_client.flushdb()
    await test_redis_manager.close()

@pytest_asyncio.fixture(scope="function")
async def db_session(db_manager: DatabaseManager) -> AsyncGenerator[Any, None]:
    """Create a test database session with automatic rollback."""
    async with db_manager.session_factory() as session:
        try:
            yield session
            await session.rollback()
        finally:
            await session.close()

@pytest.fixture(scope="function")
async def test_data() -> Dict[str, Any]:
    """Provide test data for database tests."""
    return {
        "article": {
            "title": "Test Article",
            "content": "This is a test article content.",
            "source": "Test Source",
            "url": "https://example.com/test-article",
            "published_at": "2023-01-01T00:00:00Z",
        },
        "validation": {
            "status": "pending",
            "confidence_score": 0.85,
            "details": {"test": "test"},
        },
    }
