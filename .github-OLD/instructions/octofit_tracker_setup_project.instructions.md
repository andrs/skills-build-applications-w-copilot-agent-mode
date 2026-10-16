---
applyTo: "**"
---
# AndresFit Tracker Multi-tier Application Setup Guidelines

## Application goals

Build an AndresFit Tracker **multi-tier application** with:

- User profiles
- Activity logging and tracking
- Team creation and management
- Competitive leaderboard
- Personalized workout suggestions

## Command execution rules

- Never change directories in commands.
- Always reference target paths directly.

## Forwarded ports

- 8000: public (logic/API tier — FastAPI)
- 5173: public (presentation tier — React/Vite)

Do not propose any other ports to forward or make public.

## Project structure

```text
andresfit-tracker/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── routers/
│   │   │   ├── __init__.py
│   │   │   ├── users.py
│   │   │   ├── activities.py
│   │   │   ├── teams.py
│   │   │   ├── leaderboard.py
│   │   │   └── workouts.py
│   │   └── seed.py
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_api.py
│   └── requirements.txt
└── frontend/
    ├── src/
    └── package.json
```

## Stack requirements

### Presentation tier

- React 19 with Vite
- react-router-dom for navigation
- bootstrap for styling

### Logic tier

- Python 3.11+
- FastAPI
- Uvicorn (ASGI server)
- Pydantic for request/response validation

### Data tier

- SQLite (file-based, zero configuration)
- SQLAlchemy ORM for data access
