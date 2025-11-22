import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class NYTScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="New York Times", base_url="https://www.nytimes.com")

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
                
                # NYT uses 'section' tags and 'p' or 'h3' for titles
                # A common class for story wrappers is 'story-wrapper'
                for story in soup.find_all('section', class_='story-wrapper'):
                    link_tag = story.find('a')
                    if not link_tag:
                        continue
                        
                    # Title might be in p or h3
                    title_tag = story.find(['h3', 'p'], class_='indicate-hover')
                    if not title_tag:
                         title_tag = story.find(['h3', 'p'])
                    
                    if not title_tag:
                        continue
                        
                    title = title_tag.get_text(strip=True)
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
                print(f"Error scraping NYT: {e}")
                
        return articles
