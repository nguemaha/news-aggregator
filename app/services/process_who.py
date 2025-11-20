from typing import Optional

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))


from app.scrapers.who import WHOScraper
from app.database.repository import Repository


def download_and_load_who_news(hours: Optional[int] = 24) -> dict:
    scraper = WHOScraper(headless=True, wait_time=1)
    repo = Repository()

    try:
        articles = scraper.scrape_all(hours=hours)  
    except Exception as e:
        print(f"Error scraping WHO news: {e}")
      
    #repo.bulk_create_who_articles(articles)
    processed = 0 ; failed = 0; total = len(articles)
    for article_data in articles:
        try:
            repo.create_who_article(
                article_id = article_data.article_id, 
                title = article_data.title, 
                url = article_data.url, 
                release_date = article_data.release_date, 
                article_type = article_data.article_type, 
                full_text = article_data.full_text
            )
            processed += 1
        except Exception as e:
            print(f"Error processing article {article_data.article_id}: {e}")
            failed += 1

    return {
        "total": total,
        "processed": processed,
        "failed": failed
    }


if __name__ == "__main__":
    result = download_and_load_who_news()
    print(f"Total articles: {result['total']}")
    print(f"Processed: {result['processed']}")
    print(f"Failed: {result['failed']}")

