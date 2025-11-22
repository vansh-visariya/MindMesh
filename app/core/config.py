import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Advance Web Scraper"
    PROJECT_VERSION: str = "1.0.0"
    
    # Database
    # Default to SQLite for local development
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    
    # AI
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY")

settings = Settings()
