from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel
from app.db.database import get_db
from app.db.models import Article
from app.services.ai_service import ai_service

router = APIRouter()

class ChatRequest(BaseModel):
    article_id: int
    question: str

class ChatResponse(BaseModel):
    answer: str

@router.post("/", response_model=ChatResponse)
async def chat_with_article(request: ChatRequest, db: AsyncSession = Depends(get_db)):
    # Fetch article
    result = await db.execute(select(Article).where(Article.id == request.article_id))
    article = result.scalars().first()
    
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    # Generate answer using AI
    # Note: In a real app, we might want to fetch content if it's empty or just summary
    # But our scrapers should have populated it.
    # If content is empty, we can't answer.
    
    answer = await ai_service.generate_answer(article.content, request.question)
    
    return {"answer": answer}
