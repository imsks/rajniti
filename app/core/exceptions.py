"""
Custom exceptions for the Rajniti application.
"""
from typing import Any, Dict, Optional


class RajnitiException(Exception):
    """Base exception for all Rajniti-related errors."""
    
    def __init__(
        self, 
        message: str, 
        error_code: str = "RAJNITI_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(RajnitiException):
    """Raised when request validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="VALIDATION_ERROR",
            details={**(details or {}), "field": field} if field else details
        )


class DatabaseError(RajnitiException):
    """Raised when database operations fail."""
    
    def __init__(self, message: str, operation: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="DATABASE_ERROR",
            details={**(details or {}), "operation": operation} if operation else details
        )


class ScrapingError(RajnitiException):
    """Raised when scraping operations fail."""
    
    def __init__(self, message: str, url: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="SCRAPING_ERROR",
            details={**(details or {}), "url": url} if url else details
        )


class NotFoundError(RajnitiException):
    """Raised when requested resource is not found."""
    
    def __init__(self, resource: str, identifier: str, details: Optional[Dict[str, Any]] = None):
        message = f"{resource} with identifier '{identifier}' not found"
        super().__init__(
            message=message,
            error_code="NOT_FOUND",
            details={**(details or {}), "resource": resource, "identifier": identifier}
        )


class ConflictError(RajnitiException):
    """Raised when there's a conflict in resource creation."""
    
    def __init__(self, message: str, resource: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="CONFLICT",
            details={**(details or {}), "resource": resource} if resource else details
        )


class AuthenticationError(RajnitiException):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(RajnitiException):
    """Raised when authorization fails."""
    
    def __init__(self, message: str = "Access denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class RateLimitError(RajnitiException):
    """Raised when rate limit is exceeded."""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_ERROR",
            details={**(details or {}), "retry_after": retry_after} if retry_after else details
        )


class ExternalServiceError(RajnitiException):
    """Raised when external service calls fail."""
    
    def __init__(self, service: str, message: str, status_code: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=f"{service}: {message}",
            error_code="EXTERNAL_SERVICE_ERROR",
            details={**(details or {}), "service": service, "status_code": status_code}
        )
