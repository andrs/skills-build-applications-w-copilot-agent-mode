from typing import Generic, TypeVar

from sqlalchemy import select, delete, func
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, id: int) -> ModelT | None:
        result = self._session.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    def list_all(self) -> list[ModelT]:
        result = self._session.execute(select(self.model))
        return list(result.scalars().all())

    def delete(self, id: int) -> bool:
        result = self._session.execute(delete(self.model).where(self.model.id == id))
        self._session.commit()
        return result.rowcount > 0
