---
applyTo: "andresfit-tracker/backend/**"
---
# AndresFit Tracker Logic + Data Tier Guidelines

This file contains AndresFit-specific domain and runtime settings. Use
`fastapi_layered_architecture.instructions.md` for layer contracts and
`fastapi_backend_enhanced.instructions.md` for cross-cutting async patterns.
Do not duplicate or override those files' architecture rules here.

## Logic tier (Python + FastAPI)

- Use Python 3.12+ and build versioned API routes under `/api/v1/`.
- Keep API service on port `8000`.
- Use environment-aware Codespaces URLs via `CODESPACE_NAME`.
- Use `async def` route handlers and inject services with `Depends()`.

Example base URL logic:

```python
import os

codespace_name = os.environ.get("CODESPACE_NAME")
if codespace_name:
    base_url = f"https://{codespace_name}-8000.app.github.dev"
else:
    base_url = "http://localhost:8000"
```

## Data tier (SQLite + SQLAlchemy)

- Use SQLAlchemy models for users, teams, activities, leaderboard, and workouts.
- Use async SQLAlchemy 2.0 with `AsyncSession`, `select()`, and `sqlite+aiosqlite`.
- Connect to `andresfit.db` (SQLite file).
- Validate endpoints with `curl` after wiring routes.
- Use Pydantic schemas for request/response validation.
