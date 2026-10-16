# Backend Generation Prompt for GitHub Copilot — AndresFit Tracker

> Generate a complete, production-ready FastAPI backend for the **AndresFit Tracker**
> application. You are acting as a **Principal Backend Architect and Lead Python
> Engineer**. Follow the repository instruction files exactly:
> `.github/copilot-instructions.md`, `.github/instructions/fastapi_layered_architecture.instructions.md`,
> `.github/instructions/fastapi_backend_enhanced.instructions.md`, and
> `.github/instructions/andresfit_fastapi_backend.instructions.md`.
> Where this prompt and those files overlap, the instruction files win.

---

## 1. Tech Stack (mandatory)

| Concern | Technology |
|---------|-----------|
| Language | Python >= 3.12 |
| Framework | FastAPI (app-factory + `lifespan`) |
| Server | Uvicorn (ASGI) |
| Database | SQLite via `sqlite+aiosqlite` (async) |
| ORM | SQLAlchemy 2.0 typed ORM (`Mapped`, `mapped_column`, `select()`) — **async** |
| Validation | Pydantic v2 + `pydantic-settings` |
| Testing | pytest · pytest-asyncio · httpx `AsyncClient` |

All route handlers, service methods, and repository methods **must** be `async def`.
Never use `session.query()`; use SQLAlchemy 2.0 `select()/update()/delete()`.

---

## 2. Mandatory Layered Architecture

Every feature flows strictly top-to-bottom. **Never skip or merge layers.**

```
HTTP → Router (API) → Service → Repository → Model
```

| Layer | May import | Must NOT import |
|-------|-----------|-----------------|
| Routers (`api/v1/routers/`) | schemas, services, `Depends` | models, repositories, SQLAlchemy |
| Services (`services/`) | schemas, repositories, exceptions | FastAPI, `Request`, ORM models |
| Repositories (`repositories/`) | models, SQLAlchemy | schemas, services, FastAPI |
| Models (`models/`) | SQLAlchemy | Pydantic, FastAPI |
| Schemas (`schemas/`) | Pydantic | SQLAlchemy, FastAPI |

Rules:
- Routers contain **HTTP only** — no business logic, no DB access. Inject services with `Depends()`.
- Services accept and return **Pydantic schemas**, use `model_validate()` for ORM → schema, and raise **typed exceptions only** (never `HTTPException`).
- Repositories return `None` on not-found (never raise), and use `selectinload()` to avoid N+1 queries.
- Map service exceptions to HTTP codes centrally in `api/exception_handlers.py`.

---

## 3. Project Structure (exact)

```
andresfit-tracker/backend/
├── src/
│   ├── __init__.py
│   ├── main.py                 # create_app() factory + lifespan table creation
│   ├── config.py               # pydantic-settings (CODESPACE_NAME aware)
│   ├── database.py             # async engine + AsyncSession + get_db dependency
│   ├── seed.py                 # async sample-data seeder
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py     # DI wiring: service ← repository ← session
│   │   ├── exception_handlers.py  # ServiceError → HTTP status mapping
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── routers/
│   │           ├── __init__.py
│   │           ├── health.py        # /healthz + /ready
│   │           ├── users.py
│   │           ├── activities.py
│   │           ├── teams.py
│   │           ├── leaderboard.py
│   │           └── workouts.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── exceptions.py       # ServiceError, NotFoundError, DuplicateResourceError, InvalidOperationError
│   │   ├── user_service.py
│   │   ├── activity_service.py
│   │   ├── team_service.py
│   │   ├── leaderboard_service.py
│   │   └── workout_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py             # generic async repository base
│   │   ├── user_repository.py
│   │   ├── activity_repository.py
│   │   ├── team_repository.py
│   │   ├── leaderboard_repository.py
│   │   └── workout_repository.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # DeclarativeBase + TimestampMixin
│   │   ├── user.py
│   │   ├── activity.py
│   │   ├── team.py
│   │   └── workout.py
│   └── schemas/
│       ├── __init__.py
│       ├── common.py           # PaginatedResponse envelope
│       ├── user.py
│       ├── activity.py
│       ├── team.py
│       ├── leaderboard.py
│       └── workout.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # async client + in-memory DB fixtures
│   ├── test_api.py             # integration tests
│   └── unit/
│       ├── __init__.py
│       └── test_user_service.py
├── pytest.ini                  # asyncio_mode=auto, pythonpath=.
└── requirements.txt
```

