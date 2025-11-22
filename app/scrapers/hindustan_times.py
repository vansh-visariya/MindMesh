import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class HTScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="Hindustan Times", base_url="https://www.hindustantimes.com")

    async def scrape(self) -> List[ScrapedArticle]:
        articles = []
        async with httpx.AsyncClient() as client:
            try:
                # HT often blocks simple requests, might need headers
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = await client.get(self.base_url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # HT headlines are often in h3 with class 'hdg3' or similar
                for h3 in soup.find_all(['h2', 'h3']):
                    link_tag = h3.find('a')
                    if not link_tag:
                        continue
                        
                    title = link_tag.get_text(strip=True)
                    if not title:
                        continue

                    href = link_tag.get('href')
                    if not href:
                        continue
                        
                    if not href.startswith('http'):
                        url = self.base_url + href
                    else:
                        url = href

                    articles.append(ScrapedArticle(
                        title=title,
                        content="",
                        source=self.source_name,
                        url=url,
                        published_at=datetime.now()
                    ))
            except Exception as e:
                print(f"Error scraping HT: {e}")
                
        return articles
