from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.activity_repository import ActivityRepository
from app.repositories.leaderboard_repository import LeaderboardRepository
from app.repositories.team_repository import TeamRepository
from app.repositories.user_repository import UserRepository
from app.repositories.workout_repository import WorkoutRepository
from app.services.activity_service import ActivityService
from app.services.leaderboard_service import LeaderboardService
from app.services.team_service import TeamService
from app.services.user_service import UserService
from app.services.workout_service import WorkoutService


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_activity_repository(db: Session = Depends(get_db)) -> ActivityRepository:
    return ActivityRepository(db)


def get_team_repository(db: Session = Depends(get_db)) -> TeamRepository:
    return TeamRepository(db)


def get_workout_repository(db: Session = Depends(get_db)) -> WorkoutRepository:
    return WorkoutRepository(db)


def get_leaderboard_repository(db: Session = Depends(get_db)) -> LeaderboardRepository:
    return LeaderboardRepository(db)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(repo)


def get_activity_service(
    activity_repo: ActivityRepository = Depends(get_activity_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> ActivityService:
    return ActivityService(activity_repo, user_repo)


def get_team_service(
    team_repo: TeamRepository = Depends(get_team_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> TeamService:
    return TeamService(team_repo, user_repo)


def get_workout_service(repo: WorkoutRepository = Depends(get_workout_repository)) -> WorkoutService:
    return WorkoutService(repo)


def get_leaderboard_service(
    repo: LeaderboardRepository = Depends(get_leaderboard_repository),
) -> LeaderboardService:
    return LeaderboardService(repo)
