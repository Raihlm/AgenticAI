#!/usr/bin/env python3
"""Main entry point for AgenticAI."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.cli import run_cli


if __name__ == "__main__":
    run_cli()
