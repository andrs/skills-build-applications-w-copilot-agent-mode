from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., min_length=1, max_length=120)
    full_name: str = Field(..., min_length=1, max_length=100)


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ActivityBase(BaseModel):
    activity_type: str = Field(..., min_length=1, max_length=50)
    duration_minutes: int = Field(..., gt=0)
    calories_burned: float = Field(..., gt=0)


class ActivityCreate(ActivityBase):
    user_id: int


class ActivityRead(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    date: datetime


class TeamBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)


class TeamCreate(TeamBase):
    member_ids: list[int] = []


class TeamRead(TeamBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    members: list[UserRead] = []


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user: UserRead
    total_duration: int
    total_calories: float
    activity_count: int


class WorkoutBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    activity_type: str = Field(..., min_length=1, max_length=50)
    duration_minutes: int = Field(..., gt=0)
    difficulty: str = Field(..., pattern="^(beginner|intermediate|advanced)$")


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutRead(WorkoutBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
