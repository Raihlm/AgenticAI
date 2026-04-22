#!/usr/bin/env python3
"""FastAPI server for AgenticAI."""

import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List

from src.agent.agent import create_agent, AgenticAgent
from src.agent.memory import get_memory
from src.config import config


# Global agent instance
agent: Optional[AgenticAgent] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize agent on startup."""
    global agent
    print("Starting AgenticAI server...")
    try:
        agent = create_agent()
        print(f"Agent loaded with model: {config.DEFAULT_MODEL}")
    except Exception as e:
        print(f"Failed to load agent: {e}")
        agent = None
    yield
    print("Shutting down AgenticAI server...")


app = FastAPI(
    title="AgenticAI API",
    description="Local AI Agent with Real-time Data Fetching",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""

    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""

    response: str
    tools_used: Optional[List[str]] = None
    session_id: str


class ToolInfo(BaseModel):
    """Tool information schema."""

    name: str
    description: str


# API routes under /api prefix
@app.get("/api")
async def root():
    """API health check."""
    return {
        "status": "healthy",
        "model": config.DEFAULT_MODEL,
        "message": "AgenticAI API is running",
    }


@app.get("/api/tools", response_model=List[ToolInfo])
async def list_tools():
    """List all available tools."""
    from src.agent.tools_registry import get_all_tools

    tools = get_all_tools()
    return [{"name": t.name, "description": t.description} for t in tools]


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the AI agent.

    The agent will automatically use tools when needed to fetch
    real-time data like weather, news, or web search results.
    """
    if agent is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    try:
        # Get or create memory for session
        memory = get_memory()

        # Process the message
        response = agent.invoke(request.message)

        # Extract tools used from the response
        tools_used = []
        if "[Using tools:" in response:
            import re

            match = re.search(r"\[Using tools: ([^\]]+)\]", response)
            if match:
                tools_used = [t.strip() for t in match.group(1).split(",")]
                # Clean the response
                response = response.replace(match.group(0), "").strip()

        # Save to memory
        memory.add_message("user", request.message, {"session_id": request.session_id})
        memory.add_message("assistant", response, {"tools_used": tools_used})

        return ChatResponse(
            response=response,
            tools_used=tools_used if tools_used else None,
            session_id=request.session_id or memory.session_id,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/memory")
async def get_memory_info():
    """Get current memory information."""
    memory = get_memory()
    return {
        "session_id": memory.session_id,
        "conversation_length": len(memory.conversation_history),
        "long_term_memories": len(memory.long_term_memories),
    }


@app.post("/api/memory/clear")
async def clear_memory():
    """Clear conversation memory."""
    from src.agent.memory import reset_memory

    reset_memory()
    return {"status": "Memory cleared"}


@app.get("/api/models")
async def list_models():
    """List available Ollama models."""
    import requests

    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {"models": [m["name"] for m in data.get("models", [])]}
    except Exception:
        pass

    # Default known models
    return {
        "models": [
            "qwen3.5:latest",
            "llama3.1:latest",
            "llama3.2:latest",
            "llama2:latest",
            "llava:latest",
        ]
    }


# SPA Fallback - serve React app for all non-API routes
frontend_dir = Path(__file__).parent.parent / "frontend" / "dist"

if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=frontend_dir / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve React app for all non-API routes."""
        # Don't serve index.html for API routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi"):
            raise HTTPException(status_code=404)
        return FileResponse(frontend_dir / "index.html")


if __name__ == "__main__":
    import uvicorn

    print("Starting AgenticAI API server...")
    print(f"Web UI available at: http://localhost:8000")
    print(f"API Docs available at: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
