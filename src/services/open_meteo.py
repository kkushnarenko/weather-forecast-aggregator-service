from typing import Dict, Any
import httpx
from src.config import settings
from src.schemas.weather import CurrentWeatherResponse, OpenMeteoDTOResponse


class OpenMeteoService:
    def __init__(self, timeout : float):
        self.api_key = settings.OPEN_METEO_API_KEY
        self.timeout = timeout

    async def get_current_weather(self, latitude: float, longitude: float) -> CurrentWeatherResponse:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "current": ["temperature_2m", "wind_speed_10m", "surface_pressure"],
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.api_key, params=params)
            response.raise_for_status()

            data = response.json()
            current = data.get("current", {})

            response = CurrentWeatherResponse(
                temperature=current.get("temperature_2m"),
                wind_speed=current.get("wind_speed_10m"),
                pressure=current.get("surface_pressure")
            )
            return response

    async def get_daily_forecast(self, latitude: float, longitude: float) -> Dict[str, Any]:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "wind_speed_10m",
                "surface_pressure",
                "precipitation",
            ],
            "forecast_days": 1,
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(self.api_key, params=params)
            response.raise_for_status()
            return response.json()