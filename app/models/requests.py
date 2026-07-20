"""Request models for API endpoints."""
from pydantic import BaseModel


class KeyRequest(BaseModel):
    """Request model for key lookup."""
    key: str