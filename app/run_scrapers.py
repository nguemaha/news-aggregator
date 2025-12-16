import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List
from app.config import YOUTUBE_CHANNELS
from app.scrapers.youtube import YouTubeScraper, ChannelVideo
from app.scrapers.openai import OpenAIScraper, OpenAIArticle
from app.scrapers.anthropic import AnthropicScraper, AnthropicArticle
from app.scrapers.who import WHOScraper, WHOArticle
from app.database.repository import Repository


def scrape_youtube(hours: int, repo: Repository) -> List[ChannelVideo]:
    """
    Scrape YouTube videos from configured channels and save to database.
    
    :param hours: Number of hours to look back for videos
    :param repo: Repository instance for database operations
    :return: List of ChannelVideo objects that were scraped
    """
    scraper = YouTubeScraper()
    youtube_videos: List[ChannelVideo] = []
    video_dicts = []
    
    for channel_id in YOUTUBE_CHANNELS:
        videos = scraper.get_latest_videos(channel_id, hours=hours)
        youtube_videos.extend(videos)
        video_dicts.extend([
            {
                "video_id": v.video_id,
                "title": v.title,
                "url": v.url,
                "channel_id": channel_id,
                "published_at": v.published_at,
                "description": v.description,
                "transcript": v.transcript
            }
            for v in videos
        ])
    
    if video_dicts:
        repo.bulk_create_youtube_videos(video_dicts)
    
    return youtube_videos


def scrape_openai(hours: int, repo: Repository) -> List[OpenAIArticle]:
    """
    Scrape OpenAI articles and save to database.
    
    :param hours: Number of hours to look back for articles
    :param repo: Repository instance for database operations
    :return: List of OpenAIArticle objects that were scraped
    """
    scraper = OpenAIScraper()
    articles = scraper.get_articles(hours=hours)
    
    if articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in articles
        ]
        repo.bulk_create_openai_articles(article_dicts)
    
    return articles


def scrape_anthropic(hours: int, repo: Repository) -> List[AnthropicArticle]:
    """
    Scrape Anthropic articles and save to database.
    
    :param hours: Number of hours to look back for articles
    :param repo: Repository instance for database operations
    :return: List of AnthropicArticle objects that were scraped
    """
    scraper = AnthropicScraper()
    articles = scraper.get_articles(hours=hours)
    
    if articles:
        article_dicts = [
            {
                "guid": a.guid,
                "title": a.title,
                "url": a.url,
                "published_at": a.published_at,
                "description": a.description,
                "category": a.category
            }
            for a in articles
        ]
        repo.bulk_create_anthropic_articles(article_dicts)
    
    return articles


def scrape_who(hours: int, repo: Repository) -> List[WHOArticle]:
    """
    Scrape WHO articles and save to database.
    Ensures Selenium WebDriver is properly closed after scraping.
    
    :param hours: Number of hours to look back for articles
    :param repo: Repository instance for database operations
    :return: List of WHOArticle objects that were scraped
    """
    scraper = WHOScraper()
    articles: List[WHOArticle] = []
    
    try:
        articles = scraper.scrape_all(hours=hours)
        
        if articles:
            article_dicts = [
                {
                    "guid": a.guid,
                    "title": a.title,
                    "url": a.url,
                    "published_at": a.published_at,
                    "description": a.description,
                    "category": a.category
                }
                for a in articles
            ]
            repo.bulk_create_who_articles(article_dicts)
    finally:
        # Ensure the Selenium WebDriver is always cleaned up
        scraper.close()
    
    return articles


def run_scrapers(hours: int = 24) -> dict:
    """
    Orchestrate scraping from all configured sources and save results to database.
    
    :param hours: Number of hours to look back for content (default: 24)
    :return: Dictionary with keys 'youtube', 'openai', 'anthropic', 'who' containing
             lists of scraped content objects
    """
    repo = Repository()
    
    youtube_videos = scrape_youtube(hours=hours, repo=repo)
    openai_articles = scrape_openai(hours=hours, repo=repo)
    anthropic_articles = scrape_anthropic(hours=hours, repo=repo)
    who_articles = scrape_who(hours=hours, repo=repo)
    
    return {
        "youtube": youtube_videos,
        "openai": openai_articles,
        "anthropic": anthropic_articles,
        "who": who_articles,
    }


if __name__ == "__main__":
    results = run_scrapers(hours=72)
    print(f"YouTube videos: {len(results['youtube'])}")
    print(f"OpenAI articles: {len(results['openai'])}")
    print(f"Anthropic articles: {len(results['anthropic'])}")
    print(f"WHO articles: {len(results['who'])}")


