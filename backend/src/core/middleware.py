"""
Middleware for production features like CORS, security headers, and request logging.
"""

import json
import logging
import time
from typing import Any, Awaitable, Callable, Dict, List, Optional, Union

from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from ..config import settings

logger = logging.getLogger(__name__)

# Security headers constants
CSP_POLICY = """
    default-src 'self';
    script-src 'self' 'unsafe-inline' 'unsafe-eval' https:;
    style-src 'self' 'unsafe-inline' https:;
    img-src 'self' data: https:;
    font-src 'self' data: https:;
    connect-src 'self' https:;
    media-src 'self' https:;
    object-src 'none';
    frame-ancestors 'none';
    base-uri 'self';
    form-action 'self';
    frame-src 'self';
    block-all-mixed-content;
    upgrade-insecure-requests;
""".replace("\n", " ").strip()

# Common security headers
SECURITY_HEADERS = {
    "Content-Security-Policy": CSP_POLICY,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Cross-Origin-Embedder-Policy": "require-corp",
    "Cross-Origin-Opener-Policy": "same-origin",
    "Cross-Origin-Resource-Policy": "same-site",
}


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging HTTP requests and responses."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Log request and response details."""
        # Skip logging for health checks and metrics
        if request.url.path in {"/health", "/metrics", "/favicon.ico"}:
            return await call_next(request)
        
        # Log request
        start_time = time.time()
        request_id = request.headers.get("X-Request-ID", "")
        
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": dict(request.query_params),
                "client": request.client.host if request.client else None,
                "user_agent": request.headers.get("user-agent"),
            },
        )
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log unhandled exceptions
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "error": str(exc),
                    "exc_info": True,
                },
            )
            raise
        
        # Calculate request processing time
        process_time = (time.time() - start_time) * 1000
        process_time = round(process_time, 2)
        
        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time_ms": process_time,
            },
        )
        
        # Add server timing header
        response.headers["Server-Timing"] = f"total;dur={process_time}"
        
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers to responses."""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Add security headers to the response."""
        response = await call_next(request)
        
        # Add security headers
        for header, value in SECURITY_HEADERS.items():
            if header not in response.headers:
                response.headers[header] = value
        
        # Add HSTS header for HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting requests."""
    
    def __init__(
        self,
        app: ASGIApp,
        limit: int = 100,
        window: int = 60,
        identifier: Optional[Callable[[Request], str]] = None,
    ) -> None:
        super().__init__(app)
        self.limit = limit
        self.window = window
        self.identifier = identifier or (lambda request: request.client.host if request.client else "default")
        self.rate_limits: Dict[str, List[float]] = {}
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Enforce rate limiting."""
        # Skip rate limiting for health checks and metrics
        if request.url.path in {"/health", "/metrics", "/favicon.ico"}:
            return await call_next(request)
        
        # Get client identifier
        client_id = self.identifier(request)
        now = time.time()
        
        # Clean up old entries
        if client_id in self.rate_limits:
            self.rate_limits[client_id] = [
                timestamp for timestamp in self.rate_limits[client_id]
                if now - timestamp < self.window
            ]
        else:
            self.rate_limits[client_id] = []
        
        # Check rate limit
        if len(self.rate_limits[client_id]) >= self.limit:
            return Response(
                content=json.dumps({"detail": "Rate limit exceeded"}),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={"Retry-After": str(self.window)},
            )
        
        # Add current request timestamp
        self.rate_limits[client_id].append(now)
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers.update({
            "X-RateLimit-Limit": str(self.limit),
            "X-RateLimit-Remaining": str(self.limit - len(self.rate_limits[client_id])),
            "X-RateLimit-Reset": str(int(now + self.window)),
        })
        
        return response


def setup_cors(app: FastAPI) -> None:
    """Configure CORS middleware."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["Content-Range", "X-Total-Count"],
    )


def setup_trusted_hosts(app: FastAPI) -> None:
    """Configure trusted hosts middleware."""
    if settings.DEBUG:
        allowed_hosts = ["*"]
    else:
        allowed_hosts = [
            host.strip()
            for host in settings.ALLOWED_HOSTS.split(",")
            if host.strip()
        ]
    
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=allowed_hosts,
    )


def setup_gzip(app: FastAPI) -> None:
    """Configure GZip middleware."""
    app.add_middleware(
        GZipMiddleware,
        minimum_size=1000,  # Only compress responses larger than 1KB
    )


def setup_security_headers(app: FastAPI) -> None:
    """Add security headers to all responses."""
    app.add_middleware(SecurityHeadersMiddleware)


def setup_request_logging(app: FastAPI) -> None:
    """Add request logging middleware."""
    app.add_middleware(RequestLoggingMiddleware)


def setup_rate_limiting(app: FastAPI) -> None:
    """Add rate limiting middleware."""
    if not settings.DEBUG:  # Only enable rate limiting in production
        app.add_middleware(
            RateLimitMiddleware,
            limit=settings.RATE_LIMIT,
            window=settings.RATE_LIMIT_WINDOW,
        )


def setup_middleware(app: FastAPI) -> None:
    """Set up all middleware for the application."""
    setup_cors(app)
    setup_trusted_hosts(app)
    setup_gzip(app)
    setup_security_headers(app)
    setup_request_logging(app)
    setup_rate_limiting(app)
