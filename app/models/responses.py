"""Response models for API endpoints."""
from pydantic import BaseModel


class KeyResponse(BaseModel):
    """Response model for key retrieval."""
    key: str
    value: str
    status: str = "success"


class ErrorResponse(BaseModel):
    """Response model for errors."""
    error: str
    status: str = "error"