"""FAQ API endpoints."""
from fastapi import APIRouter, HTTPException, Form, UploadFile, File, Response
import redis.asyncio as redis
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any, Union

from app.core.redis_client import db
from app.models import ErrorResponse
from app.models import Faq, FaqId, FaqWithScore, FaqCreate, FaqSearchRequest
from app.services.embedding_service import EmbeddingService
from app.services.faq_service import FaqService

router = APIRouter(
    prefix="/faq",
    tags=["faq"]
)

# Create an instance of the EmbeddingService class
embedding_service = EmbeddingService()
faq_service = FaqService(db, embedding_service)

@router.post("/", response_model=Faq)
@router.post("", response_model=Faq)  # Handle both /faq and /faq/ 
async def create_item(faq_data: FaqCreate):
    # create a new item and return it
    return await faq_service.create(
        question=faq_data.question,
        answer=faq_data.answer,
        embedding=faq_data.embedding,
    )

# Updated search endpoint
@router.post("/search", response_model=List[FaqWithScore])
async def search_faqs(search_request: FaqSearchRequest):
    # search for FAQs based on the text query and return them
    return await faq_service.search_by_text(search_request.query)
