---
agent: 'agent'
description: 'Build or extend the AndresFit Tracker FastAPI backend with async best practices and the layered src/ architecture'
---

Build or extend the **AndresFit Tracker** FastAPI backend following the project's
layered architecture and async best practices.

## Context — read first

- `.github/instructions/fastapi_layered_architecture.instructions.md` — layer rules (source of truth)
- `.github/instructions/fastapi_backend_enhanced.instructions.md` — async cross-cutting patterns
- `AGENTS.md` — real structure, run and test commands

Everything below is **async** (`AsyncSession`, `select()`), uses **SQLite async**
(`sqlite+aiosqlite`), and uses the real **`src/`** layout. Never use `app/`,
`session.query()`, or synchronous `Session`.

## Target Structure

```
andresfit-tracker/backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # create_app() factory + lifespan table creation
│   ├── config.py            # pydantic-settings (CODESPACE_NAME aware)
│   ├── database.py          # async engine + get_db() session dependency
│   ├── seed.py              # async sample-data seeder
│   ├── api/
│   │   ├── dependencies.py       # DI wiring (service ← repository ← session)
│   │   ├── exception_handlers.py # ServiceError → HTTP status mapping
│   │   └── v1/routers/           # health, users, activities, teams, leaderboard, workouts
│   ├── services/            # business logic + typed exceptions
│   ├── repositories/        # async data access (select/update/delete only)
│   ├── models/              # SQLAlchemy 2.0 ORM + TimestampMixin
│   └── schemas/             # Pydantic Create/Read/Update
├── tests/
│   ├── conftest.py          # in-memory SQLite + AsyncClient fixtures
│   └── unit/                # service unit tests (AsyncMock repositories)
├── .env.example
├── requirements.txt
└── pytest.ini
```

## Layer Rules (enforce strictly)

- **Routers** (`src/api/v1/routers/`): HTTP only. Inject services with `Depends()`.
  Declare `response_model`, `status_code`, `summary`. No business logic, no DB access.
- **Services** (`src/services/`): business rules. Accept and return Pydantic schemas,
  use `model_validate()` for ORM → schema. Raise typed exceptions from
  `src/services/exceptions.py` — never `HTTPException`.
- **Repositories** (`src/repositories/`): async SQLAlchemy 2.0 `select()/update()/delete()`.
  Return `None` for not-found. Use `selectinload`/`joinedload` to avoid N+1.
- **Models** (`src/models/`): `Mapped[]` + `mapped_column()`, `TimestampMixin`,
  `back_populates`, `index=True` on FKs, `cascade="all, delete-orphan"` on children.
- **Schemas** (`src/schemas/`): `{Resource}Create/Read/Update`; `Read` sets
  `ConfigDict(from_attributes=True)`; `Update` fields optional; `Field(...)` constraints.

## Required Endpoints

### Users (`/api/v1/users/`)
- `GET /` list (paginated, searchable) · `GET /{user_id}` · `POST /` (unique username/email)
- `PATCH /{user_id}` · `DELETE /{user_id}` · `GET /{user_id}/activities`

### Activities (`/api/v1/activities/`)
- `GET /` (filter by type, user, date range) · `GET /{activity_id}` · `POST /`
- `DELETE /{activity_id}` · `GET /stats`

### Teams (`/api/v1/teams/`)
- `GET /` · `GET /{team_id}` (with members) · `POST /` · `PATCH /{team_id}` · `DELETE /{team_id}`
- `POST /{team_id}/members/{user_id}` · `DELETE /{team_id}/members/{user_id}`

### Leaderboard (`/api/v1/leaderboard/`)
- `GET /` (sorted by calories) · `GET /weekly` · `GET /teams`

### Workouts (`/api/v1/workouts/`)
- `GET /` (filter by difficulty, type) · `GET /{workout_id}` · `POST /`
- `DELETE /{workout_id}` · `GET /recommended`

## Configuration (`src/config.py`)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "AndresFit Tracker API"
    debug: bool = False
    version: str = "1.0.0"
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./andresfit.db"
    db_echo: bool = False

    backend_cors_origins: list[str] = ["http://localhost:5173"]
    default_page_size: int = 50
    max_page_size: int = 100


settings = Settings()
```

## Async Database Setup (`src/database.py`)

```python
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from src.config import settings

engine = create_async_engine(settings.database_url, pool_pre_ping=True, echo=settings.db_echo)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

## Testing Requirements

- `conftest.py`: in-memory SQLite (`sqlite+aiosqlite:///:memory:`), `AsyncClient` with
  `ASGITransport`, `get_db` override, sample-data fixtures.
- Each endpoint: success (200/201/204), not-found (404), duplicate (409), validation (422).
- Unit tests mock repositories with `AsyncMock`.
- Use `@pytest.mark.parametrize` for validation scenarios.

```python
@pytest.mark.parametrize("username,email,expected", [
    ("valid_user", "valid@email.com", 201),
    ("ab", "valid@email.com", 422),
    ("valid_user", "invalid-email", 422),
])
async def test_create_user(client, username, email, expected):
    r = await client.post("/api/v1/users/", json={
        "username": username, "email": email, "full_name": "Test User",
    })
    assert r.status_code == expected
```

## Requirements

**requirements.txt**
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
aiosqlite>=0.20.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pydantic[email]>=2.0.0
python-multipart>=0.0.9
```

**requirements-dev.txt**
```
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
faker>=24.0.0
```

## Execution Order

1. `config.py`, `.env.example`
2. `database.py` (async engine + `get_db`)
3. `models/base.py` (Base + TimestampMixin), then all models
4. All schemas (Create/Read/Update + `common.py`)
5. Repositories (`base.py` + per-resource)
6. Services + `exceptions.py`
7. `api/dependencies.py`, `api/exception_handlers.py`, routers
8. `main.py` (`create_app()` factory, lifespan table creation, CORS, routers, handlers)
9. `seed.py` (async, idempotent)
10. Tests (unit + integration)

## Success Criteria

- All layers respect their boundaries (routers → services → repositories → models).
- All endpoints declare `response_model` and `status_code`.
- Services raise typed exceptions; handlers map them to HTTP codes.
- No `session.query()`, no synchronous `Session`, no hardcoded values.
- `/healthz` and `/ready` work; seed data loads; all tests pass.

## Run Commands

```bash
# Setup
python -m venv andresfit-tracker/backend/.venv
andresfit-tracker/backend/.venv/bin/pip install -r andresfit-tracker/backend/requirements.txt

# Seed + run (from andresfit-tracker/backend with venv active)
python -m src.seed
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Tests
python -m pytest tests -v
```
