import asyncio
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import Article
from app.scrapers.bbc import BBCScraper
from app.scrapers.cnn import CNNScraper
from app.scrapers.hindustan_times import HTScraper
from app.scrapers.reuters import ReutersScraper
from app.scrapers.nyt import NYTScraper
from app.scrapers.al_jazeera import AlJazeeraScraper
from app.scrapers.toi import TOIScraper

SCRAPERS = [
    BBCScraper(),
    CNNScraper(),
    HTScraper(),
    ReutersScraper(),
    NYTScraper(),
    AlJazeeraScraper(),
    TOIScraper()
]

async def run_all_scrapers(db: AsyncSession):
    print("Starting scrape cycle...")
    for scraper in SCRAPERS:
        print(f"Running {scraper.source_name} scraper...")
        try:
            articles = await scraper.scrape()
            print(f"Found {len(articles)} articles from {scraper.source_name}")
            
            for scraped_article in articles:
                # Check if article already exists
                result = await db.execute(select(Article).where(Article.url == scraped_article.url))
                existing_article = result.scalars().first()
                
                if not existing_article:
                    new_article = Article(
                        title=scraped_article.title,
                        content=scraped_article.content,
                        source=scraped_article.source,
                        url=scraped_article.url,
                        published_at=scraped_article.published_at
                    )
                    db.add(new_article)
            
            await db.commit()
            print(f"Saved new articles from {scraper.source_name}")
            
        except Exception as e:
            print(f"Error running {scraper.source_name} scraper: {e}")
    print("Scrape cycle completed.")
