import asyncio
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup

from playwright.async_api import async_playwright

from app.scrapers.base_scraper import BaseScraper, ScrapedArticle


class ReutersScraper(BaseScraper):
    def __init__(self):
        super().__init__(source_name="Reuters", base_url="https://www.reuters.com")

    async def scrape(self) -> List[ScrapedArticle]:
        articles = []

        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(self.base_url, timeout=30000)
                html = await page.content()
                with open("reuters_dump.html", "w", encoding="utf-8") as f:
                    f.write(html)
                print("Saved HTML to reuters_dump.html")

                soup = BeautifulSoup(html, "html.parser")

                # --- Primary selector ---
                story_cards = soup.find_all(attrs={"data-testid": "MediaStoryCard"})

                # --- Fallback selector ---
                if not story_cards:
                    story_cards = soup.select('a[data-testid="Link"]')

                for card in story_cards:
                    # Extract URL
                    link = card if card.name == "a" else card.find("a", href=True)
                    if not link:
                        continue

                    href = link.get("href")
                    if not href:
                        continue

                    url = href if href.startswith("http") else self.base_url + href

                    # Extract headline
                    heading = (
                        card.find("h3") or
                        card.find(attrs={"data-testid": "Heading"}) or
                        link
                    )
                    title = heading.get_text(strip=True)

                    content = await self.scrape_article_content(url, browser)

                    articles.append(
                        ScrapedArticle(
                            title=title,
                            content=content,
                            source=self.source_name,
                            url=url,
                            published_at=datetime.now(),
                        )
                    )

            except Exception as e:
                print(f"Error scraping Reuters: {e}")

            finally:
                await browser.close()

        return articles


    async def scrape_article_content(self, url: str, browser) -> str:
        page = await browser.new_page()

        try:
            await page.goto(url, timeout=30000)
            html = await page.content()
            soup = BeautifulSoup(html, "html.parser")

            # Primary Reuters article body
            body = soup.find("div", class_=lambda c: c and "article-body__content" in c)
            if body:
                return " ".join(p.get_text(strip=True) for p in body.find_all("p"))

            # Fallback – main content area
            main = soup.find("main")
            if main:
                paragraphs = main.find_all("p")
                return " ".join(p.get_text(strip=True) for p in paragraphs)

            return ""

        except Exception:
            return ""

        finally:
            await page.close()
