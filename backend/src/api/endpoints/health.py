"""
Health check endpoints for monitoring the application status.
"""

import logging
from datetime import datetime
from typing import Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.core.database import get_db
from src.core.redis import get_redis, RedisManager
from src.schemas.health import HealthCheck, HealthStatus, ServiceHealth

router = APIRouter()
logger = logging.getLogger(__name__)


async def check_database_health(db: AsyncSession) -> ServiceHealth:
    """Check database health by executing a simple query."""
    try:
        start_time = datetime.utcnow()
        await db.execute(text("SELECT 1"))
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000  # ms
        return ServiceHealth(
            status=HealthStatus.HEALTHY,
            details={"latency_ms": round(latency, 2)},
        )
    except Exception as e:
        logger.error(f"Database health check failed: {e}", exc_info=True)
        return ServiceHealth(
            status=HealthStatus.UNHEALTHY,
            details={"error": str(e)},
        )


async def check_redis_health(redis: RedisManager) -> ServiceHealth:
    """Check Redis health by executing a PING command."""
    try:
        start_time = datetime.utcnow()
        client = await redis.get_redis()
        await client.ping()
        latency = (datetime.utcnow() - start_time).total_seconds() * 1000  # ms
        return ServiceHealth(
            status=HealthStatus.HEALTHY,
            details={"latency_ms": round(latency, 2)},
        )
    except Exception as e:
        logger.error(f"Redis health check failed: {e}", exc_info=True)
        return ServiceHealth(
            status=HealthStatus.UNHEALTHY,
            details={"error": str(e)},
        )


@router.get(
    "/health",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check the health status of the application and its dependencies.",
    response_description="Health status of the application and its dependencies.",
)
async def health_check(
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
) -> HealthCheck:
    """
    Check the health status of the application and its dependencies.
    
    This endpoint performs health checks on the application and its dependencies
    (database, Redis, etc.) and returns a detailed health status report.
    
    Returns:
        HealthCheck: A detailed health status report.
    """
    # Run all health checks in parallel
    db_health, redis_health = await asyncio.gather(
        check_database_health(db),
        check_redis_health(redis),
    )
    
    # Determine overall status
    services_health = {
        "database": db_health,
        "redis": redis_health,
    }
    
    # Check if all services are healthy
    all_healthy = all(
        service.status == HealthStatus.HEALTHY 
        for service in services_health.values()
    )
    
    overall_status = (
        HealthStatus.HEALTHY if all_healthy 
        else HealthStatus.UNHEALTHY
    )
    
    return HealthCheck(
        status=overall_status,
        version=settings.APP_VERSION,
        timestamp=datetime.utcnow().isoformat(),
        services=services_health,
    )


@router.get(
    "/health/live",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Liveness Check",
    description="Simple liveness check to verify that the application is running.",
    response_description="Empty response with 204 status code if the application is running.",
)
async def liveness_check() -> None:
    """
    Simple liveness check endpoint.
    
    This endpoint returns a 204 status code if the application is running.
    It does not check any dependencies, making it suitable for liveness probes.
    """
    return None


@router.get(
    "/health/ready",
    response_model=HealthCheck,
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Check if the application is ready to handle requests.",
    response_description="Readiness status of the application.",
)
async def readiness_check(
    db: AsyncSession = Depends(get_db),
    redis: RedisManager = Depends(get_redis),
) -> HealthCheck:
    """
    Check if the application is ready to handle requests.
    
    This endpoint performs readiness checks on the application and its dependencies
    (database, Redis, etc.) to determine if the application is ready to handle requests.
    
    Returns:
        HealthCheck: A detailed readiness status report.
    """
    # For readiness, we can use the same checks as the health endpoint
    health = await health_check(db, redis)
    
    # If any service is unhealthy, return a 503 status code
    if health.status != HealthStatus.HEALTHY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=jsonable_encoder(health),
        )
    
    return health
