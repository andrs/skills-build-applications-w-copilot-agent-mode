---
mode: 'agent'
description: 'Create a production-ready FastAPI backend with best practices'
---

Create a complete, production-ready FastAPI backend for AndresFit Tracker following modern best practices.

## Requirements

### 1. Project Structure
```
andresfit-tracker/backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app with middleware
│   ├── config.py            # Settings with pydantic-settings
│   ├── database.py          # SQLAlchemy setup with pooling
│   ├── dependencies.py      # Reusable dependencies
│   ├── exceptions.py        # Custom exception handlers
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py          # Base model with timestamps
│   │   ├── user.py
│   │   ├── activity.py
│   │   ├── team.py
│   │   └── workout.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── common.py        # Paginated response, API response wrapper
│   │   ├── user.py          # UserCreate, UserRead, UserUpdate
│   │   ├── activity.py
│   │   ├── team.py
│   │   └── workout.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── users.py
│   │   ├── activities.py
│   │   ├── teams.py
│   │   ├── leaderboard.py
│   │   └── workouts.py
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── activity_service.py
│   │   └── team_service.py
│   └── utils/
│       ├── __init__.py
│       ├── logging.py
│       └── pagination.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Fixtures
│   ├── test_users.py
│   ├── test_activities.py
│   ├── test_teams.py
│   ├── test_leaderboard.py
│   └── test_workouts.py
├── alembic/                 # Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── .env.example
├── requirements.txt
└── requirements-dev.txt
```

### 2. Database Models (app/models/)

#### Base Model (models/base.py)
```python
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
```

#### All models should:
- Inherit from Base and TimestampMixin
- Use `Mapped` type hints
- Include proper indexes on foreign keys
- Have cascade delete rules defined
- Include `__repr__` for debugging

### 3. Pydantic Schemas (app/schemas/)

#### Common Schemas (schemas/common.py)
```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int
    
class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T | None = None
    message: str | None = None
    errors: dict | None = None
```

#### Schema Patterns
- Base schemas for shared fields
- Create schemas for POST requests
- Read schemas for responses (with from_attributes)
- Update schemas with optional fields
- Advanced validation with `@validator`
- Email validation with `EmailStr`
- String patterns with `Field(pattern=...)`

### 4. API Routes Structure

All routes must follow this pattern:

```python
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/v1/resource",
    tags=["resource"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/",
    response_model=PaginatedResponse[ResourceRead],
    summary="List resources",
    description="Retrieve paginated list of resources with optional filters"
)
def list_resources(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(50, ge=1, le=100, description="Items per page"),
    search: str | None = Query(None, description="Search query"),
    db: Session = Depends(get_db)
):
    # Implementation
    pass

@router.get("/{resource_id}", response_model=ResourceRead)
def get_resource(resource_id: int, db: Session = Depends(get_db)):
    # Implementation with error handling
    pass

@router.post("/", response_model=ResourceRead, status_code=status.HTTP_201_CREATED)
def create_resource(payload: ResourceCreate, db: Session = Depends(get_db)):
    # Implementation with duplicate checks
    pass

@router.patch("/{resource_id}", response_model=ResourceRead)
def update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    db: Session = Depends(get_db)
):
    # Implementation
    pass

@router.delete("/{resource_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_resource(resource_id: int, db: Session = Depends(get_db)):
    # Implementation
    pass
```

### 5. Required Endpoints

#### Users (`/api/v1/users/`)
- GET `/` - List users (paginated, searchable)
- GET `/{user_id}` - Get user details
- POST `/` - Create user (validate unique username/email)
- PATCH `/{user_id}` - Update user
- DELETE `/{user_id}` - Delete user
- GET `/{user_id}/activities` - Get user's activities

#### Activities (`/api/v1/activities/`)
- GET `/` - List activities (filter by type, user, date range)
- GET `/{activity_id}` - Get activity details
- POST `/` - Create activity
- DELETE `/{activity_id}` - Delete activity
- GET `/stats` - Activity statistics

#### Teams (`/api/v1/teams/`)
- GET `/` - List teams
- GET `/{team_id}` - Get team with members
- POST `/` - Create team
- PATCH `/{team_id}` - Update team
- DELETE `/{team_id}` - Delete team
- POST `/{team_id}/members/{user_id}` - Add member
- DELETE `/{team_id}/members/{user_id}` - Remove member

#### Leaderboard (`/api/v1/leaderboard/`)
- GET `/` - Global leaderboard (sorted by calories)
- GET `/weekly` - Weekly leaderboard
- GET `/teams` - Team leaderboard

#### Workouts (`/api/v1/workouts/`)
- GET `/` - List workouts (filter by difficulty, type)
- GET `/{workout_id}` - Get workout details
- POST `/` - Create workout
- DELETE `/{workout_id}` - Delete workout
- GET `/recommended` - Get personalized recommendations

### 6. Configuration (app/config.py)

```python
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # App
    app_name: str = "AndresFit Tracker API"
    debug: bool = False
    version: str = "1.0.0"
    
    # API
    api_v1_prefix: str = "/api/v1"
    
    # Database
    database_url: str = "sqlite:///./andresfit.db"
    db_echo: bool = False
    
    # CORS
    backend_cors_origins: list[str] = ["http://localhost:5173"]
    
    # Pagination
    default_page_size: int = 50
    max_page_size: int = 100

settings = Settings()
```

