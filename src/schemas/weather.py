from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class OpenMeteoCurrentDTO(BaseModel):
    time: str
    temperature_2m : float
    wind_speed_10m : float
    surface_pressure: Optional[float] = None

class OpenMeteoHourlyDTO(BaseModel):
    time: list[str]
    wind_speed_10m : list[float]
    temperature_2m : list[float]
    relative_humidity_2m : list[float]
    surface_pressure: list[Optional[float]]
    precipitation: list[Optional[float]]

class OpenMeteoDTOResponse(BaseModel):
    current: Optional[OpenMeteoCurrentDTO] = None
    hourly: Optional[OpenMeteoHourlyDTO] = None

class CurrentWeatherResponse(BaseModel):
    temperature : float = Field(..., description="Температура в Цельсиях")
    wind_speed : float = Field(..., description="Скорость ветра в м/с")
    pressure : Optional[float] = Field(..., description="Атмосферное давление")


class DetailWeatherResponse(BaseModel):
    city_name: str
    timestamp: datetime
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    precipitation: Optional[float] = None

    

