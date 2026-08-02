import pytest
from src.services.open_meteo import OpenMeteoService
from src.schemas.weather import CurrentWeatherResponse, OpenMeteoHourlyDTO

pytestmark = pytest.mark.asyncio

class TestOpenMeteoService:

    @pytest.fixture(autouse=True)
    def setup(self):
        self.client = OpenMeteoService(15)
        self.latitude = 55.7558
        self.longitude = 37.6173

    async def test_get_weather_success(self):
        result = await self.client.get_current_weather(latitude = self.latitude,longitude = self.longitude)

        assert isinstance(result, CurrentWeatherResponse)
        assert isinstance(result.temperature, float)
        assert isinstance(result.wind_speed, float)
        assert isinstance(result.pressure, float)


