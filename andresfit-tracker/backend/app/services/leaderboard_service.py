from app.repositories.leaderboard_repository import LeaderboardRepository
from app.schemas.leaderboard import LeaderboardEntry


class LeaderboardService:
    def __init__(self, repo: LeaderboardRepository) -> None:
        self._repo = repo

    def get_rankings(self) -> list[LeaderboardEntry]:
        return self._repo.get_rankings()
