# AGENTS.md

## Project Overview

This repository hosts the **AndresFit Tracker** fitness application. The active
codebase is the backend logic tier at [andresfit-tracker/backend](andresfit-tracker/backend),
a FastAPI microservice built on a strict layered architecture (API → Service →
Repository → Model) with async SQLAlchemy 2.0 and Pydantic v2.

Domain resources: users, activities, teams, leaderboard, and workouts.

## Structure

```
andresfit-tracker/backend/
├── src/
│   ├── main.py              # App factory (create_app) + lifespan table creation
│   ├── config.py            # Pydantic Settings (CODESPACE_NAME aware)
│   ├── database.py          # Async engine + get_db session dependency
│   ├── seed.py              # Async sample-data seeder
│   ├── api/                 # Presentation layer
│   │   ├── dependencies.py  # DI wiring (service ← repository ← session)
│   │   ├── exception_handlers.py  # ServiceError → HTTP status mapping
│   │   └── v1/routers/      # health, users, activities, teams, leaderboard, workouts
│   ├── services/            # Business logic + typed exceptions
│   ├── repositories/        # Async data access (select/delete, no business logic)
│   ├── models/             # SQLAlchemy ORM models + TimestampMixin
│   └── schemas/            # Pydantic Create/Read/Update schemas
├── tests/                   # pytest-asyncio (integration + unit)
├── requirements.txt
└── pytest.ini               # asyncio_mode=auto, pythonpath=.
```

## Setup

```powershell
cd andresfit-tracker/backend
python -m venv .venv                                 # requires Python >= 3.12
./.venv/Scripts/python.exe -m pip install -r requirements.txt
```

## Running

```powershell
# From andresfit-tracker/backend with the venv active
python -m src.seed                                   # seed sample data
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

- API prefix: `/api/v1/`
- Swagger UI: `/docs`  ·  ReDoc: `/redoc`
- Health probes: `/healthz` (liveness), `/ready` (readiness)
- Base URL is environment-aware via `settings.base_url` (`src/config.py`): it returns
  the Codespaces URL on port 8000 when `CODESPACE_NAME` is set, otherwise
  `http://localhost:8000`.
  
## Testing
- Unit tests under `tests/unit/` mock repositories with `AsyncMock`; integration
  tests under `tests/` use an in-memory SQLite DB (`sqlite+aiosqlite:///:memory:`)
  via the `client` fixture in `tests/conftest.py`.

```powershell
# From andresfit-tracker/backend
./.venv/Scripts/python.exe -m pytest tests -v
```

## Conventions

- Follow PEP 8; 4-space indentation.
- Keep the layer boundaries strict: routers call services only; services call
  repositories only; repositories hold no business logic.  
- Use `async def` for routes, services, repository methods.
- Raise typed exceptions from `src/services/exceptions.py` and map them in
  `src/api/exception_handlers.py` (e.g. duplicates → 409, missing → 404).
- Use `model_validate()` to convert ORM objects to Pydantic schemas.
- Drive configuration through `src/config.py` / `.env`, never hardcode values.
- services call repositories (and `clients/` for external integrations, not yet used).

## Instructions for Copilot

- Implement changes directly rather than only suggesting them.
- Keep code simple and avoid over-engineering.
- Only add comments when they clarify non-obvious logic.
- Do not create documentation files unless explicitly requested.
- Respect the instruction files under `.github/instructions/` that match the path being edited.

