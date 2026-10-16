---
agent: 'agent'
description: 'Create or complete the AndresFit async FastAPI logic tier'
---

Create or complete the logic tier in `andresfit-tracker/backend` for the AndresFit Tracker multi-tier application.

## Required workflow

1. Read `AGENTS.md`, the applicable `.github/instructions` files, and the existing backend files before editing.
2. Preserve existing behavior and data models unless the requested change requires otherwise. Do not overwrite working files or create duplicate layers.
3. Implement the change using the API -> Service -> Repository -> Model architecture.
4. Run the backend test suite after implementation.
5. Report the files changed, tests executed, and any remaining issues.

Never create synchronous SQLAlchemy code. Use `AsyncSession`, `select()`, `update()`,
`delete()`, `sqlite+aiosqlite`, and `async def` for all I/O-bound functions.

Requirements:

1. Do not change directories; use path-qualified commands.
2. Use Python 3.12+, FastAPI, Uvicorn, Pydantic v2, and async SQLAlchemy 2.0.
3. Configure `sqlite+aiosqlite:///./andresfit.db` and the existing virtual environment and requirements files.
4. Add or preserve the following layers:
   - SQLAlchemy models in `src/models/` with `TimestampMixin` and relationships.
   - Pydantic v2 Create, Read, and Update schemas in `src/schemas/`.
   - Async repositories in `src/repositories/` using SQLAlchemy 2.0 statements.
   - Async services in `src/services/` containing business rules and typed exceptions.
   - Routers and dependency wiring in `src/api/v1/routers/` and `src/api/dependencies.py`.
   - Exception mappings in `src/api/exception_handlers.py`.
5. Add route handlers for:
   - `/api/v1/users/`
   - `/api/v1/teams/`
   - `/api/v1/activities/`
   - `/api/v1/leaderboard/`
   - `/api/v1/workouts/`
6. Include `/healthz` and `/ready` probes.
7. Keep server port on `8000` and add Codespaces-aware API URL support using `CODESPACE_NAME`.
8. Add or update unit tests with `AsyncMock` repositories and integration tests with `httpx.AsyncClient` and in-memory async SQLite.
