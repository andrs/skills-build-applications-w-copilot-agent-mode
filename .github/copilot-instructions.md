# GitHub Copilot Instructions — AndresFit Tracker

This file is automatically loaded by GitHub Copilot for every chat and code completion in this repository.
It defines the project context, coding standards, and architectural rules Copilot must follow at all times.

---

## Project Overview

**AndresFit Tracker** is a multi-tier fitness tracking application built for Mergington High School.
It allows students to log workouts, compete on a leaderboard, join teams, and receive personalized workout suggestions.

### Tech Stack

| Tier | Technology |
|------|-----------|
| Presentation | React 19 + Vite + react-router-dom + Bootstrap |
| Logic / API | Python >= 3.12 · FastAPI · Uvicorn |
| Data | SQLite · Async SQLAlchemy 2.0 ORM with `sqlite+aiosqlite` |
| Validation | Pydantic v2 |
| Testing (backend) | pytest · pytest-asyncio · httpx.AsyncClient |
| Testing (frontend) | vitest |

### Ports

- `8000` — FastAPI backend API
- `5173` — React/Vite frontend dev server

### Project Root Paths

- Backend: `andresfit-tracker/backend/`
- Frontend: `andresfit-tracker/frontend/`

---

## Architecture — Mandatory Layered Structure

Every backend feature **must** follow this layer order. Never skip or merge layers.

```
HTTP Request
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│  API Layer     andresfit-tracker/backend/src/api/v1/routers/ │
│  FastAPI routers — HTTP only, no business logic        │
└──────────────────────────┬──────────────────────────────┘
                           │  Depends()
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Service Layer  andresfit-tracker/backend/src/services/ │
│  Business rules, lifecycle flows, custom exceptions    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Repository Layer  .../backend/src/repositories/        │
│  SQLAlchemy queries only — return None on not-found    │
└──────────────────────────┬──────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Model Layer   andresfit-tracker/backend/src/models/    │
│  SQLAlchemy ORM models with TimestampMixin             │
└─────────────────────────────────────────────────────────┘
```

### Layer Contracts — What Each Layer Can Import

| Layer | Can import | Cannot import |
|-------|-----------|---------------|
| **Routers** | schemas, services, `Depends` | models, repositories, SQLAlchemy |
| **Services** | schemas, repositories, exceptions | FastAPI, `Request`, SQLAlchemy models |
| **Repositories** | models, SQLAlchemy | schemas, services, FastAPI |
| **Models** | SQLAlchemy | Pydantic, FastAPI |
| **Schemas** | Pydantic | SQLAlchemy, FastAPI |

---

## Backend Rules

### Routers (`src/api/v1/routers/`)

- Prefix all resource routes with `/api/v1/`
- Always declare `response_model` and `status_code` on every endpoint
- Use `status.HTTP_*` constants — never bare integers like `404`
- Inject services with `Depends()` — never instantiate them directly
- Map service exceptions to HTTP codes via `HTTPException` or exception handlers
- Include `/healthz` endpoint in every router module

```python
# CORRECT
@router.post("/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return await service.create_user(payload)

# WRONG — never do this: routers must not access the database directly
@router.post("/users/")
async def create_user(payload: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

### Services (`src/services/`)

- Accept Pydantic schemas as input
- Return Pydantic schemas as output (use `model_validate()` to convert ORM → schema)
- Raise typed custom exceptions only — never `HTTPException`
- All methods must be `async def`

```python
# Custom exceptions always live in src/services/exceptions.py
class NotFoundError(ServiceError):
    def __init__(self, resource: str, id: int):
        self.resource = resource
        super().__init__(f"{resource} with id {id} not found")

class DuplicateResourceError(ServiceError):
    def __init__(self, resource: str, field: str, value: str):
        self.field = field
        super().__init__(f"{resource} with {field}='{value}' already exists")

class InvalidOperationError(ServiceError):
    """Raised when a business rule is violated."""
```

### Repositories (`src/repositories/`)

- Use SQLAlchemy 2.0 style: `select()`, `update()`, `delete()` — never `session.query()`
- Return `None` for not-found — never raise exceptions
- Use `selectinload()` or `joinedload()` to prevent N+1 queries
- All methods must be `async def` if using `AsyncSession`

```python
# CORRECT — SQLAlchemy 2.0 style
result = await session.execute(select(User).where(User.id == user_id))
return result.scalar_one_or_none()

