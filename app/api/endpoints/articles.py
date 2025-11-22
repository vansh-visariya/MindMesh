from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.db.database import get_db
from app.db.models import Article
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class ArticleResponse(BaseModel):
    id: int
    title: str
    content: str
    source: str
    url: str
    published_at: Optional[datetime]
    created_at: datetime

    class Config:
        orm_mode = True

@router.get("/", response_model=List[ArticleResponse])
async def get_articles(
    source: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    query = select(Article).order_by(Article.published_at.desc()).offset(skip).limit(limit)
    
    if source:
        query = query.where(Article.source == source)
        
    result = await db.execute(query)
    articles = result.scalars().all()
    return articles
