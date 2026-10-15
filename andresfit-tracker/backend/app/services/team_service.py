from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository
from app.schemas.team import TeamCreate, TeamRead
from app.services.exceptions import DuplicateResourceError, NotFoundError


class TeamService:
    def __init__(self, team_repo: TeamRepository, user_repo: UserRepository) -> None:
        self._team_repo = team_repo
        self._user_repo = user_repo

    def list_teams(self) -> list[TeamRead]:
        return [TeamRead.model_validate(t) for t in self._team_repo.list_all()]

    def get_team(self, team_id: int) -> TeamRead:
        team = self._team_repo.get_by_id(team_id)
        if not team:
            raise NotFoundError("Team", team_id)
        return TeamRead.model_validate(team)

    def create_team(self, payload: TeamCreate) -> TeamRead:
        if self._team_repo.get_by_name(payload.name):
            raise DuplicateResourceError("Team", "name", payload.name)
        members = []
        for uid in payload.member_ids:
            user = self._user_repo.get_by_id(uid)
            if not user:
                raise NotFoundError("User", uid)
            members.append(user)
        team = self._team_repo.create(payload, members)
        return TeamRead.model_validate(team)

    def delete_team(self, team_id: int) -> None:
        if not self._team_repo.get_by_id(team_id):
            raise NotFoundError("Team", team_id)
        self._team_repo.delete(team_id)
