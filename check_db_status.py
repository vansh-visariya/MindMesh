import asyncio
from sqlalchemy import select, func
from app.db.database import AsyncSessionLocal
from app.db.models import Article

async def check_db():
    async with AsyncSessionLocal() as db:
        # Count articles
        result = await db.execute(select(func.count(Article.id)))
        count = result.scalar()
        print(f"Total articles in DB: {count}")
        
        # Show last 20 articles
        result = await db.execute(select(Article).order_by(Article.created_at.desc()).limit(20))
        articles = result.scalars().all()
        print(f"\nLatest {len(articles)} articles:")
        for a in articles:
            print(f"- [{a.source}] {a.title[:50]}... (Content Len: {len(a.content) if a.content else 0})")

if __name__ == "__main__":
    asyncio.run(check_db())