---

## 4. Models (`src/models/`) — SQLAlchemy 2.0 typed ORM

Every model uses `Mapped[]` + `mapped_column()`, includes `TimestampMixin`
(`created_at`, `updated_at`), declares relationships with `back_populates`,
adds `index=True` on all FK columns, and `cascade="all, delete-orphan"` on child relationships.

### User (`users`)
- `id`: int PK, index
- `username`: `String(50)`, unique, not null
- `email`: `String(120)`, unique, not null
- `full_name`: `String(100)`, not null
- `activities`: one-to-many → Activity (`cascade="all, delete-orphan"`)
- `teams`: many-to-many → Team (via `team_members`)

### Activity (`activities`)
- `id`: int PK, index
- `user_id`: int FK → users.id, index, not null
- `activity_type`: `String(50)`, not null — `running | walking | strength`
- `duration_minutes`: int, not null
- `calories_burned`: float, not null
- `date`: datetime, default `utcnow`
- `user`: many-to-one → User (`back_populates`)

### Team (`teams`)
- `id`: int PK, index
- `name`: `String(100)`, unique, not null
- `description`: `String(255)`, nullable
- `members`: many-to-many → User (via `team_members`, `back_populates`)

### Workout (`workouts`)
- `id`: int PK, index
- `name`: `String(100)`, not null
- `description`: `String(255)`, nullable
- `activity_type`: `String(50)`, not null — `running | walking | strength`
- `duration_minutes`: int, not null
- `difficulty`: `String(20)`, not null — `beginner | intermediate | advanced`

### Association table
- `team_members`: `Table` linking `team_id` ↔ `user_id` (composite PK).

---

## 5. Schemas (`src/schemas/`) — Pydantic v2

For every resource provide `{Resource}Create`, `{Resource}Read`, `{Resource}Update`.
- `Read` schemas: `model_config = ConfigDict(from_attributes=True)`.
- `Update` schemas: every field optional (`field: type | None = None`).
- Use `Field(...)` constraints (`gt`, `ge`, `min_length`, `max_length`, `pattern`).
- Use `model_validator` for cross-field validation where needed.

- **User**: `username` (`min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$"`), `email` (`EmailStr`), `full_name` (`1..100`).
- **Activity**: `activity_type` (pattern enum), `duration_minutes` (`gt=0`), `calories_burned` (`gt=0`); `Create` adds `user_id`; `Read` adds `id`, `user_id`, `date`.
- **Team**: `name` (`1..100`), `description` (optional, `max_length=255`); `Create` adds `member_ids: list[int]`; `Read` adds `id`, `members: list[UserRead]`.
- **Workout**: `name`, `description?`, `activity_type` (pattern), `duration_minutes` (`gt=0`), `difficulty` (`pattern="^(beginner|intermediate|advanced)$"`).
- **Leaderboard**: `LeaderboardEntry` = `user: UserRead`, `total_duration: int`, `total_calories: float`, `activity_count: int`.
- **common.py**: generic `PaginatedResponse[T]` (`items`, `total`, `page`, `size`, `pages`).

---

## 6. Service exceptions (`src/services/exceptions.py`)

```python
class ServiceError(Exception): ...
class NotFoundError(ServiceError): ...          # → 404
class DuplicateResourceError(ServiceError): ...  # → 409
class InvalidOperationError(ServiceError): ...   # → 400
```

