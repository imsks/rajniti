"""
Base schemas for common validation patterns.
"""
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class BaseSchema(BaseModel):
    """Base schema with common configuration."""
    
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        use_enum_values=True,
        extra="forbid"
    )


class PaginationSchema(BaseSchema):
    """Schema for pagination parameters."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    per_page: int = Field(default=20, ge=1, le=100, description="Items per page")


class ResponseMetaSchema(BaseSchema):
    """Schema for response metadata."""
    
    total: Optional[int] = Field(None, description="Total number of items")
    page: Optional[int] = Field(None, description="Current page number")
    per_page: Optional[int] = Field(None, description="Items per page")
    total_pages: Optional[int] = Field(None, description="Total number of pages")
    has_next: Optional[bool] = Field(None, description="Whether there is a next page")
    has_prev: Optional[bool] = Field(None, description="Whether there is a previous page")


class SuccessResponseSchema(BaseSchema):
    """Schema for successful API responses."""
    
    success: bool = Field(True, description="Success status")
    message: str = Field(description="Response message")
    data: Optional[Any] = Field(None, description="Response data")
    meta: Optional[ResponseMetaSchema] = Field(None, description="Response metadata")


class ErrorDetailSchema(BaseSchema):
    """Schema for error details."""
    
    code: str = Field(description="Error code")
    message: str = Field(description="Error message")
    details: Optional[dict] = Field(None, description="Additional error details")


class ErrorResponseSchema(BaseSchema):
    """Schema for error API responses."""
    
    success: bool = Field(False, description="Success status")
    error: ErrorDetailSchema = Field(description="Error information")
