from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.database import SessionLocal
from src.models.city import City
from src.models.weather_forecast import WeatherForecast
from src.services.open_meteo import OpenMeteoService

scheduler = AsyncIOScheduler()


async def update_all_cities_weather():
    db = SessionLocal()
    try:
        cities = db.query(City).all()
        service = OpenMeteoService(15)

        for city in cities:
            data = await service.get_daily_forecast(city.latitude, city.longitude)
            hourly = data.get("hourly", {})
            times = hourly.get("time", [])

            db.query(WeatherForecast).filter(WeatherForecast.city_id == city.id).delete()
            for i, time_str in enumerate(times):
                forecast = WeatherForecast(
                    city_id=city.id,
                    timestamp=datetime.fromisoformat(time_str),
                    temperature=hourly.get("temperature_2m", [])[i],
                    wind_speed=hourly.get("wind_speed_10m", [])[i],
                    pressure=hourly.get("surface_pressure", [])[i],
                    humidity=hourly.get("relative_humidity_2m", [])[i],
                    precipitation=hourly.get("precipitation", [])[i],
                )
                db.add(forecast)
        db.commit()

    finally:
        db.close()

def start_scheduler():
    scheduler.add_job(update_all_cities_weather, 'interval', minutes=15)
    scheduler.start()


