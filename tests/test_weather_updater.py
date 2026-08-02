import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import City, WeatherForecast
from src.tasks.weather_updater import update_all_cities_weather

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.mark.asyncio
async def test_update_all_cities_weather(db_session):
    city = City(name="Moscow", latitude=55.75, longitude=37.61, user_id=1)
    db_session.add(city)
    db_session.commit()
    db_session.refresh(city)

    mock_forecast_responce = {
        "hourly": {
            "time" : ["2026-07-31T12:00", "2026-07-31T13:00"],
            "temperature_2m" : [22.5, 23.0],
            "wind_speed_10m" : [3.5, 4.0],
            "surface_pressure" : [5.0, 6.0],
            "relative_humidity_2m" : [50.0, 48.0],
            "precipitation" : [0.0, 0.1],
        }
    }

    with patch("src.tasks.weather_updater.SessionLocal", new=TestingSessionLocal), \
        patch("src.tasks.weather_updater.OpenMeteoService") as MockService:

        mock_instance = MockService.return_value
        mock_instance.get_daily_forecast = AsyncMock(return_value=mock_forecast_responce)

        await update_all_cities_weather()

    forecast = db_session.query(WeatherForecast).filter_by(city_id=city.id).all()

    assert len(forecast) == 2
    assert forecast[0].temperature == 22.5
    assert forecast[0].wind_speed == 3.5
    assert forecast[0].timestamp == datetime.fromisoformat("2026-07-31T12:00")
    assert forecast[1].temperature == 23.0


@pytest.mark.asyncio
async def test_update_weather_overwrites_old_dates(db_session):
    city = City(name="Moscow", latitude=55.75, longitude=37.61, user_id=1)
    db_session.add(city)
    db_session.commit()

    old_forecast = WeatherForecast(
        city_id=city.id,
        timestamp=datetime(2026, 1,1,0,0),
        temperature = 10.0
    )

    db_session.add(old_forecast)
    db_session.commit()

    mock_forecast_responce = {
        "hourly": {
            "time": ["2026-07-31T12:00"],
            "temperature_2m": [25.0],
            "wind_speed_10m": [2.0],
            "surface_pressure": [1000.0],
            "relative_humidity_2m": [40.0],
            "precipitation": [0.0],
        }
    }
    with patch("src.tasks.weather_updater.SessionLocal", new=TestingSessionLocal), \
            patch("src.tasks.weather_updater.OpenMeteoService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.get_daily_forecast = AsyncMock(return_value=mock_forecast_responce)

        await update_all_cities_weather()

    forecasts = db_session.query(WeatherForecast).filter_by(city_id=city.id).all()
    assert len(forecasts) == 1
    assert forecasts[0].temperature == 25.0



@pytest.mark.asyncio
async def test_update_weather_empty_cities():
    with patch("src.tasks.weather_updater.SessionLocal", TestingSessionLocal), \
            patch("src.tasks.weather_updater.OpenMeteoService") as MockService:
        mock_instance = MockService.return_value
        mock_instance.get_daily_forecast = AsyncMock()

        await update_all_cities_weather()

        mock_instance.get_daily_forecast.assert_not_called()