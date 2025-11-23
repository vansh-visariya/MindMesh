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

                    content = await self.scrape_article_content(url)
                    
                    articles.append(ScrapedArticle(
                        title=title,
                        content=content,
                        source=self.source_name,
                        url=url,
                        published_at=datetime.now()
                    ))
            except Exception as e:
                print(f"Error scraping HT: {e}")
                
        return articles

    async def scrape_article_content(self, url: str) -> str:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/115.0 Safari/537.36"
            )
        }

        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")

                # Try multiple known HT containers
                article_container = (
                    soup.find("div", {"data-autom": "article-body"}) or
                    soup.find("div", class_="storyDetail") or
                    soup.find("div", class_="storyDetails") or
                    soup.find("section", {"id": "dataHolder"})
                )

                if not article_container:
                    return "Content not found"

                # Collect readable content
                texts = [
                    tag.get_text(" ", strip=True)
                    for tag in article_container.find_all(["p", "h2", "li"])
                ]

                content = " ".join(texts).strip()
                return content if content else "Content not found"

        except Exception as e:
            print(f"Error fetching content for {url}: {e}")
            return "Error fetching content"


