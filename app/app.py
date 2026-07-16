from contextlib import asynccontextmanager
from typing import Optional

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel


# Global Redis client
redis_client: Optional[redis.Redis] = None


class KeyRequest(BaseModel):
    """Request model for key lookup"""
    key: str


class KeyResponse(BaseModel):
    """Response model for key retrieval"""
    key: str
    value: str
    status: str = "success"


class ErrorResponse(BaseModel):
    """Response model for errors"""
    error: str
    status: str = "error"


async def get_redis_client() -> redis.Redis:
    """Dependency to get Redis client"""
    if redis_client is None:
        raise HTTPException(
            status_code=500,
            detail="Redis client not initialized"
        )
    return redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for Redis connection"""
    global redis_client
    
    # Startup
    try:
        redis_client = redis.Redis(
            host="localhost",
            port=6379,
            db=0,
            decode_responses=True,  # Automatically decode responses to strings
            retry_on_timeout=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test the connection
        await redis_client.ping()
        print("✅ Redis connection established successfully")
    except redis.RedisError as e:
        print(f"❌ Failed to connect to Redis: {e}")
        redis_client = None
    
    yield
    
    # Shutdown
    if redis_client:
        await redis_client.aclose()
        print("✅ Redis connection closed")


app = FastAPI(
    title="Help Parcel API",
    description="FastAPI application with Redis integration",
    version="0.1.0",
    lifespan=lifespan
)


@app.get("/hello-world")
def hello_world():
    return {"message": "Hello, World!"}


@app.post(
    "/get-name",
    response_model=KeyResponse,
    responses={
        200: {"description": "Key retrieved successfully"},
        404: {"description": "Key not found", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse},
    }
)
async def get_value_from_redis(
    request: KeyRequest,
    client: redis.Redis = Depends(get_redis_client)
) -> KeyResponse:
    """
    Retrieve the value associated with the provided key from Redis.
    
    Args:
        request: KeyRequest containing the key to lookup
        
    Returns:
        KeyResponse: The key and value if found
        
    Raises:
        HTTPException: 404 if key not found, 500 for Redis errors
    """
    try:
        # Get the value from Redis using the provided key
        value = await client.get(request.key)
        
        if value is None:
            raise HTTPException(
                status_code=404,
                detail=f"Key '{request.key}' not found in Redis"
            )
        print(f"✅ Retrieved from Redis: {request.key} = {value}")
        return KeyResponse(key=request.key, value=value)
        
    except redis.RedisError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Redis operation failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        )