from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.team import Team
from app.models.user import User
from app.repositories.base import BaseRepository
from app.schemas.team import TeamCreate


class TeamRepository(BaseRepository[Team]):
    model = Team

    def get_by_name(self, name: str) -> Team | None:
        result = self._session.execute(select(Team).where(Team.name == name))
        return result.scalar_one_or_none()

    def create(self, payload: TeamCreate, members: list[User]) -> Team:
        team = Team(name=payload.name, description=payload.description, members=members)
        self._session.add(team)
        self._session.commit()
        self._session.refresh(team)
        return team