# WRONG — legacy style
return session.query(User).filter(User.id == user_id).first()
```

### Models (`src/models/`)

- Use `Mapped[]` and `mapped_column()` — SQLAlchemy 2.0 typed ORM
- Every model must include `TimestampMixin` (provides `created_at`, `updated_at`)
- Define all relationships with `back_populates`
- Add `index=True` on all foreign key columns
- Add `cascade="all, delete-orphan"` on child relationships

```python
class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    activities: Mapped[list["Activity"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
```

### Schemas (`src/schemas/`)

- Always define three schema variants: `{Resource}Create`, `{Resource}Read`, `{Resource}Update`
- `Read` schemas: add `model_config = ConfigDict(from_attributes=True)`
- `Update` schemas: all fields optional (`field: type | None = None`)
- Use `Field(...)` with constraints: `gt`, `ge`, `min_length`, `max_length`, `pattern`
- Use `model_validator` for cross-field or computed field validation

```python
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime

class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=1, max_length=100)
    email: EmailStr | None = None
```

---

## HTTP Status Codes — Standard Mapping

| Scenario | Status Code |
|----------|------------|
| Resource created | `201 Created` |
| Successful deletion | `204 No Content` |
| Validation error (Pydantic) | `422 Unprocessable Entity` (automatic) |
| Duplicate resource | `409 Conflict` |
| Business rule violated | `400 Bad Request` |
| Resource not found | `404 Not Found` |
| Unauthorized | `401 Unauthorized` |
| Forbidden | `403 Forbidden` |
| Server error | `500 Internal Server Error` |

---

## API Response Patterns

### Paginated List

```python
class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

@router.get("/", response_model=PaginatedResponse[UserRead])
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    service: UserService = Depends(get_user_service),
) -> PaginatedResponse[UserRead]:
    return await service.list_users(page=page, size=size)
```

### Structured Error

```python
# Always return structured errors — never plain strings
raise HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail={
        "message": f"User {user_id} not found",
        "code": "USER_NOT_FOUND",
        "resource": "user",
        "id": user_id,
    },
)
```

---

## Testing Rules

### Backend Tests (`tests/`)

- **Unit tests**: mock repositories with `AsyncMock`, test service logic in isolation
- **Integration tests**: use `httpx.AsyncClient` with `ASGITransport` and a real in-memory async SQLite DB
- Use `pytest.mark.parametrize` for validation scenarios
- Each endpoint needs tests for: success, not-found (404), duplicate (400/409), invalid input (422)

```python
# Unit test — mock the repository
@pytest.fixture
def service(mock_repo):
    return UserService(mock_repo)

async def test_create_user_raises_on_duplicate(service, mock_repo):
    mock_repo.get_by_username.return_value = existing_user
    with pytest.raises(DuplicateResourceError):
        await service.create_user(UserCreate(username="existing", ...))

# Parametrized validation test
@pytest.mark.parametrize("username,expected", [
    ("valid_user", 201),
    ("ab", 422),        # too short
    ("x" * 51, 422),    # too long
    ("has space", 422), # invalid chars
])
async def test_create_user_username_validation(client, username, expected):
    r = await client.post("/api/v1/users/", json={"username": username, ...})
    assert r.status_code == expected
