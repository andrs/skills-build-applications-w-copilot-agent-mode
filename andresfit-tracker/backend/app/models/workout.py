from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class Workout(Base, TimestampMixin):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
    activity_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, index=True)

    def __repr__(self) -> str:
        return f"<Workout id={self.id} name={self.name!r} difficulty={self.difficulty!r}>"
