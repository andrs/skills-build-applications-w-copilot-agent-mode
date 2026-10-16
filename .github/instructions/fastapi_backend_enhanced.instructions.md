---
applyTo: "andresfit-tracker/backend/**"
---
# FastAPI Backend — Enhanced Best Practices (Async Supplement)

> This file **supplements** `fastapi_layered_architecture.instructions.md`.
> The layered file is the source of truth for layer boundaries, DI wiring, models,
> schemas, repositories, services, and exception handling. This file only adds
> cross-cutting patterns (pagination, filtering, logging, caching, rate limiting,
> background tasks, OpenAPI docs). Everything here is **async** and uses the real
> `src/` layout with routers nested under `src/api/v1/routers/`.

## Core Principles

- All routes live under `src/api/v1/routers/` and use the `/api/v1/` prefix.
- Use plural nouns for resources: `/api/v1/users/`, `/api/v1/activities/`.
- RESTful verbs: GET (list/read), POST (create), PATCH (partial update), DELETE.
- Always declare `response_model` and a `status.HTTP_*` status code.
- Routers call **services only** — never repositories, ORM models, or `AsyncSession`.
- Every data-access method is `async def` and uses SQLAlchemy 2.0 `select()`.
  Never use `session.query()`.

## Router Structure (`src/api/v1/routers/`)

```python
from fastapi import APIRouter, Depends, Query, status

from src.api.dependencies import get_user_service
from src.schemas.common import PaginatedResponse
from src.schemas.user import UserCreate, UserRead
from src.services.user_service import UserService

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/", response_model=PaginatedResponse[UserRead])
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserRead]:
    return await service.list_users(page=page, size=size)


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.create_user(payload)
```

## Pydantic Schemas — Validation (`src/schemas/`)

Use Pydantic v2. Prefer `field_validator`/`model_validator` over the removed v1 `validator`.

```python
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("username")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        return v.lower()


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    username: str
    email: EmailStr
    full_name: str
    created_at: datetime
    updated_at: datetime | None = None
```

## Efficient Async Queries (`src/repositories/`)

```python
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.team import Team
from src.repositories.base import BaseRepository


class TeamRepository(BaseRepository[Team]):
    model = Team

    async def list_with_members(self) -> list[Team]:
        result = await self._session.execute(
            select(Team).options(selectinload(Team.members))
        )
        return list(result.scalars().all())
```

## Pagination

Define generic envelopes in `src/schemas/common.py`; build pages in the **service**
from the repository's `(items, total)` result.

```python
from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
```

```python
# src/services/user_service.py
async def list_users(self, *, page: int, size: int) -> PaginatedResponse[UserRead]:
    rows, total = await self._user_repo.list(offset=(page - 1) * size, limit=size)
    return PaginatedResponse(
        items=[UserRead.model_validate(r) for r in rows],
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size,
    )
```

## Filtering & Sorting

Validate query params in the router, pass primitives to the service, build the query
in the repository.

```python
@router.get("/", response_model=list[ActivityRead])
async def list_activities(
    activity_type: str | None = Query(None),
    min_duration: int | None = Query(None, ge=0),
    sort_by: str = Query("date", pattern="^(date|duration|calories)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    service: ActivityService = Depends(get_activity_service),
) -> list[ActivityRead]:
    return await service.list_activities(
        activity_type=activity_type,
        min_duration=min_duration,
        sort_by=sort_by,
        order=order,
    )
```

```python
# repository
from sqlalchemy import asc, desc, select


async def list_filtered(
    self, *, activity_type: str | None, min_duration: int | None,
    sort_by: str, order: str,
) -> list[Activity]:
    query = select(Activity)
    if activity_type is not None:
        query = query.where(Activity.activity_type == activity_type)
    if min_duration is not None:
        query = query.where(Activity.duration_minutes >= min_duration)
    direction = desc if order == "desc" else asc
    query = query.order_by(direction(getattr(Activity, sort_by)))
    result = await self._session.execute(query)
    return list(result.scalars().all())
```

## Error Handling

Raise typed exceptions from `src/services/exceptions.py` in the service layer and map
them centrally in `src/api/exception_handlers.py`. Never raise `HTTPException` from
services, and never catch raw DB errors in routers. See the layered file for the full
`add_exception_handlers` pattern.

## Logging

```python
import logging

logger = logging.getLogger(__name__)
# Never use bare print() for logging.
```

## Caching Headers

```python
from fastapi import Depends, Response, status

from src.api.dependencies import get_workout_service
from src.schemas.workout import WorkoutRead
from src.services.workout_service import WorkoutService


@router.get("/{workout_id}", response_model=WorkoutRead)
async def get_workout(
    workout_id: int,
    response: Response,
    service: WorkoutService = Depends(get_workout_service),
) -> WorkoutRead:
    workout = await service.get_workout(workout_id)
    response.headers["Cache-Control"] = "public, max-age=3600"
    return workout
```

## Rate Limiting (optional, slowapi)

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter


@router.post("/")
@limiter.limit("5/minute")
async def create_user(request: Request, payload: UserCreate, ...):
    ...
```

## Background Tasks

```python
from fastapi import BackgroundTasks


@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    user = await service.create_user(payload)
    background_tasks.add_task(logger.info, "user created: %s", user.id)
    return user
```

## Health & Monitoring

Expose `/healthz` (liveness) and `/ready` (readiness). The readiness probe runs
`await db.execute(text("SELECT 1"))`. See `src/api/v1/routers/health.py`.

## OpenAPI Documentation

```python
# src/main.py
app = FastAPI(
    title="AndresFit Tracker API",
    description="Fitness tracking and team management API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "users", "description": "User management operations"},
        {"name": "activities", "description": "Activity tracking"},
        {"name": "teams", "description": "Team management"},
        {"name": "leaderboard", "description": "Competition rankings"},
        {"name": "workouts", "description": "Workout suggestions"},
    ],
)
```

## Testing Patterns

```python
# Parametrized validation (integration test with AsyncClient)
import pytest


@pytest.mark.parametrize(
    "username,email,expected",
    [
        ("valid_user", "valid@email.com", 201),
        ("ab", "valid@email.com", 422),
        ("valid_user", "invalid-email", 422),
    ],
)
async def test_create_user_validation(client, username, email, expected):
    response = await client.post(
        "/api/v1/users/",
        json={"username": username, "email": email, "full_name": "Test User"},
    )
    assert response.status_code == expected
```

Unit tests mock repositories with `AsyncMock`; integration tests use an in-memory
SQLite database (`sqlite+aiosqlite:///:memory:`) with the `client` fixture.

## CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Code Quality Rules

### Always
- Type hints on every parameter and return value.
- `async def` for all routes, services, and repository methods.
- Named `status.HTTP_*` constants — never bare integers.
- Return Pydantic schemas from routers (`model_validate()` in services) — never raw ORM objects.
- `selectinload`/`joinedload` to prevent N+1 queries.
- Drive config through `src/config.py` / `.env`.

### Never
- Hardcode configuration values.
- Use `session.query()` — always `select()` from SQLAlchemy 2.0.
- Write business logic or DB queries in routers.
- Raise `HTTPException` from services.
- Use synchronous blocking I/O inside `async def`.
- Use bare `print()` for logging.

## Port Configuration

- API server: `8000`.
- Use Codespace-aware URLs when `CODESPACE_NAME` is set (`settings.base_url`).
- Health checks at `/healthz` and `/ready` (no auth required).
