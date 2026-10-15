from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WorkoutBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    activity_type: str = Field(..., min_length=1, max_length=50)
    duration_minutes: int = Field(..., gt=0)
    difficulty: str = Field(..., pattern="^(beginner|intermediate|advanced)$")


class WorkoutCreate(WorkoutBase):
    pass


class WorkoutUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, max_length=255)
    difficulty: str | None = Field(None, pattern="^(beginner|intermediate|advanced)$")


class WorkoutRead(WorkoutBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
