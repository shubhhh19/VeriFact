"""
Database Dependencies

This module provides database session dependencies for FastAPI endpoints.
"""

from typing import AsyncGenerator

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency that provides a database session.
    
    Yields:
        AsyncSession: An async database session
        
    Raises:
        HTTPException: If there's an error creating the session
    """
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}",
            )
        finally:
            await session.close()


# Re-export commonly used types for convenience
DatabaseSession = AsyncSession
DatabaseSessionDep = Depends(get_db)
