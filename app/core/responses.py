"""
Standardized API response utilities for consistent response formatting.
"""
from typing import Any, Dict, List, Optional, Union
from flask import jsonify
from flask.wrappers import Response


class APIResponse:
    """Standardized API response class."""
    
    @staticmethod
    def success(
        data: Any = None,
        message: str = "Success",
        status_code: int = 200,
        meta: Optional[Dict[str, Any]] = None
    ) -> Response:
        """Create a successful response."""
        response_data = {
            "success": True,
            "message": message,
            "data": data
        }
        
        if meta:
            response_data["meta"] = meta
            
        return jsonify(response_data), status_code
    
    @staticmethod
    def error(
        message: str = "An error occurred",
        error_code: str = "ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None
    ) -> Response:
        """Create an error response."""
        response_data = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message
            }
        }
        
        if details:
            response_data["error"]["details"] = details
            
        return jsonify(response_data), status_code
    
    @staticmethod
    def paginated(
        data: List[Any],
        page: int,
        per_page: int,
        total: int,
        message: str = "Success"
    ) -> Response:
        """Create a paginated response."""
        total_pages = (total + per_page - 1) // per_page
        
        meta = {
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }
        
        return APIResponse.success(
            data=data,
            message=message,
            meta=meta
        )
    
    @staticmethod
    def created(
        data: Any = None,
        message: str = "Resource created successfully",
        resource_id: Optional[Union[str, int]] = None
    ) -> Response:
        """Create a resource creation response."""
        meta = {}
        if resource_id:
            meta["resource_id"] = resource_id
            
        return APIResponse.success(
            data=data,
            message=message,
            status_code=201,
            meta=meta if meta else None
        )
    
    @staticmethod
    def no_content(message: str = "Operation completed successfully") -> Response:
        """Create a no content response."""
        return APIResponse.success(
            message=message,
            status_code=204
        )
    
    @staticmethod
    def not_found(resource: str = "Resource", identifier: str = "") -> Response:
        """Create a not found response."""
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier '{identifier}'"
            
        return APIResponse.error(
            message=message,
            error_code="NOT_FOUND",
            status_code=404
        )
    
    @staticmethod
    def validation_error(errors: Dict[str, List[str]]) -> Response:
        """Create a validation error response."""
        return APIResponse.error(
            message="Validation failed",
            error_code="VALIDATION_ERROR",
            status_code=422,
            details={"errors": errors}
        )
    
    @staticmethod
    def unauthorized(message: str = "Authentication required") -> Response:
        """Create an unauthorized response."""
        return APIResponse.error(
            message=message,
            error_code="UNAUTHORIZED",
            status_code=401
        )
    
    @staticmethod
    def forbidden(message: str = "Access denied") -> Response:
        """Create a forbidden response."""
        return APIResponse.error(
            message=message,
            error_code="FORBIDDEN",
            status_code=403
        )
    
    @staticmethod
    def conflict(message: str = "Resource already exists") -> Response:
        """Create a conflict response."""
        return APIResponse.error(
            message=message,
            error_code="CONFLICT",
            status_code=409
        )
    
    @staticmethod
    def internal_error(message: str = "Internal server error") -> Response:
        """Create an internal server error response."""
        return APIResponse.error(
            message=message,
            error_code="INTERNAL_ERROR",
            status_code=500
        )
    
    @staticmethod
    def rate_limited(retry_after: Optional[int] = None) -> Response:
        """Create a rate limit exceeded response."""
        details = {}
        if retry_after:
            details["retry_after"] = retry_after
            
        return APIResponse.error(
            message="Rate limit exceeded",
            error_code="RATE_LIMITED",
            status_code=429,
            details=details if details else None
        )
