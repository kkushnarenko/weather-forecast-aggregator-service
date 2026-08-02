from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_TITLE: str = "Weather Forecast Aggregator"
    HOST: str = "127.0.0.1"
    PORT: int = 8080
    DEBUG: bool = True

    DATABASE_URI: str = "sqlite+aiosqlite:///./weather.db"

    OPEN_METEO_API_KEY: str = "https://api.open-meteo.com/v1/forecast"

settings = Settings()

