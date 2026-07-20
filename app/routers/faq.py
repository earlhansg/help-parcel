"""FAQ API endpoints."""
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Response
import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Union
from pydantic import BaseModel

from app.core.redis_client import db
from app.models import ErrorResponse
from app.models import Faq, FaqId, FaqWithScore
from app.services.faq_service import FaqService

class FaqCreate(BaseModel):
    question: str
    answer: str
    embedding: str

router = APIRouter(
    prefix="/faq",
    tags=["faq"]
)

faq_service = FaqService(db)

@router.post("/", response_model=Faq)
@router.post("", response_model=Faq)  # Handle both /faq and /faq/ 
async def create_item(faq_data: FaqCreate):
    # create a new item and return it
    return await faq_service.create(
        question=faq_data.question,
        answer=faq_data.answer,
        embedding=faq_data.embedding,
    )


# @router.get(
#     "/",
#     response_model=Dict[str, str],
#     responses={
#         500: {"description": "Internal server error", "model": ErrorResponse},
#     }
# )
# async def get_faq_status(
#     client: redis.Redis = Depends(get_redis_client)
# ) -> Dict[str, str]:
#     """
#     Get FAQ API status and basic information.
    
#     This is a placeholder endpoint for the future FAQ functionality.
    
#     Returns:
#         Dict with FAQ API status information
#     """
#     try:
#         # Test Redis connectivity for FAQ operations
#         await client.ping()
#         return {
#             "status": "ready",
#             "message": "FAQ API is ready for implementation",
#             "redis_status": "connected"
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"FAQ service error: {str(e)}"
#         )


# @router.get(
#     "/search",
#     response_model=Dict[str, Any],
#     responses={
#         500: {"description": "Internal server error", "model": ErrorResponse},
#     }
# )
# async def search_faq(
#     query: str = "",
#     client: redis.Redis = Depends(get_redis_client)
# ) -> Dict[str, Any]:
#     """
#     Search FAQ entries (placeholder implementation).
    
#     Args:
#         query: Search query string
#         client: Redis client dependency
        
#     Returns:
#         Dict with search results (placeholder data)
#     """
#     try:
#         # Placeholder implementation for FAQ search
#         return {
#             "query": query,
#             "results": [],
#             "message": "FAQ search functionality will be implemented here",
#             "total_results": 0
#         }
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"FAQ search error: {str(e)}"
#         )