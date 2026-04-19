"""News fetching tool using NewsAPI and RSS feeds."""

import requests
from datetime import datetime, timedelta
from typing import Optional
from ..config import config


class NewsTool:
    """Fetch real-time news from various sources."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.NEWS_API_KEY

    def get_top_news(
        self,
        country: str = "us",
        category: str = "general",
        page_size: int = 5,
    ) -> list[dict]:
        """
        Get top headlines for a country and/or category.

        Args:
            country: ISO 3166-1 alpha-2 country code (default: 'us')
            category: Category like 'business', 'technology', 'sports', etc.
            page_size: Number of articles to return

        Returns:
            List of news articles
        """
        if not self.api_key:
            return self._get_news_fallback(country, category, page_size)

        try:
            response = requests.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "country": country,
                    "category": category,
                    "pageSize": page_size,
                    "apiKey": self.api_key,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            return self._parse_articles(data.get("articles", []))
        except requests.RequestException as e:
            return [{"error": f"Failed to fetch news: {str(e)}"}]

    def search_news(
        self,
        query: str,
        from_date: Optional[str] = None,
        language: str = "en",
        page_size: int = 5,
    ) -> list[dict]:
        """
        Search news articles by keyword.

        Args:
            query: Search query string
            from_date: Start date (YYYY-MM-DD format)
            language: Language code (default: 'en')
            page_size: Number of articles to return

        Returns:
            List of matching news articles
        """
        if not self.api_key:
            return self._search_news_fallback(query, page_size)

        try:
            params = {
                "q": query,
                "language": language,
                "pageSize": page_size,
                "sortBy": "publishedAt",
                "apiKey": self.api_key,
            }

            if from_date:
                params["from"] = from_date

            response = requests.get(
                "https://newsapi.org/v2/everything",
                params=params,
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            return self._parse_articles(data.get("articles", []))
        except requests.RequestException as e:
            return [{"error": f"Failed to search news: {str(e)}"}]

    def _parse_articles(self, articles: list) -> list[dict]:
        """Parse and format articles."""
        parsed = []
        for article in articles:
            parsed.append(
                {
                    "title": article.get("title", "No title"),
                    "description": article.get("description", ""),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "author": article.get("author", ""),
                    "published_at": article.get("publishedAt", ""),
                    "url": article.get("url", ""),
                    "image": article.get("urlToImage", ""),
                }
            )
        return parsed

    def _get_news_fallback(
        self, country: str, category: str, page_size: int
    ) -> list[dict]:
        """Fallback using DuckDuckGo News search when no API key."""
        # Use DuckDuckGo News as primary fallback (more reliable than RSS)
        return self._search_news_fallback(f"{category} news", page_size)

    def _search_news_fallback(self, query: str, page_size: int) -> list[dict]:
        """Fallback search using web search when news-specific search fails."""
        # Try DuckDuckGo News first
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.news(query, max_results=page_size))
                return [
                    {
                        "title": r.get("title", ""),
                        "description": r.get("body", ""),
                        "source": r.get("source", "DuckDuckGo News"),
                        "published_at": r.get("date", ""),
                        "url": r.get("url", ""),
                        "image": "",
                    }
                    for r in results
                ]
        except Exception:
            # Fall back to regular web search for news-like results
            from ..tools.search import search_tool
            web_results = search_tool.search_web(f"{query} news", num_results=page_size)
            for result in web_results:
                result["source"] = result.get("source", "Web Search")
            return web_results

    def _parse_rss(self, xml_content: str, limit: int) -> list[dict]:
        """Parse RSS feed content."""
        try:
            import xml.etree.ElementTree as ET

            root = ET.fromstring(xml_content)
            channel = root.find("channel")
            items = channel.findall("item")[:limit]

            articles = []
            for item in items:
                articles.append(
                    {
                        "title": self._get_text(item, "title"),
                        "description": self._get_text(item, "description"),
                        "source": "Reuters RSS",
                        "published_at": self._get_text(item, "pubDate"),
                        "url": self._get_text(item, "link"),
                        "image": "",
                    }
                )
            return articles
        except Exception as e:
            return [{"error": f"RSS parsing failed: {str(e)}"}]

    def _get_text(self, element, tag: str) -> str:
        """Safely get text from XML element."""
        child = element.find(tag)
        return child.text if child is not None and child.text else ""


# Create singleton instance
news_tool = NewsTool()
