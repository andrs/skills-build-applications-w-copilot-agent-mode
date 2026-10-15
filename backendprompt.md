# Backend Generation Prompt for GitHub Copilot

Generate a complete FastAPI backend for the **AndresFit Tracker** application with the following specifications:

## Tech Stack
- **Framework**: FastAPI
- **Server**: Uvicorn (ASGI)
- **Database**: SQLite
- **ORM**: SQLAlchemy 2.0+
- **Validation**: Pydantic v2
- **Testing**: pytest with TestClient

## Project Structure
```
andresfit-tracker/backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with CORS
│   ├── database.py          # SQLAlchemy session and Base
│   ├── models.py            # SQLAlchemy ORM models
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── seed.py              # Database seed script
│   └── routers/
│       ├── __init__.py
│       ├── users.py
│       ├── activities.py
│       ├── teams.py
│       ├── leaderboard.py
│       └── workouts.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # pytest fixtures
│   └── test_api.py          # API endpoint tests
└── requirements.txt
```

## Database Models (SQLAlchemy)

### 1. User Model
- `id`: Integer, primary key
- `username`: String(50), unique, not null
- `email`: String(120), unique, not null
- `full_name`: String(100), not null
- Relationships: activities (one-to-many), teams (many-to-many)

### 2. Activity Model
- `id`: Integer, primary key
- `user_id`: Integer, foreign key to User
- `activity_type`: String(50), not null (running, walking, strength)
- `duration_minutes`: Integer, not null
- `calories_burned`: Float, not null
- `date`: DateTime, default=utcnow
- Relationship: user (many-to-one)

### 3. Team Model
- `id`: Integer, primary key
- `name`: String(100), unique, not null
- `description`: String(255), nullable
- Relationship: members (many-to-many with User)

### 4. Workout Model
- `id`: Integer, primary key
- `name`: String(100), not null
- `description`: String(255), nullable
- `activity_type`: String(50), not null
- `duration_minutes`: Integer, not null
- `difficulty`: String(20), not null (beginner, intermediate, advanced)

### 5. Association Table
- `team_members`: Many-to-many relationship between Team and User

## Pydantic Schemas

### User Schemas
- `UserBase`: username, email, full_name (with Field validation)
- `UserCreate`: inherits UserBase
- `UserRead`: inherits UserBase + id (with from_attributes=True)

### Activity Schemas
- `ActivityBase`: activity_type, duration_minutes (>0), calories_burned (>0)
- `ActivityCreate`: inherits ActivityBase + user_id
- `ActivityRead`: inherits ActivityBase + id, user_id, date

### Team Schemas
- `TeamBase`: name, description (optional)
- `TeamCreate`: inherits TeamBase + member_ids (list[int])
- `TeamRead`: inherits TeamBase + id, members (list[UserRead])

### Workout Schemas
- `WorkoutBase`: name, description, activity_type, duration_minutes, difficulty (with regex pattern)
- `WorkoutCreate`: inherits WorkoutBase
- `WorkoutRead`: inherits WorkoutBase + id

### Leaderboard Schema
- `LeaderboardEntry`: user (UserRead), total_duration, total_calories, activity_count

## API Endpoints

### Users Router (`/api/users/`)
- `GET /api/users/` → List all users
- `GET /api/users/{user_id}` → Get user by ID (404 if not found)
- `POST /api/users/` → Create user (400 if duplicate username/email, 422 for validation)
- `DELETE /api/users/{user_id}` → Delete user (204 on success, 404 if not found)

### Activities Router (`/api/activities/`)
- `GET /api/activities/` → List all activities
- `GET /api/activities/{activity_id}` → Get activity by ID
- `POST /api/activities/` → Create activity (404 if user not found)
- `DELETE /api/activities/{activity_id}` → Delete activity

### Teams Router (`/api/teams/`)
- `GET /api/teams/` → List all teams with members
- `GET /api/teams/{team_id}` → Get team by ID with members
- `POST /api/teams/` → Create team (400 if duplicate name, 404 if member not found)
- `DELETE /api/teams/{team_id}` → Delete team

