from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.user import UserRead


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)


class TeamCreate(TeamBase):
    member_ids: list[int] = []


class TeamUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    members: list[UserRead] = []
    created_at: datetime
