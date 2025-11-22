from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class ScrapedArticle(BaseModel):
    title: str
    content: str
    source: str
    url: str
    published_at: Optional[datetime] = None
    author: Optional[str] = None

class BaseScraper(ABC):
    def __init__(self, source_name: str, base_url: str):
        self.source_name = source_name
        self.base_url = base_url

    @abstractmethod
    async def scrape(self) -> List[ScrapedArticle]:
        """
        Scrapes the news source and returns a list of ScrapedArticle objects.
        """
        pass
