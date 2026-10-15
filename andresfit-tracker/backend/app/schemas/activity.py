from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ActivityBase(BaseModel):
    activity_type: str = Field(..., min_length=1, max_length=50)
    duration_minutes: int = Field(..., gt=0)
    calories_burned: float = Field(..., gt=0)


class ActivityCreate(ActivityBase):
    user_id: int = Field(..., gt=0)


class ActivityRead(ActivityBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    date: datetime
    created_at: datetime
