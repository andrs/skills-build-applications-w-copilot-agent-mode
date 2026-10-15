"""Seed the andresfit database with test data."""

from datetime import datetime, timedelta

from app.database import Base, SessionLocal, engine
from app.models import Activity, Team, User, Workout


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).count() > 0:
        print("Database already seeded — skipping.")
        db.close()
        return

    users = [
        User(username="paul_octo", email="paul@mergington.edu", full_name="Paul Octo"),
        User(username="jessica_cat", email="jessica@mergington.edu", full_name="Jessica Cat"),
        User(username="alex_run", email="alex@mergington.edu", full_name="Alex Runner"),
        User(username="maria_fit", email="maria@mergington.edu", full_name="Maria Fitness"),
        User(username="john_lift", email="john@mergington.edu", full_name="John Lifter"),
    ]
    db.add_all(users)
    db.flush()

    now = datetime.utcnow()
    activities = [
        Activity(user_id=users[0].id, activity_type="running", duration_minutes=30, calories_burned=300, date=now - timedelta(days=1)),
        Activity(user_id=users[0].id, activity_type="walking", duration_minutes=45, calories_burned=150, date=now - timedelta(days=2)),
        Activity(user_id=users[1].id, activity_type="strength", duration_minutes=60, calories_burned=400, date=now - timedelta(days=1)),
        Activity(user_id=users[2].id, activity_type="running", duration_minutes=50, calories_burned=500, date=now),
        Activity(user_id=users[2].id, activity_type="running", duration_minutes=40, calories_burned=380, date=now - timedelta(days=3)),
        Activity(user_id=users[3].id, activity_type="walking", duration_minutes=60, calories_burned=200, date=now - timedelta(days=1)),
        Activity(user_id=users[3].id, activity_type="strength", duration_minutes=45, calories_burned=350, date=now - timedelta(days=2)),
        Activity(user_id=users[4].id, activity_type="strength", duration_minutes=90, calories_burned=600, date=now),
    ]
    db.add_all(activities)

    team_alpha = Team(name="Alpha Runners", description="Morning running crew", members=[users[0], users[2]])
    team_beta = Team(name="Beta Lifters", description="Strength training squad", members=[users[1], users[4]])
    team_gamma = Team(name="Gamma Walkers", description="Walking club", members=[users[3], users[0]])
    db.add_all([team_alpha, team_beta, team_gamma])

    workouts = [
        Workout(name="Morning Jog", description="Easy 30-min jog", activity_type="running", duration_minutes=30, difficulty="beginner"),
        Workout(name="Interval Sprints", description="High-intensity intervals", activity_type="running", duration_minutes=25, difficulty="advanced"),
        Workout(name="Power Walk", description="Brisk walking session", activity_type="walking", duration_minutes=45, difficulty="beginner"),
        Workout(name="Full Body Strength", description="Compound lifts", activity_type="strength", duration_minutes=60, difficulty="intermediate"),
        Workout(name="Advanced Deadlifts", description="Heavy deadlift program", activity_type="strength", duration_minutes=50, difficulty="advanced"),
    ]
    db.add_all(workouts)

    db.commit()
    db.close()
    print("Database seeded successfully with test data.")


if __name__ == "__main__":
    seed()
