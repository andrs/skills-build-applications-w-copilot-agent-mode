from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserRead
from app.services.exceptions import DuplicateResourceError, NotFoundError


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def list_users(self) -> list[UserRead]:
        return [UserRead.model_validate(u) for u in self._repo.list_all()]

    def get_user(self, user_id: int) -> UserRead:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        return UserRead.model_validate(user)

    def create_user(self, payload: UserCreate) -> UserRead:
        if self._repo.get_by_username(payload.username):
            raise DuplicateResourceError("User", "username", payload.username)
        if self._repo.get_by_email(payload.email):
            raise DuplicateResourceError("User", "email", payload.email)
        user = self._repo.create(payload)
        return UserRead.model_validate(user)

    def delete_user(self, user_id: int) -> None:
        user = self._repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("User", user_id)
        self._repo.delete(user_id)
