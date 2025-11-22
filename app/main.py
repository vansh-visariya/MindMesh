from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.database import engine, Base, AsyncSessionLocal
from app.scrapers.scraper_manager import run_all_scrapers

scheduler = AsyncIOScheduler()

async def scrape_job():
    async with AsyncSessionLocal() as db:
        await run_all_scrapers(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Start Scheduler
    scheduler.add_job(scrape_job, 'interval', hours=1) # Run every hour
    scheduler.start()
    
    yield
    
    # Shutdown Scheduler
    scheduler.shutdown()
    # Close connection on shutdown (optional, engine handles it)

app = FastAPI(title="Advance Web Scraper", lifespan=lifespan)

from app.api.endpoints import articles, chat

app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Advance Web Scraper API"}
