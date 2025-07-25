"""
VeriFact API v1

This package contains the API routes for version 1 of the VeriFact API.
"""

__all__ = ["router"]

from fastapi import APIRouter

# Create API router
router = APIRouter(prefix="/api/v1", tags=["v1"])

# Import and include all route modules
from . import health
from .routers import articles

# Include routers
router.include_router(health.router)
router.include_router(articles.router, prefix="/articles")
