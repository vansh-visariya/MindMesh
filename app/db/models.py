from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.db.database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    source = Column(String, index=True)
    url = Column(String, unique=True, index=True)
    published_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Article(title={self.title}, source={self.source})>"
