from pydantic import BaseModel, ConfigDict

from app.schemas.user import UserRead


class LeaderboardEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user: UserRead
    total_duration: int
    total_calories: float
    activity_count: int
