from fastapi import APIRouter, Depends, status

from app.dependencies import get_activity_service
from app.schemas.activity import ActivityCreate, ActivityRead
from app.services.activity_service import ActivityService

router = APIRouter(prefix="/api/activities", tags=["activities"])


@router.get("/", response_model=list[ActivityRead], summary="List all activities")
def list_activities(service: ActivityService = Depends(get_activity_service)) -> list[ActivityRead]:
    return service.list_activities()


@router.get("/{activity_id}", response_model=ActivityRead, summary="Get activity by ID")
def get_activity(
    activity_id: int,
    service: ActivityService = Depends(get_activity_service),
) -> ActivityRead:
    return service.get_activity(activity_id)


@router.post(
    "/",
    response_model=ActivityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a new activity",
)
def create_activity(
    payload: ActivityCreate,
    service: ActivityService = Depends(get_activity_service),
) -> ActivityRead:
    return service.create_activity(payload)


@router.delete(
    "/{activity_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an activity",
)
def delete_activity(
    activity_id: int,
    service: ActivityService = Depends(get_activity_service),
) -> None:
    service.delete_activity(activity_id)
