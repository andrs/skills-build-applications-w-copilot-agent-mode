from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., min_length=5, max_length=120)
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, min_length=5, max_length=120)


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
