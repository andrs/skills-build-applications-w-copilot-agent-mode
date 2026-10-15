from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.repositories.base import BaseRepository
from app.schemas.workout import WorkoutCreate


class WorkoutRepository(BaseRepository[Workout]):
    model = Workout

    def list_filtered(
        self,
        difficulty: str | None = None,
        activity_type: str | None = None,
    ) -> list[Workout]:
        query = select(Workout)
        if difficulty:
            query = query.where(Workout.difficulty == difficulty)
        if activity_type:
            query = query.where(Workout.activity_type == activity_type)
        result = self._session.execute(query)
        return list(result.scalars().all())

    def create(self, payload: WorkoutCreate) -> Workout:
        workout = Workout(**payload.model_dump())
        self._session.add(workout)
        self._session.commit()
        self._session.refresh(workout)
        return workout
