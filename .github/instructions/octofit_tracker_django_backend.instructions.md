---
applyTo: "andresfit-tracker/backend/**"
---
# AndresFit Tracker Logic + Data Tier Guidelines

## Logic tier (Python + FastAPI)

- Build API routes under `/api/`.
- Keep API service on port `8000`.
- Use environment-aware Codespaces URLs via `CODESPACE_NAME`.

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
- Connect to `andresfit.db` (SQLite file).
- Validate endpoints with `curl` after wiring routes.
- Use Pydantic schemas for request/response validation.