Register handlers in `src/api/exception_handlers.py` returning **structured** error
bodies (`message`, `code`, `resource`, `id`) — never plain strings.

---

## 7. API Endpoints — prefix `/api/v1/`

Every endpoint declares `response_model` **and** `status_code`, uses `status.HTTP_*`
constants, and injects a service via `Depends()`.

### Health (`health.py`)
- `GET /healthz` → `{"status": "alive"}`
- `GET /ready` → executes `SELECT 1`; returns `503` on failure.

### Users (`/api/v1/users/`)
- `GET /` → list users
- `GET /{user_id}` → `404` if missing
- `POST /` → `201`; `409` on duplicate username/email; `422` on validation
- `DELETE /{user_id}` → `204`; `404` if missing

### Activities (`/api/v1/activities/`)
- `GET /` → list (optional `?activity_type=` and `?user_id=` filters)
- `GET /{activity_id}` → `404` if missing
- `POST /` → `201`; `404` if user not found; `422` on invalid duration/calories
- `DELETE /{activity_id}` → `204`; `404` if missing

### Teams (`/api/v1/teams/`)
- `GET /` → list teams with members (eager-loaded)
- `GET /{team_id}` → `404` if missing
- `POST /` → `201`; `409` on duplicate name; `404` if any member not found
- `DELETE /{team_id}` → `204`; `404` if missing

### Leaderboard (`/api/v1/leaderboard/`)
- `GET /` → ranked list ordered by `total_calories` descending.
  - Aggregate with `func.sum(duration_minutes)`, `func.sum(calories_burned)`, `func.count(activities.id)`.
  - **Left join** users → activities so users with no activity appear with `0` values via `func.coalesce(...)`.

### Workouts (`/api/v1/workouts/`)
- `GET /` → list with optional `?difficulty=` and `?activity_type=` filters
- `GET /{workout_id}` → `404` if missing
- `POST /` → `201`; `422` on invalid difficulty/type
- `DELETE /{workout_id}` → `204`; `404` if missing

---

## 8. Application wiring

### `src/main.py`
- `create_app()` factory returning the `FastAPI` instance.
- `lifespan` context manager creates tables on startup (async `engine.begin()` + `run_sync`).
- CORS middleware driven by `settings.cors_origins` (not a hardcoded `["*"]`).
- Register exception handlers from `api/exception_handlers.py`.
- Include all v1 routers under `settings.api_prefix` (`/api/v1`).
- Root `GET /` → `{"message": "Welcome to AndresFit Tracker API"}`.

### `src/config.py`
- `Settings(BaseSettings)` with `SettingsConfigDict(env_file=".env")`.
- Keys: `database_url` (`sqlite+aiosqlite:///./andresfit.db`), `api_prefix="/api/v1"`, `cors_origins`, `debug`.
- `base_url` property: Codespaces URL on port 8000 when `CODESPACE_NAME` is set, else `http://localhost:8000`.
- No hardcoded values anywhere else.

### `src/database.py`
- `create_async_engine(settings.database_url, pool_pre_ping=True)`.
- `async_sessionmaker(expire_on_commit=False)`.
- `async def get_db()` yielding an `AsyncSession` with try/finally cleanup.
- `DeclarativeBase` lives in `models/base.py` alongside `TimestampMixin`.

### `src/api/dependencies.py`
- Factory functions wiring `service ← repository ← session`, e.g.
  `get_user_service(db: AsyncSession = Depends(get_db)) -> UserService`.

---

## 9. Seed script (`src/seed.py`) — async

Realistic Mergington High School data:
- **5 users**: `paul_octo`, `jessica_cat`, `alex_run`, `maria_fit`, `john_lift`.
- **8 activities**: mix of running/walking/strength with varied durations and calories.
- **3 teams**: Alpha Runners, Beta Lifters, Gamma Walkers (with member assignments).
- **5 workouts**: spanning all difficulties and activity types.
- Skip seeding if users already exist.
- Print `"Database seeded successfully with test data."`.

