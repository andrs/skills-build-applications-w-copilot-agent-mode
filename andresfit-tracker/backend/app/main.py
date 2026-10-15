from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.exception_handlers import add_exception_handlers
from app.models.base import Base
from app.routers import activities, health, leaderboard, teams, users, workouts

# Import models so SQLAlchemy registers them before create_all
import app.models  # noqa: F401

Base.metadata.create_all(bind=engine)


def create_app() -> FastAPI:
    app = FastAPI(
        title="AndresFit Tracker API",
        version="1.0.0",
        description="Fitness tracking and team management for Mergington High School",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(users.router)
    app.include_router(activities.router)
    app.include_router(teams.router)
    app.include_router(leaderboard.router)
    app.include_router(workouts.router)

    @app.get("/", tags=["root"])
    def root() -> dict:
        return {"message": "Welcome to AndresFit Tracker API", "docs": "/api/docs"}

    return app


app = create_app()
