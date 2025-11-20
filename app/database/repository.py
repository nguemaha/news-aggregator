from datetime import datetime, timedelta, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from .models import WHOArticle, Digest
from .connection import get_session


class Repository:
    def __init__(self, session: Optional[Session] = None):
        self.session = session or get_session()
    
    def create_who_article(self, article_id: str, title: str, url: str, release_date: datetime,
                          article_type: Optional[str] = None,
                          full_text: Optional[str] = None) -> Optional[WHOArticle]:
        existing = self.session.query(WHOArticle).filter_by(article_id=article_id).first()      
        if existing:
            return None
        article = WHOArticle(
            article_id=article_id,
            title=title,
            url=url,
            release_date=release_date,
            article_type=article_type,
            full_text=full_text
        )
        self.session.add(article)
        self.session.commit()
        return article
    
    def bulk_create_who_articles(self, articles: List[dict]) -> int:
        new_articles = []
        for a in articles:
            existing = self.session.query(WHOArticle).filter_by(article_id=a["article_id"]).first()
            if not existing:
                new_articles.append(WHOArticle(
                    article_id=a["article_id"],
                    title=a["title"],
                    url=a["url"],
                    release_date=a["release_date"],
                    article_type=a.get("article_type"),
                    full_text=a.get("full_text")
                ))
        if new_articles:
            self.session.add_all(new_articles)
            self.session.commit()
        return len(new_articles)
    
    def get_who_articles(self, limit: Optional[int] = None, hours: Optional[int] = None) -> List[WHOArticle]:
        query = self.session.query(WHOArticle)
        
        if hours:
            cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
            query = query.filter(WHOArticle.release_date >= cutoff_time)
        
        query = query.order_by(WHOArticle.release_date.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_who_article_by_id(self, article_id: str) -> Optional[WHOArticle]:
        return self.session.query(WHOArticle).filter_by(article_id=article_id).first()
    
    def update_who_article(self, article_id: str, **kwargs) -> bool:
        article = self.session.query(WHOArticle).filter_by(article_id=article_id).first()
        if article:
            for key, value in kwargs.items():
                if hasattr(article, key):
                    setattr(article, key, value)
            self.session.commit()
            return True
        return False

    
    def create_digest(self, article_id: str, title: str,  url: str, release_date:datetime, article_type: str, 
            summary: str, published_at: Optional[datetime] = None) -> Optional[Digest]:
        digest_id = f"{article_type}:{article_id}"
        existing = self.session.query(Digest).filter_by(id=digest_id).first()
        if existing:
            return None
       
        if published_at:
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            created_at = published_at
        else:
            created_at = datetime.now(timezone.utc)
        
        digest = Digest(
            id=digest_id,
            title=title,
            url=url,
            release_date=release_date,
            article_type=article_type,
            summary=summary,
            created_at = created_at
        )
        
        self.session.add(digest)
        self.session.commit()
        return digest
    
    def get_recent_digests(self, hours: int = 24) -> List[Dict[str, Any]]:
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=hours)
        digests = self.session.query(Digest).filter(
            Digest.created_at >= cutoff_time
        ).order_by(Digest.created_at.desc()).all()
        
        return [
            {
                "id": d.id,
                "article_type": d.article_type,
                "url": d.url,
                "title": d.title,
                "summary": d.summary,
                "created_at": d.created_at
            }
            for d in digests
        ]
