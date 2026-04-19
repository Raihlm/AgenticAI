"""Web search and information retrieval tools."""

import requests
from typing import Optional
from bs4 import BeautifulSoup
from ..config import config


class SearchTool:
    """Web search and content fetching capabilities."""

    def __init__(self, tavily_api_key: Optional[str] = None):
        self.tavily_api_key = tavily_api_key or config.TAVILY_API_KEY

    def search_web(
        self, query: str, num_results: int = 5, search_depth: str = "basic"
    ) -> list[dict]:
        """
        Search the web for information.

        Args:
            query: Search query
            num_results: Number of results to return
            search_depth: 'basic' or 'advanced'

        Returns:
            List of search results
        """
        if self.tavily_api_key:
            return self._tavily_search(query, num_results, search_depth)
        else:
            return self._duckduckgo_search(query, num_results)

    def _tavily_search(
        self, query: str, num_results: int, search_depth: str
    ) -> list[dict]:
        """Search using Tavily API (optimized for AI agents)."""
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "max_results": num_results,
                    "search_depth": search_depth,
                    "include_answer": True,
                    "include_raw_content": False,
                },
                timeout=15,
            )
            response.raise_for_status()
            data = response.json()

            results = []
            for result in data.get("results", []):
                results.append(
                    {
                        "title": result.get("title", ""),
                        "content": result.get("content", ""),
                        "url": result.get("url", ""),
                        "score": result.get("score", 0),
                    }
                )

            # Include the direct answer if available
            if data.get("answer"):
                results.insert(
                    0,
                    {
                        "title": "Direct Answer",
                        "content": data["answer"],
                        "url": "Tavily AI-generated answer",
                        "score": 1.0,
                    },
                )

            return results
        except requests.RequestException as e:
            return [{"error": f"Tavily search failed: {str(e)}"}]

    def _duckduckgo_search(self, query: str, num_results: int) -> list[dict]:
        """Search using DuckDuckGo (no API key required)."""
        try:
            try:
                from ddgs import DDGS
            except ImportError:
                from duckduckgo_search import DDGS

            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
                return [
                    {
                        "title": r.get("title", ""),
                        "content": r.get("body", ""),
                        "url": r.get("href", ""),
                        "source": "DuckDuckGo",
                    }
                    for r in results
                ]
        except Exception as e:
            # Return helpful error with alternative suggestion
            return [{
                "error": f"Web search unavailable: {str(e)}",
                "hint": "Install a search tool or use Tavily API key for better results"
            }]

    def fetch_url_content(self, url: str, max_length: int = 5000) -> dict:
        """
        Fetch and extract main content from a URL.

        Args:
            url: URL to fetch
            max_length: Maximum content length to return

        Returns:
            Dictionary with title and content
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "lxml")

            # Extract title
            title = ""
            if soup.title:
                title = soup.title.string

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "header", "footer"]):
                script.decompose()

            # Get main content
            main = soup.find("main") or soup.find("article") or soup.body
            content = main.get_text(separator="\n", strip=True) if main else ""

            # Clean up whitespace
            lines = [
                line.strip()
                for line in content.splitlines()
                if line.strip() and len(line.strip()) > 10
            ]
            content = "\n".join(lines)[:max_length]

            return {"title": title, "content": content, "url": url}
        except Exception as e:
            return {"error": f"Failed to fetch URL: {str(e)}"}

    def get_current_time_info(self) -> dict:
        """Get current date and time information."""
        from datetime import datetime

        now = datetime.now()
        return {
            "current_datetime": now.isoformat(),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "day_of_week": now.strftime("%A"),
            "timezone": "local",
        }

    def calculate(self, expression: str) -> dict:
        """
        Safely evaluate a mathematical expression.

        Args:
            expression: Mathematical expression to evaluate

        Returns:
            Result of the calculation
        """
        try:
            # Only allow safe characters
            allowed_chars = set("0123456789+-*/.() ")
            if not all(c in allowed_chars for c in expression):
                return {"error": "Invalid characters in expression"}

            result = eval(expression, {"__builtins__": {}}, {})
            return {"expression": expression, "result": result}
        except Exception as e:
            return {"error": f"Calculation failed: {str(e)}"}


# Create singleton instance
search_tool = SearchTool()
