"""Configuration settings for the AgenticAI system."""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Config:
    """Main configuration class."""

    # Ollama settings
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama2:latest")
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text:latest")

    # API Keys (optional - some tools work without keys)
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")  # OpenWeatherMap
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")  # NewsAPI.org
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "")  # Tavily Search

    # Agent settings
    MAX_ITERATIONS: int = int(os.getenv("MAX_ITERATIONS", "10"))
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))

    # Memory settings
    MEMORY_DIR: str = os.getenv("MEMORY_DIR", "memory")
    ENABLE_LONG_TERM_MEMORY: bool = os.getenv("ENABLE_LONG_TERM_MEMORY", "true").lower() == "true"


config = Config()
