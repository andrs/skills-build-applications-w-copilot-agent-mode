from fastapi import APIRouter, Depends

from app.dependencies import get_leaderboard_service
from app.schemas.leaderboard import LeaderboardEntry
from app.services.leaderboard_service import LeaderboardService

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get(
    "/",
    response_model=list[LeaderboardEntry],
    summary="Get leaderboard ranked by total calories",
)
def get_leaderboard(
    service: LeaderboardService = Depends(get_leaderboard_service),
) -> list[LeaderboardEntry]:
    return service.get_rankings()
