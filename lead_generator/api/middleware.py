"""Middleware for the Lead Generator API.

This module provides middleware components for the API layer, including:
- Rate limiting
- Request logging
- Error handling
"""

import time
from typing import Dict, Callable, Awaitable, Optional, Tuple
from datetime import datetime, timedelta
import logging
from fastapi import FastAPI, Request, Response, status, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Configure logging
logger = logging.getLogger(__name__)

class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware that limits requests based on client IP address.
    
    Implements a sliding window rate limiting algorithm to prevent abuse.
    """
    
    def __init__(self, app: FastAPI, requests_per_minute: int = 60):
        """
        Initialize the rate limiter.
        
        Args:
            app: FastAPI application
            requests_per_minute: Maximum number of requests allowed per minute
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_records: Dict[str, list] = {}  # IP -> list of timestamps
        self.cleanup_interval = 5 * 60  # Clean old entries every 5 minutes
        self.last_cleanup = datetime.now()
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process the request and apply rate limiting.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response from the API
        """
        # Get client IP - consider X-Forwarded-For for proxies
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Use the first IP if multiple are present
            client_ip = forwarded_for.split(",")[0].strip()
        
        # Clean old records periodically
        now = datetime.now()
        if (now - self.last_cleanup).total_seconds() > self.cleanup_interval:
            self._cleanup_old_records()
            self.last_cleanup = now
        
        # Check rate limit
        is_rate_limited, retry_after = self._is_rate_limited(client_ip)
        if is_rate_limited:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": retry_after
                },
            )
        
        # Record this request
        if client_ip not in self.request_records:
            self.request_records[client_ip] = []
        self.request_records[client_ip].append(datetime.now())
        
        # Process the request
        return await call_next(request)
    
    def _is_rate_limited(self, client_ip: str) -> Tuple[bool, Optional[int]]:
        """
        Check if the client has exceeded the rate limit.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Tuple of (is_limited, retry_after_seconds)
        """
        if client_ip not in self.request_records:
            return False, None
            
        # Get requests in the last minute
        now = datetime.now()
        minute_ago = now - timedelta(minutes=1)
        
        # Filter recent requests
        recent_requests = [
            timestamp for timestamp in self.request_records[client_ip] 
            if timestamp > minute_ago
        ]
        
        # Update the list with only recent requests
        self.request_records[client_ip] = recent_requests
        
        # Check if rate limit is exceeded
        if len(recent_requests) >= self.requests_per_minute:
            # Calculate when they can retry (oldest timestamp + 1 minute)
            oldest = min(recent_requests)
            retry_after = int((oldest + timedelta(minutes=1) - now).total_seconds())
            retry_after = max(1, retry_after)  # At least 1 second
            return True, retry_after
            
        return False, None
    
    def _cleanup_old_records(self) -> None:
        """
        Clean up old request records to prevent memory growth.
        Removes records older than 1 hour.
        """
        hour_ago = datetime.now() - timedelta(hours=1)
        for ip in list(self.request_records.keys()):
            # Keep only records from the last hour
            self.request_records[ip] = [
                timestamp for timestamp in self.request_records[ip] 
                if timestamp > hour_ago
            ]
            
            # Remove empty entries
            if not self.request_records[ip]:
                del self.request_records[ip]
        
        logger.debug(f"Cleaned rate limiter records. Active IPs: {len(self.request_records)}")


class RequestLogger(BaseHTTPMiddleware):
    """
    Middleware for logging request information.
    
    Logs detailed information about each request including:
    - Method
    - Path
    - Status code
    - Processing time
    - Client IP
    """
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process the request and log details.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response from the API
        """
        start_time = time.time()
        client_ip = request.client.host
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
            
        # Log request details
        logger.info(f"Request: {request.method} {request.url.path} from {client_ip}")
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log response details
        logger.info(
            f"Response: {request.method} {request.url.path} {response.status_code} "
            f"Took: {process_time:.3f}s Client: {client_ip}"
        )
        
        # Add server timing header
        response.headers["X-Process-Time"] = f"{process_time:.3f}s"
        
        return response


class ErrorHandler(BaseHTTPMiddleware):
    """
    Error handling middleware for providing secure and consistent error responses.
    
    In production mode, hides detailed error information to prevent information leakage.
    """
    
    def __init__(self, app: FastAPI, debug: bool = False):
        """
        Initialize the error handler.
        
        Args:
            app: FastAPI application
            debug: Whether to show detailed error information
        """
        super().__init__(app)
        self.debug = debug
    
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        """
        Process the request and handle any exceptions.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or endpoint
            
        Returns:
            Response from the API
        """
        try:
            return await call_next(request)
        except Exception as exc:
            # Log the exception with details
            logger.exception(f"Unhandled exception: {str(exc)}")
            
            # Extract request path for the error response
            path = request.url.path
            
            # Check for HTTPException which already has status_code and detail
            if isinstance(exc, HTTPException):
                return JSONResponse(
                    status_code=exc.status_code,
                    content={
                        "detail": exc.detail,
                        "status_code": exc.status_code,
                        "timestamp": datetime.now().isoformat(),
                        "path": path
                    }
                )
            
            # Determine if we should show detailed error information
            if self.debug:
                error_detail = str(exc)
                # Include error type in debug mode
                error_type = type(exc).__name__
                content = {
                    "detail": error_detail,
                    "error_type": error_type,
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "timestamp": datetime.now().isoformat(),
                    "path": path
                }
            else:
                # Generic error message in production
                content = {
                    "detail": "An unexpected error occurred",
                    "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "timestamp": datetime.now().isoformat(),
                    "path": path
                }
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content=content
            )


def add_middleware(app: FastAPI, rate_limit: int = 60, debug: bool = False) -> None:
    """
    Add all middleware to the FastAPI application.
    
    Args:
        app: FastAPI application
        rate_limit: Number of requests allowed per minute
        debug: Whether to show detailed error information
    """
    # Add request logger - should be first to capture all requests
    app.add_middleware(RequestLogger)
    
    # Add error handler - should be before rate limiter to catch its exceptions
    app.add_middleware(ErrorHandler, debug=debug)
    
    # Add rate limiter
    app.add_middleware(RateLimiter, requests_per_minute=rate_limit) 