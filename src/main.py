from contextlib import asynccontextmanager
from fastapi import FastAPI, APIRouter

from src.database import Base, engine

from src.models.city import City
from src.models.weather_forecast import WeatherForecast
from src.models.user import User

from src.api.router import router as weather_router
from src.tasks.weather_updater import start_scheduler, scheduler

Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    start_scheduler()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="Weather Aggregator Service",
    version="1.0.0",
    description="API для отслеживания и агрегации прогнозов погоды",
)

api_router = APIRouter()
api_router.include_router(weather_router, tags=["Weather"])
app.include_router(api_router)