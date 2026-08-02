from pydantic import BaseModel, Field

class CityCreateRequest(BaseModel):
    user_id: int = Field(0, description="ID пользователя", example=1)
    name: str = Field(..., min_length=1, max_length=100, description="Название города", example="Moscow")
    latitude: float = Field(..., ge=-90.0, le=90.0, description="Широта (-90.0 до 90.0)", example=55.75)
    longitude: float = Field(..., ge=-180.0, le=180.0, description="Долгота (-180.0 до 180.0)", example=37.61)

class CityResponse(CityCreateRequest):
    id: int

    class Config:
        from_attributes = True