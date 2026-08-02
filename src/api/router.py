from datetime import datetime
from typing import List
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from src.schemas.weather import CurrentWeatherResponse, DetailWeatherResponse
from src.schemas.city import CityResponse
from src.schemas.user import UserResponse, UserCreateRequest
from src.services.open_meteo import OpenMeteoService
from src.database import get_db
from src.models.city import City
from src.models.user import User
from src.models.weather_forecast import WeatherForecast
from src.tasks.weather_updater import update_all_cities_weather

router = APIRouter(prefix="/weather")

def get_weather() -> OpenMeteoService:
    return OpenMeteoService(15)

@router.get("/", response_model=CurrentWeatherResponse, summary="Получить текущую погоду по координатам")
async def weather(
    latitude: float = Query(..., ge=-90, le=90, description="Широта (-90..90)"),
    longitude: float = Query(..., ge=-180, le=180, description="Долгота (-180..180)"),
    weather_service: OpenMeteoService = Depends(get_weather),
):
    return await weather_service.get_current_weather(latitude=latitude, longitude=longitude)


@router.post("/cities", response_model=CityResponse, status_code=status.HTTP_201_CREATED, summary="Добавить город для отслеживания погоды")
async def add_city(
    name: str = Query(..., description="Название города", example="Moscow"),
    latitude: float = Query(..., ge=-90, le=90, description="Широта (-90..90)", example=55.75),
    longitude: float = Query(..., ge=-180, le=180, description="Долгота (-180..180)", example=37.61),
    user_id: int = Query(1, description="ID пользователя", example=1),
    db: Session = Depends(get_db)
):
    existing_city = db.query(City).filter(
        City.user_id == user_id,
        City.name == name
    ).first()

    if existing_city:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="City with this name already added for this user"
        )

    new_city = City(
        user_id=user_id,
        name=name,
        latitude=latitude,
        longitude=longitude,
    )

    db.add(new_city)
    db.commit()
    db.refresh(new_city)

    # Принудительно подтягиваем погоду для нового города сразу при добавлении!
    await update_all_cities_weather()

    return new_city


@router.get("/cities", response_model=List[CityResponse], summary="Получить список всех отслеживаемых городов")
async def get_cities(
    user_id: int = Query(..., description="ID пользователя"),
    db: Session = Depends(get_db)
):
    cities = db.query(City).filter(City.user_id == user_id).all()
    return cities


@router.get("/city-weather", response_model=DetailWeatherResponse, summary="Получить погоду в городе на указанное время")
async def get_city_weather(
    city_name: str = Query(..., description="Название города"),
    target_time: str = Query(..., description="Время в формате ISO (например: 2026-08-02T15:00:00)"),
    user_id: int = Query(..., description="ID пользователя"),
    include_temperature: bool = Query(True, description="Включить температуру"),
    include_humidity: bool = Query(True, description="Включить влажность"),
    include_wind_speed: bool = Query(True, description="Включить скорость ветра"),
    include_precipitation: bool = Query(True, description="Включить осадки"),
    db: Session = Depends(get_db)
):
    try:
        clean_time_str = target_time.strip()
        parsed_time = datetime.fromisoformat(clean_time_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неверный формат даты. Используйте формат YYYY-MM-DDTHH:MM:SS"
        )

    city = db.query(City).filter(City.user_id == user_id, City.name == city_name).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Город '{city_name}' не найден у пользователя с user_id={user_id}"
        )

    forecast = db.query(WeatherForecast).filter(
        WeatherForecast.city_id == city.id,
        WeatherForecast.timestamp == parsed_time
    ).first()

    if not forecast:
        forecast = (
            db.query(WeatherForecast)
            .filter(WeatherForecast.city_id == city.id)
            .order_by(func.abs(func.strftime('%s', WeatherForecast.timestamp) - func.strftime('%s', parsed_time)))
            .first()
        )

    if not forecast:
        await update_all_cities_weather()
        forecast = (
            db.query(WeatherForecast)
            .filter(WeatherForecast.city_id == city.id)
            .order_by(func.abs(func.strftime('%s', WeatherForecast.timestamp) - func.strftime('%s', parsed_time)))
            .first()
        )
    if not forecast:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Не удалось получить данные о погоде от внешнего сервиса."
        )

    return DetailWeatherResponse(
        city_name=city.name,
        timestamp=forecast.timestamp,
        temperature=forecast.temperature if include_temperature else None,
        humidity=forecast.humidity if include_humidity else None,
        wind_speed=forecast.wind_speed if include_wind_speed else None,
        precipitation=forecast.precipitation if include_precipitation else None
    )

@router.post("/users/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, summary="Регистрация пользователя")
async def register(
        username: str = Query(..., description="Имя пользователя"),
        db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким именем уже существует"
        )

    new_user = User(username=username)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
