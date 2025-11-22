from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    article_id: int
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/", response_model=ChatResponse)
async def chat_with_article(request: ChatRequest):
    # Stub implementation for now
    return {"answer": f"This is a placeholder answer for question: '{request.question}' regarding article {request.article_id}. AI integration coming in Phase 3."}
