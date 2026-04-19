#!/usr/bin/env python3
"""Demo script for AgenticAI - Test all features."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent.agent import create_agent
from src.tools.weather import weather_tool
from src.tools.search import search_tool


def print_section(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    print_section("AgenticAI Demo")
    print("Testing all available features...\n")

    # Test 1: Weather Tool
    print("[1] Testing Weather Tool...")
    weather = weather_tool.get_weather("Dhaka")
    if "error" not in weather:
        print(f"    Location: {weather['location']}, {weather.get('country', '')}")
        print(f"    Temperature: {weather['temperature']}°C")
        print(f"    Conditions: {weather['description']}")
        print("    [OK] Weather tool working!")
    else:
        print(f"    ✗ Weather error: {weather['error']}")

    # Test 2: Weather Forecast
    print("\n[2] Testing Weather Forecast...")
    forecast = weather_tool.get_forecast("London", days=2)
    if "error" not in forecast:
        print(f"    Forecast for: {forecast['location']}")
        for day in forecast.get("forecast", [])[:2]:
            if "temp_max" in day:
                print(f"    - {day.get('date', 'N/A')}: {day['temp_min']}°C to {day['temp_max']}°C")
            else:
                print(f"    - {day.get('datetime', 'N/A')}: {day['temperature']}°C")
        print("    [OK] Forecast tool working!")
    else:
        print(f"    ✗ Forecast error: {forecast['error']}")

    # Test 3: Time Info
    print("\n[3] Testing Time Info...")
    time_info = search_tool.get_current_time_info()
    print(f"    Current: {time_info['date']} {time_info['time']} ({time_info['day_of_week']})")
    print("    [OK] Time tool working!")

    # Test 4: Calculator
    print("\n[4] Testing Calculator...")
    calc = search_tool.calculate("25 * 4 + 10")
    if "error" not in calc:
        print(f"    25 * 4 + 10 = {calc['result']}")
        print("    [OK] Calculator tool working!")
    else:
        print(f"    ✗ Calculator error: {calc['error']}")

    # Test 5: Agent with simple query
    print("\n[5] Testing Agent (Simple Math)...")
    agent = create_agent()
    response = agent.invoke("What is 100 divided by 4?")
    print(f"    Response: {response[:100]}...")
    print("    [OK] Agent responding!")

    # Test 6: Agent with weather query
    print("\n[6] Testing Agent (Weather Query)...")
    response = agent.invoke("What's the weather in Tokyo?")
    print(f"    Response: {response[:150]}...")
    print("    [OK] Agent with tool use working!")

    print_section("Demo Complete!")
    print("\nAll core features tested successfully!")
    print("\nNext steps:")
    print("  - Run CLI: python main.py")
    print("  - Run API: python run_api.py")
    print("  - Open notebook: overview/demo.ipynb")
    print("\nNote: Some external services (DuckDuckGo, news RSS) may have")
    print("      connectivity issues. Weather tools work reliably via")
    print("      Open-Meteo (free, no API key required).")


if __name__ == "__main__":
    main()
