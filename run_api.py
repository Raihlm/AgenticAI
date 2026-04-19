#!/usr/bin/env python3
"""Run the AgenticAI API server."""

import uvicorn

if __name__ == "__main__":
    print("Starting AgenticAI API Server...")
    print("API Docs: http://localhost:8000/docs")
    print("API Root: http://localhost:8000")
    print("\nPress Ctrl+C to stop\n")

    uvicorn.run(
        "src.api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