### Leaderboard Router (`/api/leaderboard/`)
- `GET /api/leaderboard/` → Get ranked list ordered by total_calories descending
  - Use SQLAlchemy aggregate functions: SUM(duration_minutes), SUM(calories_burned), COUNT(activities)
  - Left join to include users with no activities (showing 0 values)

### Workouts Router (`/api/workouts/`)
- `GET /api/workouts/` → List workouts with optional query params:
  - `?difficulty=beginner|intermediate|advanced`
  - `?activity_type=running|walking|strength`
- `GET /api/workouts/{workout_id}` → Get workout by ID
- `POST /api/workouts/` → Create workout
- `DELETE /api/workouts/{workout_id}` → Delete workout

## Main Application (`app/main.py`)
- Create FastAPI app instance
- Add CORS middleware with allow_origins=["*"]
- Include all routers
- Create database tables on startup
- Root endpoint returns: `{"message": "Welcome to AndresFit Tracker API"}`

## Database Configuration (`app/database.py`)
- SQLite connection string: `sqlite:///./andresfit.db`
- Create engine with `connect_args={"check_same_thread": False}`
- SessionLocal with autocommit=False, autoflush=False
- Dependency function `get_db()` with try/finally to close session
- DeclarativeBase class for models

## Seed Script (`app/seed.py`)
Create realistic sample data:
- **5 users**: paul_octo, jessica_cat, alex_run, maria_fit, john_lift (Mergington High School theme)
- **8 activities**: Mix of running, walking, strength with varying durations and calories
- **3 teams**: Alpha Runners, Beta Lifters, Gamma Walkers (with member assignments)
- **5 workouts**: Various difficulty levels and activity types
- Skip seeding if users already exist
- Print "Database seeded successfully with test data."

## Testing Requirements (`tests/test_api.py`)

Write pytest tests covering:

### User Tests (8 tests)
- Create user successfully (201)
- Duplicate username returns 400
- Invalid payload returns 422
- List users
- Get user by ID
- Get non-existent user returns 404
- Delete user returns 204
- Deleted user returns 404

### Activity Tests (5 tests)
- Create activity (201)
- Create with invalid user_id returns 404
- Invalid duration returns 422
- List activities
- Delete activity

### Team Tests (6 tests)
- Create team with members (201)
- Duplicate team name returns 400
- Invalid member_id returns 404
- List teams
- Get team by ID
- Delete team

### Leaderboard Tests (2 tests)
- Empty leaderboard returns []
- Leaderboard ordered by total_calories descending

### Workout Tests (5 tests)
- Create workout (201)
- Invalid difficulty returns 422
- Filter by difficulty
- Filter by activity_type
- Delete workout

### Test Configuration (`tests/conftest.py`)
- Use in-memory SQLite: `sqlite:///./test.db`
- Override `get_db` dependency
- Fixture to create/drop tables before/after each test
- TestClient fixture

## Requirements (`requirements.txt`)
```
fastapi>=0.115.0
uvicorn>=0.30.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pytest>=8.0.0
httpx>=0.27.0
```

## Error Handling
- Use FastAPI's HTTPException for errors
- 400: Bad Request (duplicates, business logic violations)
- 404: Not Found (resource doesn't exist)
- 422: Validation Error (Pydantic validation, automatic)
- 204: No Content (successful deletion)
- 201: Created (successful resource creation)

## Additional Requirements
- All routers use `Depends(get_db)` for database sessions
- Use proper response_model for all endpoints
- Use status_code parameter where appropriate (201, 204)
- Database session management in try/finally blocks
- Aggregate queries use func.coalesce() for null handling
- All string fields have max_length constraints
- Numeric fields validated with gt (greater than) where needed

## Run Commands
```bash
# Setup
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt

# Seed database
.venv/bin/python -m app.seed

# Start server
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
.venv/bin/pytest tests/ -v
```

---

**Generate all files following these specifications, ensuring clean separation between data tier (SQLAlchemy models), logic tier (FastAPI routers), and validation layer (Pydantic schemas).**
