"""Health check and basic endpoints."""
from fastapi import APIRouter

router = APIRouter(
    tags=["health"]
)


@router.get("/hello-world")
def hello_world():
    """Simple hello world endpoint."""
    return {"message": "Hello, World!"}


@router.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "message": "API is running"
    }