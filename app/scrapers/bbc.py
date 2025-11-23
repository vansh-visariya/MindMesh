import asyncio
import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class BBCScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="BBC News", base_url="https://www.bbc.com")

    async def scrape(self) -> List[ScrapedArticle]:
        articles = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article links - this selector needs to be robust
                # BBC structure changes, but usually they have 'h2' with links
                # This is a simplified example and might need adjustment based on actual HTML
                for article_tag in soup.find_all('div', {'data-testid': 'card-text-wrapper'}):
                    link_tag = article_tag.find_parent('a') # Often the card is wrapped in an 'a' or has an 'a' inside
                    if not link_tag:
                         # Try finding 'a' inside
                         link_tag = article_tag.find('a')
                    
                    if not link_tag:
                        # Try finding the closest 'a' tag if the wrapper isn't one
                         link_tag = article_tag.find_previous('a')

                    # Fallback: Look for specific class names common on BBC
                    # This part is tricky without live inspection. 
                    # Let's try a more generic approach for headlines
                
                # Better approach for BBC: Look for h2 tags which usually contain headlines
                for h2 in soup.find_all('h2', {'data-testid': 'card-headline'}):
                    title = h2.get_text(strip=True)
                    link_tag = h2.find_parent('a')
                    if not link_tag:
                        continue
                        
                    href = link_tag.get('href')
                    if not href:
                        continue
                        
                    if not href.startswith('http'):
                        url = self.base_url + href
                    else:
                        url = href

                    # Skip video/live pages if needed, or keep them
                    if '/av/' in url or '/live/' in url:
                        continue

                    # Now fetch the article content
                    # We should probably limit concurrency here or do it in a separate step
                    # For MVP, let's just get the list first, or fetch content for top 5
                    
                    # For now, let's just return the metadata we found on the homepage
                    # Fetching full content for every article on homepage might be slow/blocked
                    # We will implement a detail fetcher later or loop here
                    
                    # Fetch full content
                    content = await self.scrape_article_content(url)
                    
                    articles.append(ScrapedArticle(
                        title=title,
                        content=content,
                        source=self.source_name,
                        url=url,
                        published_at=datetime.now() # Placeholder
                    ))
                    
            except Exception as e:
                print(f"Error scraping BBC: {e}")
                
        return articles

    async def scrape_article_content(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                # BBC article content is usually in <article> tags or specific divs
                article_body = soup.find('article')
                if article_body:
                    paragraphs = article_body.find_all('p')
                    text = " ".join([p.get_text(strip=True) for p in paragraphs])
                    return text
                return ""
            except Exception:
                return ""
