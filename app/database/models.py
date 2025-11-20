from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class WHOArticle(Base):
    __tablename__ = "who_news"
    
    article_id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    release_date = Column(DateTime, nullable=False)
    full_text = Column(Text, nullable=False)
    article_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Digest(Base):
    __tablename__ = "digests"

    id = Column(String, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    release_date = Column(DateTime, nullable=False)
    summary = Column(Text, nullable=False)
    article_type = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    