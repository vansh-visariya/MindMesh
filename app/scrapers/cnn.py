import httpx
from bs4 import BeautifulSoup
from typing import List
from datetime import datetime
from app.scrapers.base_scraper import BaseScraper, ScrapedArticle

class CNNScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="CNN", base_url="https://edition.cnn.com/")

    async def scrape(self) -> List[ScrapedArticle]:
        articles = []
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(self.base_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # CNN uses specific classes for headlines. 
                # 'container__headline-text' is a common one.
                for span in soup.find_all('span', {'class': 'container__headline-text'}):
                    title = span.get_text(strip=True)
                    link_tag = span.find_parent('a')
                    if not link_tag:
                        continue
                        
                    href = link_tag.get('href')
                    if not href:
                        continue
                        
                    if not href.startswith('http'):
                        url = self.base_url + href
                    else:
                        url = href

                    content = await self.scrape_article_content(url)

                    articles.append(ScrapedArticle(
                        title=title,
                        content=content,
                        source=self.source_name,
                        url=url,
                        published_at=datetime.now()
                    ))
            except Exception as e:
                print(f"Error scraping CNN: {e}")
                
        return articles

    async def scrape_article_content(self, url: str) -> str:
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                soup = BeautifulSoup(response.content, 'html.parser')
                # CNN content is often in 'article__content' or 'zn-body__paragraph'
                # Modern CNN uses 'article__content'
                article_body = soup.find('div', class_='article__content')
                if not article_body:
                     article_body = soup.find('div', class_='zn-body__paragraph')
                
                if article_body:
                    paragraphs = article_body.find_all('p')
                    text = " ".join([p.get_text(strip=True) for p in paragraphs])
                    return text.strip()
                
                # Fallback for some layouts
                paragraphs = soup.find_all('p', class_='paragraph')
                if paragraphs:
                     text = " ".join([p.get_text(strip=True) for p in paragraphs])
                     return text.strip()

                return ""
            except Exception:
                return ""
