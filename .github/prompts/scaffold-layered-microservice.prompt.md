---
mode: 'agent'
description: 'Scaffold a production-ready FastAPI microservice with strict layered architecture (API / Service / Repository / Model)'
---

You are a **Principal Backend Architect**. Scaffold a complete, production-ready FastAPI microservice following a strict **Layered Architecture** (API → Service → Repository → Model).

## Context

Read `.github/instructions/fastapi_layered_architecture.instructions.md` first. Every file you generate must comply with the layer rules defined there.

---

## Task

Scaffold the microservice for the domain described by the user.
If no domain is given, use **Order Management** as the default domain.

---

## Step-by-Step Execution

### STEP 1 — Scaffold Directory Structure

Create every file and directory exactly as specified in the instructions:

```
src/
├── api/
│   ├── __init__.py
│   ├── dependencies.py
│   ├── exception_handlers.py
│   └── v1/
│       ├── __init__.py
│       └── routers/
│           ├── __init__.py
│           ├── health.py
│           └── <resource>.py
├── services/
│   ├── __init__.py
│   ├── exceptions.py
│   └── <resource>_service.py
├── repositories/
│   ├── __init__.py
│   ├── base.py
│   └── <resource>_repository.py
├── models/
│   ├── __init__.py
│   ├── base.py
│   └── <resource>.py
├── schemas/
│   ├── __init__.py
│   ├── common.py
│   └── <resource>.py
├── clients/
│   ├── __init__.py
│   └── <external>_client.py
├── config.py
├── database.py
└── main.py
tests/
├── conftest.py
├── unit/
│   └── services/
│       └── test_<resource>_service.py
└── integration/
    └── api/
        └── test_<resource>.py
requirements.txt
requirements-dev.txt
.env.example
```

---

### STEP 2 — Generate Models (`src/models/`)

- Use `Base` and `TimestampMixin` from `src/models/base.py`
- Use `Mapped[]` and `mapped_column()` — SQLAlchemy 2.0 style
- Define all relationships with `back_populates`
- Add indexes on all foreign key columns
- Add `cascade="all, delete-orphan"` where appropriate

---

### STEP 3 — Generate Schemas (`src/schemas/`)

- Generate `{Resource}Create`, `{Resource}Read`, `{Resource}Update` per entity
- `Read` schemas: `model_config = ConfigDict(from_attributes=True)`
- `Update` schemas: all fields optional
- Use `Field(...)` with `gt`, `ge`, `min_length`, `max_length`, `pattern` constraints
- Use `model_validator` for computed or cross-field validation
- Generate `PaginatedResponse[T]` and `ApiResponse[T]` in `common.py`

---

### STEP 4 — Generate Repository Layer (`src/repositories/`)

- Implement `BaseRepository[ModelT]` with `get_by_id`, `list`, `delete`
- Implement resource-specific repository inheriting from `BaseRepository`
- Use ONLY `select()`, `update()`, `delete()` from SQLAlchemy 2.0
- Use `selectinload` / `joinedload` to avoid N+1 queries
- Return ORM instances or `None` — never raise exceptions
- All methods must be `async def`

---

### STEP 5 — Generate Service Layer (`src/services/`)

- Implement all business rules and domain lifecycle flows
- Import and use only repositories and external clients — never ORM models directly
- Raise typed exceptions from `src/services/exceptions.py`
- Use `model_validate()` to convert ORM → Pydantic before returning
- Coordinate transactions using `async with session.begin()` when spanning repos
- All methods must be `async def`

---

### STEP 6 — Generate External Clients (`src/clients/`)

- Use `httpx.AsyncClient` with explicit `timeout`
- Return typed `@dataclass` result objects — never raw HTTP responses
- Catch `httpx.TimeoutException` and `httpx.RequestError`
- Wrap errors as `ServiceError` subclasses

---

### STEP 7 — Generate API Layer (`src/api/`)

- Map ALL service exceptions to HTTP codes in `exception_handlers.py`
- Wire all dependencies in `dependencies.py`
- Generate full CRUD endpoints in router files:
  - `GET /` → paginated list with filters
  - `GET /{id}` → get by id
  - `POST /` → create
  - `PATCH /{id}` → partial update
  - `DELETE /{id}` → delete (204)
- Add `/healthz` (liveness) and `/ready` (readiness) endpoints
- Every endpoint must have `response_model`, `status_code`, `summary`, `description`
- Never write business logic in routers

---

### STEP 8 — Generate `main.py`, `database.py`, `config.py`

Follow exactly the patterns in the instructions:
- `main.py`: use `create_app()` factory, register exception handlers and routers
- `database.py`: async engine with pooling, `get_db()` generator with rollback on error
- `config.py`: Pydantic `BaseSettings`, env file support, typed fields

---

### STEP 9 — Generate Tests

**Unit tests** (`tests/unit/services/`):
- Mock repositories and clients with `AsyncMock`
- Test every business rule branch
- Test each custom exception is raised under the right conditions
- Use `pytest.mark.parametrize` for multiple scenarios

**Integration tests** (`tests/integration/api/`):
- Use `AsyncClient` with `ASGITransport`
- Override `get_db` with test session
- Test full request → response cycle
- Test success cases (201, 200, 204)
- Test error cases (400, 404, 409, 422)

---

### STEP 10 — Generate Supporting Files

**`requirements.txt`**:
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
asyncpg>=0.29.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pydantic[email]>=2.0.0
httpx>=0.27.0
python-multipart>=0.0.9
```

**`requirements-dev.txt`**:
```
pytest>=8.0.0
pytest-asyncio>=0.23.0
aiosqlite>=0.20.0
faker>=24.0.0
```

**`.env.example`**:
```
APP_NAME=OrderService
DEBUG=false
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/orders
DB_ECHO=false
PAYMENT_GATEWAY_URL=https://gateway.example.com
PAYMENT_GATEWAY_KEY=secret
```

---

## Validation Checklist

Before reporting done, verify:

- [ ] Every router endpoint calls ONLY the service layer
- [ ] Service layer raises ONLY typed exceptions from `services/exceptions.py`
- [ ] Repository methods return `None` for not-found instead of raising
- [ ] All exception types are mapped in `exception_handlers.py`
- [ ] All endpoints have `response_model`, `status_code`, `summary`
- [ ] All service methods accept Pydantic schemas, return Pydantic schemas
- [ ] All DB queries use SQLAlchemy 2.0 `select()` style
- [ ] All async functions are `async def`
- [ ] Config uses `pydantic_settings.BaseSettings` — no hardcoded values
- [ ] Tests: unit tests mock repositories, integration tests use real in-memory DB
- [ ] `/healthz` and `/ready` endpoints exist and work
- [ ] `model_validate()` used in services to convert ORM → Pydantic
- [ ] N+1 queries prevented with `selectinload`/`joinedload`

---

## Run Commands

```bash
# Setup
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt

# Start server
.venv/bin/uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Run all tests
.venv/bin/pytest tests/ -v --asyncio-mode=auto

# Run only unit tests
.venv/bin/pytest tests/unit/ -v --asyncio-mode=auto

# Run only integration tests
.venv/bin/pytest tests/integration/ -v --asyncio-mode=auto
```
