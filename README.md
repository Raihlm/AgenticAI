# AgenticAI - Local AI Agent with Real-time Data

An AI agent powered by **Ollama** (local LLMs) that can fetch real-time data including weather, news, and web search results using **LangGraph** for workflow orchestration.

## Features

### Core Capabilities
- **Weather Data**: Current conditions and forecasts for any location
- **News Fetching**: Top headlines by category and keyword search
- **Web Search**: Search the internet for information
- **Time & Calculations**: Current date/time and mathematical operations

### Advanced Features
- **LangGraph Workflow**: State-based agent with tool routing
- **Conversation Memory**: Session history and long-term memory
- **Multi-step Planning**: Automatic task breakdown for complex queries
- **Dual Interface**: CLI and REST API

### Tools Available
| Tool | Description |
|------|-------------|
| `get_weather` | Current weather for any location |
| `get_weather_forecast` | Multi-day forecast |
| `get_top_news` | Headlines by category/country |
| `search_news` | Search news by keyword |
| `web_search` | General web search |
| `get_current_time` | Date and time info |
| `calculate` | Math calculations |

## Installation

### Prerequisites
1. **Ollama** installed and running
   ```bash
   # Download from https://ollama.ai
   # Then pull a model:
   ollama pull qwen3.5:latest
   ```

2. **Python 3.10+**

### Setup
```bash
cd Documents/rayhan/AgenticAi

# Install dependencies
pip install -r requirements.txt

# Copy environment file (optional - has sensible defaults)
cp .env.example .env
```

### Optional API Keys
For enhanced functionality, add these to `.env`:
- **OpenWeatherMap**: Free weather API (fallback works without key)
- **NewsAPI.org**: News articles (fallback works without key)
- **Tavily**: AI-optimized search (DuckDuckGo fallback available)

## Usage

### CLI Mode (Recommended)
```bash
python main.py
```

Example queries:
```
You: What's the weather in Dhaka?
You: Get me the latest tech news
You: Search for information about quantum computing
You: What's 25% of 150?
You: Compare weather in London and Paris
```

### API Mode
```bash
python run_api.py
```

Then access:
- API Docs: http://localhost:8000/docs
- API Root: http://localhost:8000

Example API request:
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the weather in Tokyo?"}'
```

### CLI Commands
| Command | Description |
|---------|-------------|
| `/help` | Show help message |
| `/clear` | Clear conversation |
| `/memory` | Show stored memories |
| `/model` | Show/change model |
| `/tools` | List available tools |
| `/quit` | Exit program |

## Project Structure

```
AgenticAi/
├── src/
│   ├── agent/
│   │   ├── agent.py       # LangGraph agent
│   │   ├── state.py       # State management
│   │   ├── memory.py      # Conversation memory
│   │   ├── planner.py     # Multi-step planning
│   │   └── tools_registry.py
│   ├── tools/
│   │   ├── weather.py     # Weather tool
│   │   ├── news.py        # News tool
│   │   └── search.py      # Search tool
│   ├── config.py          # Configuration
│   ├── cli.py             # CLI interface
│   └── api.py             # REST API
├── main.py                # CLI entry point
├── run_api.py             # API entry point
├── requirements.txt
└── .env.example
```

## Architecture

```
┌─────────────┐
│   User      │
│  (CLI/API)  │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│     LangGraph Agent             │
│  ┌─────────────────────────┐    │
│  │  State Management       │    │
│  │  - Messages             │    │
│  │  - Tool Results         │    │
│  │  - Memory Context       │    │
│  └─────────────────────────┘    │
└──────────────┬──────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ▼          ▼          ▼
┌───────┐  ┌───────┐  ┌────────┐
│Weather│  │ News  │  │ Search │
│ Tool  │  │ Tool  │  │  Tool  │
└───────┘  └───────┘  └────────┘
```

## Models

Tested with:
- `qwen3.5:latest` (recommended - excellent tool use)
- `llama3.1:latest`
- `llama3.2:latest`
- `llama2:latest`

Change model with: `/model llama3.1:latest`

## Troubleshooting

**Agent not responding:**
```bash
# Make sure Ollama is running
ollama serve
```

**Model not found:**
```bash
# Pull the model
ollama pull qwen3.5:latest
```

**Import errors:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## License

MIT License - Feel free to use and modify!



# Agent's prompt

 Project Summary

  Core Features

  ┌─────────────────┬───────────────────────────────────────────────────────────────┐
  │     Feature     │                          Description                          │
  ├─────────────────┼───────────────────────────────────────────────────────────────┤
  │ Weather         │ Real-time weather + forecasts (Open-Meteo, no API key needed) │
  ├─────────────────┼───────────────────────────────────────────────────────────────┤
  │ News            │ Top headlines & search (NewsAPI or DuckDuckGo fallback)       │
  ├─────────────────┼───────────────────────────────────────────────────────────────┤
  │ Web Search      │ DuckDuckGo or Tavily API integration                          │
  ├─────────────────┼───────────────────────────────────────────────────────────────┤
  │ LangGraph Agent │ State-based workflow with tool routing                        │
  ├─────────────────┼───────────────────────────────────────────────────────────────┤
  │ Memory          │ Conversation history + long-term memory                       │
  ├─────────────────┼───────────────────────────────────────────────────────────────┤
  │ Planner         │ Multi-step task breakdown for complex queries                 │
  └─────────────────┴───────────────────────────────────────────────────────────────┘

  Project Structure

  AgenticAi/
  ├── src/
  │   ├── agent/       # LangGraph agent, memory, planner
  │   ├── tools/       # Weather, news, search tools
  │   ├── api.py       # REST API (FastAPI)
  │   └── cli.py       # Interactive CLI
  ├── main.py          # CLI entry point
  ├── run_api.py       # API server
  ├── demo.py          # Feature demo script
  └── requirements.txt

  Quick Start

  cd Documents/rayhan/AgenticAi

  # CLI mode
  python main.py

  # API mode
  python run_api.py

  # Run demo
  python demo.py

  Tested & Working

  - Weather tool (Dhaka: 32.5°C, partly cloudy)
  - Agent responding via Ollama (qwen3.5:latest)
  - Tool routing through LangGraph

  Note

  Network-dependent features (DuckDuckGo, news RSS) may have connectivity issues in some environments. The weather tool works reliably via Open-Meteo without any
  API key.