```

---

## Frontend Rules (`andresfit-tracker/frontend/`)

- Use functional components with hooks only — no class components
- All API calls go through `src/services/api.js` — never `fetch` directly in components
- Always handle loading and error states in every component
- Use `react-router-dom` `<Routes>` and `<Route>` for navigation
- Import Bootstrap classes — no inline styles
- Use `useEffect` + `useState` for data fetching

```jsx
// CORRECT — loading + error states
function Users() {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    api.getUsers()
      .then(setUsers)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <p>Loading...</p>
  if (error) return <div className="alert alert-danger">{error}</div>
  ...
}
```

### API Service Pattern

```javascript
// src/services/api.js — all API calls here
async function request(path, options = {}) {
  const res = await fetch(`/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `Request failed: ${res.status}`)
  }
  if (res.status === 204) return null
  return res.json()
}
```

---

## Configuration & Environment

- All configuration via `pydantic_settings.BaseSettings` — no hardcoded values
- Use `.env` file — provide `.env.example` with all required keys
- Never commit `.env` to git

```python
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")
    database_url: str = "sqlite+aiosqlite:///./andresfit.db"
    debug: bool = False
    api_prefix: str = "/api/v1"

settings = Settings()
```

---

## Code Quality Standards

### Always

- Type hints on every function parameter and return value
- `async def` for all route handlers, service methods, repository methods
- Named exception classes — no bare `Exception` catches without re-raising
- Docstrings only when the **why** is non-obvious
- `model_validate()` to convert ORM objects to Pydantic schemas
- Eager loading (`selectinload`) to avoid N+1 DB queries
- `pool_pre_ping=True` on SQLAlchemy engine

### Never

- Business logic inside router functions
- SQLAlchemy queries inside router functions
- `session.query()` legacy style — use `select()` from SQLAlchemy 2.0
- Hardcoded port numbers, passwords, or URLs
- `from module import *`
- Bare `print()` for logging — use `logging.getLogger(__name__)`
- Empty `except` blocks
- Synchronous blocking I/O inside `async def` functions

---

## Naming Conventions

| Component | Convention | Example |
|-----------|-----------|---------|
| Router file | `{resource}.py` | `users.py` |
| URL prefix | `/api/v1/{resources}` | `/api/v1/users` |
| Service class | `{Resource}Service` | `UserService` |
| Repository class | `{Resource}Repository` | `UserRepository` |
| ORM model | `{Resource}` (PascalCase) | `User`, `Activity` |
| Pydantic schema | `{Resource}{Action}` | `UserCreate`, `UserRead` |
| Exception class | `{Reason}Error` | `NotFoundError`, `PaymentFailedError` |
| React component | `{Feature}.jsx` (PascalCase) | `Users.jsx`, `Leaderboard.jsx` |
| API service fn | `{verb}{Resource}` | `getUsers`, `createActivity` |

---

## Database Domain — AndresFit Tracker

### Entities & Relationships

```
User ──< Activity     (one-to-many)
User >──< Team        (many-to-many via team_members)
Workout               (standalone suggestions)
```

### Core Resources

| Resource | Endpoint | Operations |
|----------|---------|-----------|
| Users | `/api/v1/users/` | CRUD |
| Activities | `/api/v1/activities/` | CRUD, filter by type/user |
| Teams | `/api/v1/teams/` | CRUD, manage members |
| Leaderboard | `/api/v1/leaderboard/` | Read (sorted by calories) |
| Workouts | `/api/v1/workouts/` | CRUD, filter by difficulty/type |

### Activity Types
`running` · `walking` · `strength`

### Workout Difficulty Levels
`beginner` · `intermediate` · `advanced`

---

## Run Commands Reference

```bash
# Backend — setup
python3 -m venv andresfit-tracker/backend/.venv
andresfit-tracker/backend/.venv/bin/pip install -r andresfit-tracker/backend/requirements.txt

# Backend — seed database
cd andresfit-tracker/backend && .venv/bin/python -m src.seed

# Backend — start server
cd andresfit-tracker/backend && .venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Backend — run tests
cd andresfit-tracker/backend && .venv/bin/python -m pytest tests/ -v

# Frontend — setup
npm install --prefix andresfit-tracker/frontend

# Frontend — start dev server
npm run dev --prefix andresfit-tracker/frontend

# Frontend — build
npm run build --prefix andresfit-tracker/frontend
```

---

## Health Endpoints

Every service must expose:

| Endpoint | Type | Purpose |
|----------|------|---------|
| `GET /healthz` | Liveness | Is the process alive? |
| `GET /ready` | Readiness | Is the DB connection healthy? |

```python
from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_db

router = APIRouter(tags=["health"])


@router.get("/healthz", summary="Liveness probe")
async def liveness():
    return {"status": "alive"}


@router.get("/ready", summary="Readiness probe")
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception as exc:  # noqa: BLE001
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "database": str(exc)},
        )
```

---

## Copilot Behavior Guidelines

When generating code in this repository, Copilot must:

1. **Identify the layer** of the file being edited and apply its rules
2. **Refuse to mix layers** — no DB queries in routers, no HTTP objects in services
3. **Generate complete functions** — not placeholders with `pass` or `TODO`
4. **Always add response_model and status_code** to every FastAPI route
5. **Always use `Field()`** with constraints on Pydantic schema attributes
6. **Always add loading/error state** to React data-fetching components
7. **Suggest tests** whenever a new service method or endpoint is created
8. **Prefer async** — use `async def` wherever I/O is involved
9. **Follow existing patterns** in the codebase before introducing new ones
10. **Keep responses concise** — one clear implementation, not multiple alternatives
