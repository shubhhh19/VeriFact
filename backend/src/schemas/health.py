"""
Health check schemas for API responses.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional

from pydantic import BaseModel, Field


class HealthStatus(str, Enum):
    """Health status of a service."""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"


class ServiceHealth(BaseModel):
    """Health status of a single service."""
    status: HealthStatus = Field(
        ...,
        description="Health status of the service",
        example=HealthStatus.HEALTHY,
    )
    details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional details about the service health",
        example={"latency_ms": 12.34},
    )


class HealthCheck(BaseModel):
    """Health check response model."""
    status: HealthStatus = Field(
        ...,
        description="Overall health status of the application",
        example=HealthStatus.HEALTHY,
    )
    version: str = Field(
        ...,
        description="Application version",
        example="1.0.0",
    )
    timestamp: str = Field(
        ...,
        description="ISO 8601 timestamp of the health check",
        example="2023-01-01T00:00:00Z",
    )
    services: Dict[str, ServiceHealth] = Field(
        ...,
        description="Health status of individual services",
        example={
            "database": {
                "status": "healthy",
                "details": {"latency_ms": 5.2}
            },
            "redis": {
                "status": "healthy",
                "details": {"latency_ms": 1.8}
            },
        },
    )

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "timestamp": "2023-01-01T00:00:00Z",
                "services": {
                    "database": {
                        "status": "healthy",
                        "details": {"latency_ms": 5.2}
                    },
                    "redis": {
                        "status": "healthy",
                        "details": {"latency_ms": 1.8}
                    },
                },
            }
        }
