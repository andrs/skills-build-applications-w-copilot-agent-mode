from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.user import UserCreate


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_username(self, username: str) -> User | None:
        result = self._session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    def get_by_email(self, email: str) -> User | None:
        result = self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    def create(self, payload: UserCreate) -> User:
        user = User(**payload.model_dump())
        self._session.add(user)
        self._session.commit()
        self._session.refresh(user)
        return user