### 7. Main Application (app/main.py)

Must include:
- FastAPI instance with proper metadata
- CORS middleware
- Custom exception handlers
- Router includes
- Startup/shutdown events
- Health check endpoint
- API documentation configuration

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

app = FastAPI(
    title=settings.app_name,
    description="Fitness tracking and team management API",
    version=settings.version,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": "server_error"}
    )

# Health check
@app.get("/health", tags=["monitoring"])
async def health_check():
    return {"status": "healthy", "version": settings.version}

# Include routers
app.include_router(users.router)
app.include_router(activities.router)
app.include_router(teams.router)
app.include_router(leaderboard.router)
app.include_router(workouts.router)
```

### 8. Database Setup (app/database.py)

```python
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from app.config import settings

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=settings.db_echo
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 9. Error Handling Patterns

```python
# Custom exceptions
class ResourceNotFoundError(Exception):
    def __init__(self, resource: str, id: int):
        self.message = f"{resource} with id {id} not found"

class DuplicateResourceError(Exception):
    def __init__(self, resource: str, field: str, value: str):
        self.message = f"{resource} with {field}='{value}' already exists"

# In routes
@router.get("/{user_id}")
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "message": f"User {user_id} not found",
                "code": "USER_NOT_FOUND",
                "resource": "user",
                "id": user_id
            }
        )
    return user
```

### 10. Testing Requirements

#### conftest.py
- Test database fixture (in-memory SQLite)
- TestClient fixture
- Sample data fixtures (test_user, test_activity, etc.)
- Database session override

#### Test Coverage
Each endpoint must have tests for:
- ✅ Success case (200/201/204)
- ✅ Not found case (404)
- ✅ Validation error (422)
- ✅ Duplicate resource (400)
- ✅ Invalid input types
- ✅ Edge cases (empty lists, boundaries)

#### Parametrized Tests
Use `@pytest.mark.parametrize` for validation scenarios:
```python
@pytest.mark.parametrize("username,email,status", [
    ("valid_user", "valid@email.com", 201),
    ("ab", "valid@email.com", 422),
    ("valid_user", "invalid-email", 422),
])
def test_create_user(client, username, email, status):
    response = client.post("/api/v1/users/", json={
        "username": username,
        "email": email,
        "full_name": "Test User"
    })
    assert response.status_code == status
```

### 11. Seed Script (app/seed.py)

```python
# Must create:
# - 10+ diverse users
# - 30+ activities across different types and dates
# - 5+ teams with varied memberships
# - 15+ workouts covering all difficulty levels
# - Realistic data distribution (some users very active, some not)

# Check if data exists before seeding
if db.query(User).count() > 0:
    print("Database already seeded - skipping")
    return

print("Seeding database with test data...")
# Seed implementation
print(f"Created {user_count} users, {activity_count} activities, {team_count} teams")
```

### 12. Requirements Files

#### requirements.txt
```
fastapi>=0.115.0
uvicorn[standard]>=0.30.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
pydantic[email]>=2.0.0
python-multipart>=0.0.9
```

#### requirements-dev.txt
```
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
faker>=24.0.0
```

### 13. Documentation

Every router must include:
- OpenAPI tags
- Endpoint summaries
- Detailed descriptions
- Parameter descriptions
- Response examples
- Error response documentation

### 14. Code Quality Standards

#### Type Hints
- All functions must have return type hints
- All parameters must have type hints
- Use `|` for unions (not `Union`)
- Use `list[T]` not `List[T]`

#### Naming Conventions
- snake_case for functions, variables, modules
- PascalCase for classes
- UPPER_CASE for constants
- Descriptive names (no abbreviations)

#### Imports Organization
```python
# Standard library
import os
from datetime import datetime

# Third-party
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

# Local
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
```

## Execution Order

1. Create project structure and all __init__.py files
2. Set up configuration (config.py, .env.example)
3. Create database.py with connection pooling
4. Create base model with timestamps
5. Create all SQLAlchemy models
6. Create all Pydantic schemas
7. Create routers with full CRUD operations
8. Set up main.py with middleware and exception handlers
9. Create seed script with realistic data
10. Write comprehensive tests
11. Create requirements files
12. Verify all endpoints with automated tests

## Success Criteria

- ✅ All 26+ tests pass
- ✅ Code follows type hints standards
- ✅ No hardcoded values (use config)
- ✅ Proper error handling everywhere
- ✅ Pagination implemented correctly
- ✅ API documentation complete
- ✅ Database has realistic seed data
- ✅ All routes use dependency injection
- ✅ Response models specified for all endpoints
- ✅ Health check endpoint responds correctly

## Run Commands

```bash
# Setup
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt -r requirements-dev.txt

# Seed database
.venv/bin/python -m app.seed

# Run server
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Run tests
.venv/bin/pytest tests/ -v --cov=app

# Check types
.venv/bin/mypy app/

# Format code
.venv/bin/black app/ tests/
```
