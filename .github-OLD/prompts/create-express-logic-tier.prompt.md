---
mode: 'agent'
description: 'Create the FastAPI logic tier for the AndresFit multi-tier application'
---

Create the logic tier in `andresfit-tracker/backend` for the AndresFit Tracker multi-tier application.

Requirements:

1. Do not change directories; use path-qualified commands.
2. Initialize a Python FastAPI application with SQLAlchemy and Pydantic.
3. Configure a virtual environment and requirements.txt.
4. Add route handlers for:
   - `/api/users/`
   - `/api/teams/`
   - `/api/activities/`
   - `/api/leaderboard/`
   - `/api/workouts/`
5. Keep server port on `8000`.
6. Add Codespaces-aware API URL support using `CODESPACE_NAME`.
