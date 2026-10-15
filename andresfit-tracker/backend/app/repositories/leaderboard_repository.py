from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.activity import Activity
from app.models.user import User
from app.schemas.leaderboard import LeaderboardEntry
from app.schemas.user import UserRead


class LeaderboardRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_rankings(self) -> list[LeaderboardEntry]:
        results = self._session.execute(
            select(
                User,
                func.coalesce(func.sum(Activity.duration_minutes), 0).label("total_duration"),
                func.coalesce(func.sum(Activity.calories_burned), 0.0).label("total_calories"),
                func.count(Activity.id).label("activity_count"),
            )
            .outerjoin(Activity, User.id == Activity.user_id)
            .group_by(User.id)
            .order_by(func.coalesce(func.sum(Activity.calories_burned), 0.0).desc())
        ).all()

        return [
            LeaderboardEntry(
                user=UserRead.model_validate(user),
                total_duration=int(total_duration),
                total_calories=float(total_calories),
                activity_count=int(activity_count),
            )
            for user, total_duration, total_calories, activity_count in results
        ]
