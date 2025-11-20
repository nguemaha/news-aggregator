from __future__ import annotations

import time
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from bs4 import BeautifulSoup
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, TimeoutException


class WHOArticle(BaseModel):
    article_id: str
    title: str
    url: str
    release_date: datetime
    article_type: Optional[str] = None
    full_text: str  # required


class WHOScraper:
    BASE_URL = "https://www.who.int"
    NEWS_URL = f"{BASE_URL}/news"

    def __init__(self, headless: bool = True, wait_time: int = 5):
        """
        :param headless: Run browser in headless mode (no UI).
        :param wait_time: Seconds to wait after loading pages, for JS to finish.
        """
        self.wait_time = wait_time
        self.driver = self._init_driver(headless)

    def _init_driver(self, headless: bool) -> webdriver.Chrome:
        """Initialize the Selenium Chrome driver with basic safety checks."""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")

        try:
            driver = webdriver.Chrome(options=chrome_options)
        except WebDriverException as e:
            raise RuntimeError(
                "Failed to initialize Chrome WebDriver. "
                "Ensure ChromeDriver is installed and on your PATH."
            ) from e

        return driver

    @staticmethod
    def _generate_article_id(url: str) -> str:
        """
        Generate a deterministic unique ID from the article URL.

        Using UUIDv5 so the same URL always produces the same ID.
        """
        return str(uuid.uuid5(uuid.NAMESPACE_URL, url))

    @staticmethod
    def _parse_release_date(date_text: str) -> Optional[datetime]:
        """
        Parse date strings like '19 November 2025' into a datetime.
        Returns None if parsing fails.
        """
        if not date_text:
            return None
        try:
            # interpret as midnight of that date (no time info on WHO site)
            return datetime.strptime(date_text.strip(), "%d %B %Y")
        except ValueError:
            return None

    def _get_news_metadata(self) -> List[Dict[str, Any]]:
        """
        Scrape the WHO News homepage and return a list of metadata dicts.
        Full text is NOT fetched here.
        """
        self.driver.get(self.NEWS_URL)
        time.sleep(self.wait_time)

        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        items = soup.select("div.list-view--item.vertical-list-item")

        metadata_list: List[Dict[str, Any]] = []

        for item in items:
            link_tag = item.find("a", href=True)
            if not link_tag:
                continue

            # URL normalization
            url = link_tag["href"]
            if url.startswith("/"):
                url = self.BASE_URL + url

            title_tag = item.select_one("p.heading")
            date_tag = item.select_one(".timestamp")
            type_tag = item.select_one(".sf-tags-list-item")

            title_text = title_tag.get_text(strip=True) if title_tag else None
            date_text = date_tag.get_text(strip=True) if date_tag else None
            article_type = type_tag.get_text(strip=True) if type_tag else None

            if not url or not title_text:
                continue

            release_date = self._parse_release_date(date_text or "")
            if release_date is None:
                # Skip if we cannot parse the date
                continue

            article_id = self._generate_article_id(url)

            metadata_list.append(
                {
                    "article_id": article_id,
                    "title": title_text,
                    "url": url,
                    "release_date": release_date,
                    "article_type": article_type,
                }
            )

        return metadata_list

    def get_article_body(self, url: str) -> Optional[str]:
        """
        Visit a news article page and extract the full text from the body.
        Returns None if body is not found or an error occurs.
        """
        try:
            self.driver.get(url)
            time.sleep(self.wait_time)

            soup = BeautifulSoup(self.driver.page_source, "html.parser")
            body_section = soup.select_one("article.sf-detail-body-wrapper")
            if not body_section:
                return None

            parts = [
                el.get_text(" ", strip=True)
                for el in body_section.find_all(["p", "h3", "li"])
            ]
            full_text = "\n".join(part for part in parts if part)

            return full_text or None

        except TimeoutException:
            print(f"[WARN] Timeout while loading: {url}")
            return None
        except Exception as e:
            print(f"[ERROR] Error scraping {url}: {e}")
            return None

    def scrape_all(self, hours: int = 24) -> List[WHOArticle]:
        """
        Scrape the news listing and return WHOArticle objects ONLY for:
          - Articles whose release_date is within the last `max_age_hours`
          - Articles where full_text was successfully parsed.

        :param max_age_hours: Time window in hours (default: 24)
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=hours)

        metadata_list = self._get_news_metadata()

        # Filter by recency
        recent_metadata = [
            meta for meta in metadata_list
            if meta["release_date"] >= cutoff
        ]

        articles: List[WHOArticle] = []

        for meta in recent_metadata:
            #print(f"Scraping recent article: {meta['title']}")
            body = self.get_article_body(meta["url"])

            # If we fail parsing full text, skip this article
            if not body:
                print(f"[INFO] Skipping article due to missing full_text: {meta['url']}")
                continue

            article = WHOArticle(full_text=body, **meta)
            articles.append(article)

        return articles

    def close(self):
        """Cleanly close the browser."""
        try:
            self.driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    scraper = WHOScraper(headless=True, wait_time=1)
    try:
        # Default: last 24 hours
        results = scraper.scrape_all(hours=48)  
        for art in results[0:1]:
            print(f"\nID    : {art.article_id}")
            print(f"Title : {art.title}")
            print(f"Date  : {art.release_date.isoformat()}")
            print(f"Type  : {art.article_type}")
            print(f"URL   : {art.url}")
            print(f"Body  : {art.full_text[:400]}...")
            print("=" * 80)
    finally:
        scraper.close()

