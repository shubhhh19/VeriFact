"""
Health Check Endpoint

This module provides health check endpoints for the VeriFact API.
"""

from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.models.base import Base
from src.config import settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=Dict[str, Any])
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.
    
    Returns:
        Dict containing the status and timestamp
    """
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "VeriFact API",
        "version": "1.0.0",
    }


@router.get("/health/db", response_model=Dict[str, Any])
async def db_health_check(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    Database health check endpoint.
    
    Verifies that the database is accessible and responsive.
    
    Returns:
        Dict containing the database status and metadata
    """
    try:
        # Test database connection
        result = await db.execute("SELECT 1")
        result.scalar()
        
        # Get database info
        db_info = {
            "status": "ok",
            "database": settings.POSTGRES_DB,
            "host": settings.POSTGRES_SERVER,
            "time": datetime.utcnow().isoformat(),
        }
        
        return db_info
        
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "error": str(e),
                "database": settings.POSTGRES_DB,
                "host": settings.POSTGRES_SERVER,
            }
        )


@router.get("/health/redis", response_model=Dict[str, Any])
async def redis_health_check() -> Dict[str, Any]:
    """
    Redis health check endpoint.
    
    Verifies that Redis is accessible and responsive.
    
    Returns:
        Dict containing the Redis status and metadata
    """
    try:
        import redis
        from redis.exceptions import RedisError
        
        r = redis.Redis.from_url(settings.REDIS_URL)
        pong = r.ping()
        
        return {
            "status": "ok" if pong else "error",
            "service": "Redis",
            "url": settings.REDIS_URL,
            "time": datetime.utcnow().isoformat(),
        }
        
    except RedisError as e:
        return {
            "status": "error",
            "service": "Redis",
            "error": str(e),
            "url": settings.REDIS_URL,
            "time": datetime.utcnow().isoformat(),
        }
