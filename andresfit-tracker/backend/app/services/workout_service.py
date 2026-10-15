from app.repositories.workout_repository import WorkoutRepository
from app.schemas.workout import WorkoutCreate, WorkoutRead
from app.services.exceptions import NotFoundError


class WorkoutService:
    def __init__(self, repo: WorkoutRepository) -> None:
        self._repo = repo

    def list_workouts(
        self,
        difficulty: str | None = None,
        activity_type: str | None = None,
    ) -> list[WorkoutRead]:
        workouts = self._repo.list_filtered(difficulty=difficulty, activity_type=activity_type)
        return [WorkoutRead.model_validate(w) for w in workouts]

    def get_workout(self, workout_id: int) -> WorkoutRead:
        workout = self._repo.get_by_id(workout_id)
        if not workout:
            raise NotFoundError("Workout", workout_id)
        return WorkoutRead.model_validate(workout)

    def create_workout(self, payload: WorkoutCreate) -> WorkoutRead:
        workout = self._repo.create(payload)
        return WorkoutRead.model_validate(workout)

    def delete_workout(self, workout_id: int) -> None:
        if not self._repo.get_by_id(workout_id):
            raise NotFoundError("Workout", workout_id)
        self._repo.delete(workout_id)
