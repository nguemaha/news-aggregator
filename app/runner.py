import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List
from app.config import YOUTUBE_CHANNELS
from app.scrapers.who import WHOScraper, WHOArticle
from app.database.repository import Repository


def run_scrapers(hours: int = 24) -> dict:
    who_scraper = WHOScraper()
    repo = Repository()
    
    who_articles = who_scraper.scrape_all(hours=hours)
  
    if who_articles:
        article_dicts = [
            {
                "article_id": a.article_id,
                "title": a.title,
                "url": a.url,
                "release_date": a.release_date,
                "full_text": a.full_text,
                "article_type": a.article_type
            }
            for a in who_articles
        ]
        repo.bulk_create_who_articles(article_dicts)
    
    return {
        "who": who_articles,
    }


if __name__ == "__main__":
    results = run_scrapers(hours=24)
    
    print(f"WHO articles: {len(results['who'])}")
    
