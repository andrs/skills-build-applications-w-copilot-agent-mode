from fastapi import APIRouter, Depends, Query, status

from app.dependencies import get_workout_service
from app.schemas.workout import WorkoutCreate, WorkoutRead
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/api/workouts", tags=["workouts"])


@router.get("/", response_model=list[WorkoutRead], summary="List workouts with optional filters")
def list_workouts(
    difficulty: str | None = Query(None, pattern="^(beginner|intermediate|advanced)$"),
    activity_type: str | None = Query(None),
    service: WorkoutService = Depends(get_workout_service),
) -> list[WorkoutRead]:
    return service.list_workouts(difficulty=difficulty, activity_type=activity_type)


@router.get("/{workout_id}", response_model=WorkoutRead, summary="Get workout by ID")
def get_workout(
    workout_id: int,
    service: WorkoutService = Depends(get_workout_service),
) -> WorkoutRead:
    return service.get_workout(workout_id)


@router.post(
    "/",
    response_model=WorkoutRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new workout suggestion",
)
def create_workout(
    payload: WorkoutCreate,
    service: WorkoutService = Depends(get_workout_service),
) -> WorkoutRead:
    return service.create_workout(payload)


@router.delete(
    "/{workout_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a workout",
)
def delete_workout(
    workout_id: int,
    service: WorkoutService = Depends(get_workout_service),
) -> None:
    service.delete_workout(workout_id)
