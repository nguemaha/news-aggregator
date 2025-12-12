from typing import Optional
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.scrapers.who import WHOScraper
from app.database.repository import Repository

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def process_who_news(hours: Optional[int] = 24) -> dict:
    """
    Scrape WHO news articles and save them to the database.
    
    :param hours: Number of hours to look back for articles (default: 24)
    :return: Dictionary with total, processed, and failed counts
    """
    scraper = WHOScraper(headless=True, wait_time=1)
    repo = Repository()
    
    try:
        logger.info(f"Starting WHO news scraping for articles from the past {hours} hours")
        articles = scraper.scrape_all(hours=hours)
        total = len(articles)
        
        if total == 0:
            logger.warning(f"No articles found from the past {hours} hours")
            return {
                "total": 0,
                "processed": 0,
                "failed": 0
            }
        
        logger.info(f"Scraped {total} articles, saving to database...")
        
        # Convert Pydantic models to dictionaries for bulk insert
        article_dicts = [
            {
                "guid": article.guid,
                "title": article.title,
                "url": article.url,
                "published_at": article.published_at,
                "description": article.description,
                "category": article.category
            }
            for article in articles
        ]
        
        # Use bulk create for efficiency
        processed = repo.bulk_create_who_articles(article_dicts)
        failed = total - processed
        
        logger.info(f"Processing complete: {processed} processed, {failed} failed out of {total} total")
        
        return {
            "total": total,
            "processed": processed,
            "failed": failed
        }
        
    except Exception as e:
        logger.error(f"Error scraping WHO news: {e}", exc_info=True)
        return {
            "total": 0,
            "processed": 0,
            "failed": 0
        }
    finally:
        # Always close the scraper to clean up browser resources
        scraper.close()


if __name__ == "__main__":
    result = process_who_news(hours=72)
    print(f"Total articles: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")