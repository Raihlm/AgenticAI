"""Weather data fetching tool using OpenWeatherMap API."""

import requests
from typing import Optional
from datetime import datetime
from ..config import config


class WeatherTool:
    """Fetch real-time weather data for any location."""

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or config.WEATHER_API_KEY

    def get_weather(self, location: str) -> dict:
        """
        Get current weather data for a location.

        Args:
            location: City name, coordinates, or zip code

        Returns:
            Dictionary with weather information
        """
        if not self.api_key:
            return self._get_weather_fallback(location)

        try:
            response = requests.get(
                f"{self.BASE_URL}/weather",
                params={"q": location, "appid": self.api_key, "units": "metric"},
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            return {
                "location": data.get("name", location),
                "country": data.get("sys", {}).get("country", ""),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "sunrise": datetime.fromtimestamp(
                    data["sys"]["sunrise"]
                ).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(
                    data["sys"]["sunset"]
                ).strftime("%H:%M"),
            }
        except requests.RequestException as e:
            return {"error": f"Failed to fetch weather: {str(e)}"}

    def _get_weather_fallback(self, location: str) -> dict:
        """Fallback when no API key is available - uses public API."""
        try:
            # Using Open-Meteo free API (no key required)
            # First geocode the location
            geo_response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 1},
                timeout=10,
            )
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                return {"error": f"Location '{location}' not found"}

            result = geo_data["results"][0]
            lat, lon = result["latitude"], result["longitude"]

            # Get weather data
            weather_response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "current_weather": True,
                },
                timeout=10,
            )
            weather_response.raise_for_status()
            weather_data = weather_response.json()

            current = weather_data["current_weather"]
            return {
                "location": result.get("name", location),
                "country": result.get("country", ""),
                "temperature": current["temperature"],
                "wind_speed": current["windspeed"],
                "description": self._wmo_code_to_description(
                    current["weathercode"]
                ),
                "source": "Open-Meteo (free, no API key required)",
            }
        except requests.RequestException as e:
            return {"error": f"Failed to fetch weather: {str(e)}"}

    def _wmo_code_to_description(self, code: int) -> str:
        """Convert WMO weather codes to descriptions."""
        codes = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            45: "Foggy",
            48: "Depositing rime fog",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            71: "Slight snow fall",
            73: "Moderate snow fall",
            75: "Heavy snow fall",
            95: "Thunderstorm",
            96: "Thunderstorm with slight hail",
            99: "Thunderstorm with heavy hail",
        }
        return codes.get(code, "Unknown")

    def get_forecast(self, location: str, days: int = 3) -> dict:
        """Get weather forecast for multiple days."""
        if not self.api_key:
            return self._get_forecast_fallback(location, days)

        try:
            response = requests.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "q": location,
                    "appid": self.api_key,
                    "units": "metric",
                    "cnt": days * 8,
                },
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()

            forecasts = []
            for item in data["list"][: days * 8]:
                forecasts.append(
                    {
                        "datetime": item["dt_txt"],
                        "temperature": item["main"]["temp"],
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"],
                    }
                )

            return {"location": data["city"]["name"], "forecast": forecasts}
        except requests.RequestException as e:
            return {"error": f"Failed to fetch forecast: {str(e)}"}

    def _get_forecast_fallback(self, location: str, days: int = 3) -> dict:
        """Fallback forecast using Open-Meteo."""
        try:
            geo_response = requests.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": location, "count": 1},
                timeout=10,
            )
            geo_response.raise_for_status()
            geo_data = geo_response.json()

            if not geo_data.get("results"):
                return {"error": f"Location '{location}' not found"}

            result = geo_data["results"][0]

            weather_response = requests.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": result["latitude"],
                    "longitude": result["longitude"],
                    "daily": [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_probability_max",
                        "weathercode",
                    ],
                    "forecast_days": days,
                },
                timeout=10,
            )
            weather_response.raise_for_status()
            data = weather_response.json()

            forecasts = []
            for i in range(days):
                forecasts.append(
                    {
                        "date": data["daily"]["time"][i],
                        "temp_max": data["daily"]["temperature_2m_max"][i],
                        "temp_min": data["daily"]["temperature_2m_min"][i],
                        "description": self._wmo_code_to_description(
                            data["daily"]["weathercode"][i]
                        ),
                        "precipitation_chance": data["daily"][
                            "precipitation_probability_max"
                        ][i],
                    }
                )

            return {"location": result["name"], "forecast": forecasts}
        except requests.RequestException as e:
            return {"error": f"Failed to fetch forecast: {str(e)}"}


# Create singleton instance
weather_tool = WeatherTool()
