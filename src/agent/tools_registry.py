"""LangChain tool wrappers for our custom tools."""

from langchain_core.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field

from ..tools.weather import weather_tool
from ..tools.news import news_tool
from ..tools.search import search_tool


# === Weather Tools ===


class WeatherInput(BaseModel):
    location: str = Field(description="City name or location for weather")


class WeatherTool(BaseTool):
    name: str = "get_weather"
    description: str = "Get current weather for a location. Use for questions about temperature, conditions, forecast."
    args_schema: Type[BaseModel] = WeatherInput

    def _run(self, location: str) -> str:
        result = weather_tool.get_weather(location)
        if "error" in result:
            return result["error"]

        return (
            f"Weather in {result['location']}, {result.get('country', '')}:\n"
            f"Temperature: {result['temperature']}°C (feels like {result.get('feels_like', result['temperature'])}°C)\n"
            f"Conditions: {result['description']}\n"
            f"Humidity: {result.get('humidity', 'N/A')}%\n"
            f"Wind: {result.get('wind_speed', 'N/A')} m/s\n"
            f"Source: {result.get('source', 'OpenWeatherMap')}"
        )


class WeatherForecastInput(BaseModel):
    location: str = Field(description="City name or location")
    days: int = Field(default=3, description="Number of days for forecast (1-5)")


class WeatherForecastTool(BaseTool):
    name: str = "get_weather_forecast"
    description: str = "Get weather forecast for multiple days."
    args_schema: Type[BaseModel] = WeatherForecastInput

    def _run(self, location: str, days: int = 3) -> str:
        days = min(max(days, 1), 5)  # Clamp between 1-5
        result = weather_tool.get_forecast(location, days)
        if "error" in result:
            return result["error"]

        forecast_lines = []
        for day in result["forecast"]:
            if "date" in day:
                line = f"{day['date']}: {day['temp_min']}°C - {day['temp_max']}°C, {day['description']}"
            else:
                line = f"{day.get('datetime', 'N/A')}: {day['temperature']}°C, {day['description']}"
            forecast_lines.append(line)

        return f"Forecast for {result['location']}:\n" + "\n".join(forecast_lines)


# === News Tools ===


class TopNewsInput(BaseModel):
    category: str = Field(
        default="general",
        description="News category: business, technology, sports, entertainment, health, science",
    )
    country: str = Field(default="us", description="Country code (us, gb, in, etc.)")
    limit: int = Field(default=5, description="Number of articles (1-10)")


class TopNewsTool(BaseTool):
    name: str = "get_top_news"
    description: str = "Get top news headlines by category and country."
    args_schema: Type[BaseModel] = TopNewsInput

    def _run(self, category: str = "general", country: str = "us", limit: int = 5) -> str:
        limit = min(max(limit, 1), 10)
        articles = news_tool.get_top_news(country, category, limit)

        if "error" in articles[0]:
            return articles[0]["error"]

        return self._format_articles(articles)

    def _format_articles(self, articles: list) -> str:
        formatted = []
        for i, article in enumerate(articles, 1):
            formatted.append(
                f"{i}. {article['title']}\n"
                f"   Source: {article['source']}\n"
                f"   {article.get('description', '')[:200]}\n"
                f"   URL: {article.get('url', 'N/A')}"
            )
        return "\n\n".join(formatted)


class SearchNewsInput(BaseModel):
    query: str = Field(description="Search query or topic")
    limit: int = Field(default=5, description="Number of articles (1-10)")


class SearchNewsTool(BaseTool):
    name: str = "search_news"
    description: str = "Search news articles by keyword or topic."
    args_schema: Type[BaseModel] = SearchNewsInput

    def _run(self, query: str, limit: int = 5) -> str:
        limit = min(max(limit, 1), 10)
        articles = news_tool.search_news(query, page_size=limit)

        if "error" in articles[0]:
            return articles[0]["error"]

        return TopNewsTool()._format_articles(articles)


# === Search Tools ===


class WebSearchInput(BaseModel):
    query: str = Field(description="Search query")
    num_results: int = Field(default=5, description="Number of results (1-10)")


class WebSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for information. Use for general queries, facts, current events."
    args_schema: Type[BaseModel] = WebSearchInput

    def _run(self, query: str, num_results: int = 5) -> str:
        num_results = min(max(num_results, 1), 10)
        results = search_tool.search_web(query, num_results)

        if "error" in results[0]:
            return results[0]["error"]

        formatted = []
        for i, result in enumerate(results, 1):
            if result.get("title") == "Direct Answer":
                formatted.append(f"Answer: {result['content']}\n")
            else:
                formatted.append(
                    f"{i}. {result['title']}\n"
                    f"   {result.get('content', '')[:200]}\n"
                    f"   URL: {result.get('url', 'N/A')}"
                )
        return "\n\n".join(formatted)


class TimeInfoTool(BaseTool):
    name: str = "get_current_time"
    description: str = "Get current date and time information."

    def _run(self) -> str:
        result = search_tool.get_current_time_info()
        return (
            f"Current Date: {result['date']}\n"
            f"Current Time: {result['time']}\n"
            f"Day: {result['day_of_week']}"
        )


class CalculatorInput(BaseModel):
    expression: str = Field(description="Mathematical expression to calculate")


class CalculatorTool(BaseTool):
    name: str = "calculate"
    description: str = "Calculate a mathematical expression. Use for math problems."
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(self, expression: str) -> str:
        result = search_tool.calculate(expression)
        if "error" in result:
            return result["error"]
        return f"{result['expression']} = {result['result']}"


# === Tool Registry ===


def get_all_tools() -> list:
    """Return all available tools for the agent."""
    return [
        WeatherTool(),
        WeatherForecastTool(),
        TopNewsTool(),
        SearchNewsTool(),
        WebSearchTool(),
        TimeInfoTool(),
        CalculatorTool(),
    ]
