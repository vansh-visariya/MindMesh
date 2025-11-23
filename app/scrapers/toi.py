import httpx
import feedparser
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle
from email.utils import parsedate_to_datetime

class TOIScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            source_name="Times of India",
            base_url="https://timesofindia.indiatimes.com",
        )
        # RSS feed URL for TOI Top Stories
        self.rss_url = "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"

    async def scrape(self) -> List[ScrapedArticle]:
        articles: List[ScrapedArticle] = []

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(self.rss_url)
                response.raise_for_status()
                feed = feedparser.parse(response.text)

                for entry in feed.entries:
                    title = entry.get("title", "No Title").strip()
                    url = entry.get("link", "").strip()
                    published_str = entry.get("published", None)
                    published_at = (
                        parsedate_to_datetime(published_str)
                        if published_str
                        else datetime.now()
                    )

                    content = await self.scrape_article_content(url)

                    articles.append(
                        ScrapedArticle(
                            title=title,
                            content=content,
                            source=self.source_name,
                            url=url,
                            published_at=published_at,
                        )
                    )

            except Exception as e:
                print(f"Error scraping TOI RSS: {e}")

        return articles

    async def scrape_article_content(self, url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0 Safari/537.36"
            )
        }

        async with httpx.AsyncClient(timeout=10) as client:
            try:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                # Use minimal HTML parsing to get article body
                from bs4 import BeautifulSoup

                soup = BeautifulSoup(response.text, "html.parser")

                # Try multiple possible containers
                body = (
                    soup.find("div", {"class": "_s30J"}) or
                    soup.find("div", {"class": "ga-headlines"}) or
                    soup.find("div", {"class": "Normal"})
                )

                if not body:
                    return "Content not found"

                paragraphs = body.find_all(["p", "div"])
                text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
                return text.strip() if text else "Content not found"

            except Exception:
                return "Error fetching content"
