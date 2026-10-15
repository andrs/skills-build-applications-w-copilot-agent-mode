from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.repositories.base import BaseRepository
from app.schemas.activity import ActivityCreate


class ActivityRepository(BaseRepository[Activity]):
    model = Activity

    def create(self, payload: ActivityCreate) -> Activity:
        activity = Activity(**payload.model_dump())
        self._session.add(activity)
        self._session.commit()
        self._session.refresh(activity)
        return activity

    def list_by_user(self, user_id: int) -> list[Activity]:
        result = self._session.execute(
            select(Activity).where(Activity.user_id == user_id)
        )
        return list(result.scalars().all())
