from pydantic import BaseModel, Field

class UserCreateRequest(BaseModel):
    username: str = Field(..., min_length=2, max_length=50, description="Имя пользователя", example="alex")

class UserResponse(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True