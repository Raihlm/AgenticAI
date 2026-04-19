#!/usr/bin/env python3
"""Command-line interface for AgenticAI."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agent.agent import create_agent
from src.agent.memory import get_memory, reset_memory
from src.config import config


def print_banner():
    """Print welcome banner."""
    print("=" * 60)
    print("  AgenticAI - Local AI Agent with Real-time Data")
    print("  Powered by Ollama ({})".format(config.DEFAULT_MODEL))
    print("=" * 60)
    print()
    print("Commands:")
    print("  /help     - Show this help message")
    print("  /clear    - Clear conversation history")
    print("  /memory   - Show stored memories")
    print("  /model    - Show/change current model")
    print("  /tools    - List available tools")
    print("  /quit     - Exit the program")
    print()
    print("Available Tools:")
    print("  - Weather: 'weather in Dhaka', 'forecast for London'")
    print("  - News: 'top tech news', 'news about AI'")
    print("  - Search: 'who won the world cup', 'latest AI developments'")
    print("  - Time: 'what time is it', 'current date'")
    print("  - Math: 'calculate 25 * 4 + 10'")
    print()
    print("-" * 60)


def print_tools():
    """List all available tools."""
    from src.agent.tools_registry import get_all_tools

    tools = get_all_tools()
    print("\nAvailable Tools:")
    print("-" * 40)
    for tool in tools:
        print(f"\n  {tool.name}")
        print(f"    {tool.description}")


def run_cli():
    """Run the interactive CLI."""
    print_banner()

    # Initialize agent
    print("Initializing agent...")
    try:
        agent = create_agent()
        print(f"Agent ready using model: {config.DEFAULT_MODEL}")
    except Exception as e:
        print(f"Error initializing agent: {e}")
        print("Make sure Ollama is running: ollama serve")
        return

    memory = get_memory()

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            # Handle commands
            if user_input.startswith("/"):
                command = user_input.lower().split()[0]

                if command in ["/quit", "/exit"]:
                    print("Goodbye!")
                    break

                elif command == "/help":
                    print_banner()

                elif command == "/clear":
                    reset_memory()
                    print("Conversation history cleared.")

                elif command == "/memory":
                    mem = get_memory()
                    print("\nLong-term memories:")
                    for m in mem.long_term_memories:
                        print(f"  - {m['key']}: {m['value']}")

                elif command == "/model":
                    parts = user_input.split()
                    if len(parts) > 1:
                        # Change model
                        new_model = parts[1]
                        try:
                            agent = create_agent(new_model)
                            print(f"Model changed to: {new_model}")
                        except Exception as e:
                            print(f"Error: {e}")
                    else:
                        print(f"Current model: {config.DEFAULT_MODEL}")
                        print("Available models (check with 'ollama list'):")
                        print("  - qwen3.5:latest (recommended)")
                        print("  - llama3.1:latest")
                        print("  - llama3.2:latest")
                        print("  - llama2:latest")
                        print("  - llava:latest (multimodal)")

                elif command == "/tools":
                    print_tools()

                else:
                    print(f"Unknown command: {command}. Type /help for available commands.")

                continue

            # Process query
            print("\nAgenticAI: ", end="", flush=True)

            try:
                # Use streaming for better UX
                full_response = ""
                for event in agent.stream(user_input):
                    if "agent" in event:
                        msg = event["agent"]["messages"][-1]
                        if hasattr(msg, "content") and msg.content:
                            # Check for tool calls
                            if hasattr(msg, "tool_calls") and msg.tool_calls:
                                tool_names = [tc["name"] for tc in msg.tool_calls]
                                print(f"\n[Using tools: {', '.join(tool_names)}]... ", end="")
                            else:
                                print(msg.content)
                                full_response = msg.content

                # Save to memory
                memory.add_message("user", user_input)
                if full_response:
                    memory.add_message("assistant", full_response)

            except Exception as e:
                print(f"\nError: {e}")
                print("Tip: Make sure Ollama is running with 'ollama serve'")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Type /quit to exit or press Ctrl+C again.")
        except EOFError:
            break

    print("\nThanks for using AgenticAI!")


if __name__ == "__main__":
    run_cli()
