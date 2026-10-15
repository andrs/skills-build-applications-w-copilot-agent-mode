from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Activity, User
from app.schemas import LeaderboardEntry, UserRead

router = APIRouter(prefix="/api/leaderboard", tags=["leaderboard"])


@router.get("/", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    results = (
        db.query(
            User,
            func.coalesce(func.sum(Activity.duration_minutes), 0).label("total_duration"),
            func.coalesce(func.sum(Activity.calories_burned), 0.0).label("total_calories"),
            func.count(Activity.id).label("activity_count"),
        )
        .outerjoin(Activity, User.id == Activity.user_id)
        .group_by(User.id)
        .order_by(func.coalesce(func.sum(Activity.calories_burned), 0.0).desc())
        .all()
    )
    return [
        LeaderboardEntry(
            user=UserRead.model_validate(user),
            total_duration=int(total_duration),
            total_calories=float(total_calories),
            activity_count=int(activity_count),
        )
        for user, total_duration, total_calories, activity_count in results
    ]
