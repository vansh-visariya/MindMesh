import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class TOIScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="Times of India", base_url="https://timesofindia.indiatimes.com")

    async def scrape(self) -> List[ScrapedArticle]:
        articles = []
        async with httpx.AsyncClient() as client:
            try:
                headers = {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                }
                response = await client.get(self.base_url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # TOI structure is complex and changes. 
                # Look for figcaption or specific classes
                for figcaption in soup.find_all('figcaption'):
                    link_tag = figcaption.find('a')
                    if not link_tag:
                        continue
                    
                    title = link_tag.get_text(strip=True)
                    href = link_tag.get('href')
                    
                    if not href:
                        continue

                    if not href.startswith('http'):
                        url = href # TOI sometimes has relative, sometimes absolute. 
                        # Actually TOI relative links might be tricky.
                        if href.startswith('/'):
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
                print(f"Error scraping TOI: {e}")
                
        return articles
