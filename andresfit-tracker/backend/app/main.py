from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import activities, leaderboard, teams, users, workouts

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AndresFit Tracker API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(activities.router)
app.include_router(teams.router)
app.include_router(leaderboard.router)
app.include_router(workouts.router)


@app.get("/")
def root():
    return {"message": "Welcome to AndresFit Tracker API"}
