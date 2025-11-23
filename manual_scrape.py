import asyncio
from app.db.database import AsyncSessionLocal
from app.scrapers.scraper_manager import run_all_scrapers

async def main():
    async with AsyncSessionLocal() as db:
        await run_all_scrapers(db)

if __name__ == "__main__":
    asyncio.run(main())
