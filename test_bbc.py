import asyncio
from app.scrapers.bbc import BBCScraper
from app.scrapers.cnn import CNNScraper
from app.scrapers.reuters import ReutersScraper
from app.scrapers.nyt import NYTScraper
from app.scrapers.al_jazeera import AlJazeeraScraper
from app.scrapers.hindustan_times import HTScraper
from app.scrapers.toi import TOIScraper

async def main():
    scraper = TOIScraper()
    print("Scraping...")
    articles = await scraper.scrape()
    print(f"Found {len(articles)} articles.")
    for article in articles[:3]:
        print(f"- {article.title} ({article.url})")
        # Test content fetching for the first one
        print("  Fetching content...")
        content = await scraper.scrape_article_content(article.url)
        print(f"  Content length: {len(content)}")
        print(f"  Preview: {content[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())