---

## 10. Testing

### `pytest.ini`
```
[pytest]
asyncio_mode = auto
pythonpath = .
```

### `tests/conftest.py`
- In-memory DB: `sqlite+aiosqlite:///:memory:`.
- Override `get_db` with a test `AsyncSession`.
- Create/drop tables around each test.
- Provide an `httpx.AsyncClient` fixture bound to the ASGI app.

### `tests/test_api.py` (integration) — cover success, 404, 409, and 422 per resource
- **Users (8):** create `201`; duplicate username `409`; invalid payload `422`; list; get by id; missing `404`; delete `204`; deleted-then-get `404`.
- **Activities (5):** create `201`; invalid `user_id` `404`; invalid duration `422`; list; delete.
- **Teams (6):** create with members `201`; duplicate name `409`; invalid member id `404`; list; get by id; delete.
- **Leaderboard (2):** empty → `[]`; ordered by `total_calories` descending.
- **Workouts (5):** create `201`; invalid difficulty `422`; filter by difficulty; filter by activity_type; delete.
- Use `pytest.mark.parametrize` for validation matrices.

### `tests/unit/test_user_service.py`
- Mock the repository with `AsyncMock`; test service logic in isolation (e.g. `DuplicateResourceError` raised when username exists).

---

## 11. `requirements.txt`
```
fastapi>=0.115.0
uvicorn>=0.30.0
sqlalchemy>=2.0.0
aiosqlite>=0.20.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
email-validator>=2.0.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
httpx>=0.27.0
```

---

## 12. HTTP status mapping

| Scenario | Status |
|----------|--------|
| Resource created | `201 Created` |
| Successful deletion | `204 No Content` |
| Validation error (Pydantic) | `422` (automatic) |
| Duplicate resource | `409 Conflict` |
| Business rule violated | `400 Bad Request` |
| Resource not found | `404 Not Found` |
| DB unavailable (`/ready`) | `503 Service Unavailable` |

---

## 13. Run commands (Windows / PowerShell)

```powershell
# Setup
python -m venv andresfit-tracker/backend/.venv
andresfit-tracker/backend/.venv/Scripts/python.exe -m pip install -r andresfit-tracker/backend/requirements.txt

# Seed database from the repository root
$env:PYTHONPATH = "andresfit-tracker/backend"
andresfit-tracker/backend/.venv/Scripts/python.exe -m src.seed

# Start server from the repository root
andresfit-tracker/backend/.venv/Scripts/uvicorn.exe src.main:app --app-dir andresfit-tracker/backend --reload --host 0.0.0.0 --port 8000

# Run tests from the repository root
andresfit-tracker/backend/.venv/Scripts/python.exe -m pytest --rootdir=andresfit-tracker/backend andresfit-tracker/backend/tests -v
```

> Never change directories in commands; reference target paths directly.
> Forwarded ports: `8000` (API), `5173` (frontend) — do not expose any others.

---

## Acceptance Criteria

1. Strict **API → Service → Repository → Model** separation; no layer violations.
2. Fully **async** stack (routes, services, repositories, DB session, seeder, tests).
3. All routes declare `response_model` + `status_code` and use `status.HTTP_*` constants.
4. Services raise typed exceptions only; `exception_handlers.py` maps them to HTTP codes.
5. Repositories use SQLAlchemy 2.0 `select()` with eager loading; return `None` on not-found.
6. `/api/v1/` prefix, plus `/healthz` and `/ready` health probes.
7. Config fully env-driven via `pydantic-settings`; nothing hardcoded.
8. All listed integration and unit tests pass with the in-memory async SQLite DB.

**Generate every file following these specifications, ensuring clean separation
across the presentation (routers), business (services), data-access (repositories),
and persistence (models) layers, with Pydantic v2 schemas as the validation boundary.**
