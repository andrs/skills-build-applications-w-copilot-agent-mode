from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)

    activities: Mapped[list["Activity"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    teams: Mapped[list["Team"]] = relationship(  # noqa: F821
        secondary="team_members", back_populates="members"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} username={self.username!r}>"
