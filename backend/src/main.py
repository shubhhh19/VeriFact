"""
News Validator Agent - FastAPI Application
Main entry point for the News Validator Agent API
"""

import os
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Application metadata
API_TITLE = "VeriFact API"
API_DESCRIPTION = "API for VeriFact - AI-powered news validation system"
API_VERSION = "0.1.0"

# Create application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Starting News Validator Agent API...")
    
    # Initialize services
    # TODO: Initialize database connection
    # TODO: Initialize Redis connection
    # TODO: Initialize AI models
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("Shutting down News Validator Agent API...")
    # TODO: Clean up resources

# Create FastAPI app
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint
@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "healthy"}

# API v1 router
from fastapi import APIRouter

# Create API router
api_router = APIRouter(prefix="/api/v1", tags=["v1"])

# Include routers
from .api.v1.routers import articles
from .api.v1.routers.validation import router as validation_router

api_router.include_router(articles.router, prefix="/articles", tags=["articles"])
api_router.include_router(validation_router, prefix="/validation", tags=["validation"])

# Include the API router
app.include_router(api_router)

# Root endpoint
@app.get("/", include_in_schema=False)
async def root() -> Dict[str, str]:
    """Root endpoint with API information"""
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }

# Custom exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle all other exceptions"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )

# Run with uvicorn programmatically
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("ENV") == "development",
        log_level="info"
    )
