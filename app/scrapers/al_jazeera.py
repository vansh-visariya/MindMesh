import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class AlJazeeraScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="Al Jazeera", base_url="https://www.aljazeera.com")

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
                
                # Al Jazeera uses 'h3' inside article tags usually
                for article in soup.find_all('article'):
                    h3 = article.find('h3')
                    if not h3:
                        continue
                        
                    link_tag = h3.find('a')
                    if not link_tag:
                        # Sometimes the a tag wraps the h3 or is elsewhere
                        link_tag = article.find('a')
                    
                    if not link_tag:
                        continue

                    title = h3.get_text(strip=True)
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
                print(f"Error scraping Al Jazeera: {e}")
                
        return articles
