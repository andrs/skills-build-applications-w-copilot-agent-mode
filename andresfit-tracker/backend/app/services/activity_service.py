from app.repositories.activity_repository import ActivityRepository
from app.repositories.user_repository import UserRepository
from app.schemas.activity import ActivityCreate, ActivityRead
from app.services.exceptions import NotFoundError


class ActivityService:
    def __init__(self, activity_repo: ActivityRepository, user_repo: UserRepository) -> None:
        self._activity_repo = activity_repo
        self._user_repo = user_repo

    def list_activities(self) -> list[ActivityRead]:
        return [ActivityRead.model_validate(a) for a in self._activity_repo.list_all()]

    def get_activity(self, activity_id: int) -> ActivityRead:
        activity = self._activity_repo.get_by_id(activity_id)
        if not activity:
            raise NotFoundError("Activity", activity_id)
        return ActivityRead.model_validate(activity)

    def create_activity(self, payload: ActivityCreate) -> ActivityRead:
        if not self._user_repo.get_by_id(payload.user_id):
            raise NotFoundError("User", payload.user_id)
        activity = self._activity_repo.create(payload)
        return ActivityRead.model_validate(activity)

    def delete_activity(self, activity_id: int) -> None:
        if not self._activity_repo.get_by_id(activity_id):
            raise NotFoundError("Activity", activity_id)
        self._activity_repo.delete(activity_id)
