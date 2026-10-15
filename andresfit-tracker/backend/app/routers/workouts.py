from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Workout
from app.schemas import WorkoutCreate, WorkoutRead

router = APIRouter(prefix="/api/workouts", tags=["workouts"])


@router.get("/", response_model=list[WorkoutRead])
def list_workouts(
    difficulty: str | None = Query(None, pattern="^(beginner|intermediate|advanced)$"),
    activity_type: str | None = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Workout)
    if difficulty:
        query = query.filter(Workout.difficulty == difficulty)
    if activity_type:
        query = query.filter(Workout.activity_type == activity_type)
    return query.all()


@router.get("/{workout_id}", response_model=WorkoutRead)
def get_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    return workout


@router.post("/", response_model=WorkoutRead, status_code=201)
def create_workout(payload: WorkoutCreate, db: Session = Depends(get_db)):
    workout = Workout(**payload.model_dump())
    db.add(workout)
    db.commit()
    db.refresh(workout)
    return workout


@router.delete("/{workout_id}", status_code=204)
def delete_workout(workout_id: int, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    db.delete(workout)
    db.commit()
