---
applyTo: "andresfit-tracker/backend/**"
---
# FastAPI Backend - Enhanced Best Practices

## 🎯 Core Principles

### API Design
- All routes under `/api/v1/` prefix for versioning
- Use plural nouns for resources: `/api/v1/users/`, `/api/v1/activities/`
- RESTful conventions: GET (list/read), POST (create), PUT/PATCH (update), DELETE
- Always return appropriate HTTP status codes (200, 201, 204, 400, 404, 422, 500)

### Response Models & Status Codes
```python
# Always specify response_model and status_code
@router.post("/api/v1/users/", response_model=UserRead, status_code=201)
@router.get("/api/v1/users/", response_model=list[UserRead])
@router.delete("/api/v1/users/{user_id}", status_code=204)
```

## 🔧 Code Organization

### Router Structure
```python
# Each router should have clear imports
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)
```

### Dependency Injection Pattern
```python
# Always use Depends() for database sessions
def get_current_user(
    user_id: int,
    db: Session = Depends(get_db)
) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return user

# Use in routes
@router.get("/{user_id}")
def get_user(user: User = Depends(get_current_user)):
    return user
```

## 📝 Pydantic Schemas - Advanced Patterns

### Field Validation
```python
from pydantic import BaseModel, Field, EmailStr, validator, ConfigDict

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=100)
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum() or '_' in v or '-' in v, 'must be alphanumeric with _ or -'
        return v.lower()

class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime
    updated_at: datetime | None = None
```

### Nested Models
```python
class TeamRead(BaseModel):
    id: int
    name: str
    members: list[UserRead] = []
    created_at: datetime
```

## 🗃️ SQLAlchemy Best Practices

### Model Timestamps
```python
from datetime import datetime
from sqlalchemy import DateTime, func

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True
    )
```

### Efficient Queries
```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import selectinload

def get_teams_with_members(db: Session):
    return db.query(Team).options(
        selectinload(Team.members)
    ).all()
```

## 🛡️ Error Handling

### Custom Exception Handler
```python
# In main.py
from fastapi import Request
from fastapi.responses import JSONResponse

class DatabaseError(Exception):
    def __init__(self, message: str):
        self.message = message

@app.exception_handler(DatabaseError)
async def database_exception_handler(request: Request, exc: DatabaseError):
    return JSONResponse(
        status_code=500,
        content={"detail": exc.message, "type": "database_error"}
    )
```

### Validation Error Responses
```python
# Always provide clear error messages
if db.query(User).filter(User.username == username).first():
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail={
            "field": "username",
            "message": f"Username '{username}' already exists",
            "code": "DUPLICATE_USERNAME"
        }
    )
```

## 🔄 Async Patterns (Optional but Recommended)

### Async Database Operations
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine

@router.get("/users/")
async def list_users(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User))
    return result.scalars().all()
```

## 📊 Pagination

### Standard Pagination Pattern
```python
from typing import Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
    pages: int

@router.get("/users/", response_model=PaginatedResponse[UserRead])
def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    total = db.query(func.count(User.id)).scalar()
    users = db.query(User).offset((page - 1) * size).limit(size).all()
    
    return PaginatedResponse(
        items=users,
        total=total,
        page=page,
        size=size,
        pages=(total + size - 1) // size
    )
```

## 🔍 Query Filters & Sorting

### Standard Filter Pattern
```python
from typing import Optional

@router.get("/activities/")
def list_activities(
    activity_type: Optional[str] = Query(None),
    min_duration: Optional[int] = Query(None, ge=0),
    user_id: Optional[int] = Query(None),
    sort_by: str = Query("date", regex="^(date|duration|calories)$"),
    order: str = Query("desc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(Activity)
    
    if activity_type:
        query = query.filter(Activity.activity_type == activity_type)
    if min_duration:
        query = query.filter(Activity.duration_minutes >= min_duration)
    if user_id:
        query = query.filter(Activity.user_id == user_id)
    
    # Sorting
    order_column = getattr(Activity, sort_by)
    query = query.order_by(order_column.desc() if order == "desc" else order_column.asc())
    
    return query.all()
```

## 🔐 Security Patterns

### Input Sanitization
```python
from pydantic import validator
import bleach

class CommentCreate(BaseModel):
    text: str
    
    @validator('text')
    def sanitize_text(cls, v):
        return bleach.clean(v, tags=[], strip=True)
```

### Rate Limiting (using slowapi)
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@router.post("/users/")
@limiter.limit("5/minute")
async def create_user(request: Request, payload: UserCreate):
    pass
```

## 📈 Health & Monitoring

### Health Check Endpoint
```python
from sqlalchemy import text

@app.get("/health", tags=["monitoring"])
async def health_check(db: Session = Depends(get_db)):
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    return {
        "status": "healthy" if db_status == "healthy" else "degraded",
        "database": db_status,
        "version": "1.0.0"
    }
```

### Logging
```python
import logging

logger = logging.getLogger(__name__)

@router.post("/users/")
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating user: {payload.username}")
    try:
        user = User(**payload.model_dump())
        db.add(user)
        db.commit()
        logger.info(f"User created successfully: {user.id}")
        return user
    except Exception as e:
        logger.error(f"Failed to create user: {str(e)}")
        raise
```

## 🧪 Testing Patterns

### Fixture Pattern
```python
# In conftest.py
@pytest.fixture
def test_user(client, db):
    user = User(username="testuser", email="test@example.com", full_name="Test User")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# In tests
def test_get_user(client, test_user):
    response = client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
```

### Parametrized Tests
```python
@pytest.mark.parametrize("username,email,expected_status", [
    ("validuser", "valid@email.com", 201),
    ("ab", "valid@email.com", 422),  # Too short
    ("validuser", "invalid-email", 422),  # Invalid email
])
def test_create_user_validation(client, username, email, expected_status):
    response = client.post("/api/v1/users/", json={
        "username": username,
        "email": email,
        "full_name": "Test User"
    })
    assert response.status_code == expected_status
```

## 🚀 Performance Optimization

### Database Connection Pooling
```python
# In database.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### Response Caching Headers
```python
from fastapi import Response

@router.get("/workouts/{workout_id}")
def get_workout(workout_id: int, response: Response, db: Session = Depends(get_db)):
    workout = db.query(Workout).filter(Workout.id == workout_id).first()
    if not workout:
        raise HTTPException(status_code=404, detail="Workout not found")
    
    response.headers["Cache-Control"] = "public, max-age=3600"
    return workout
```

## 📚 API Documentation

### Enhanced OpenAPI Docs
```python
# In main.py
app = FastAPI(
    title="AndresFit Tracker API",
    description="Fitness tracking and team management API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=[
        {"name": "users", "description": "User management operations"},
        {"name": "activities", "description": "Activity tracking"},
        {"name": "teams", "description": "Team management"},
        {"name": "leaderboard", "description": "Competition rankings"},
        {"name": "workouts", "description": "Workout suggestions"},
    ]
)
```

### Endpoint Documentation
```python
@router.post(
    "/users/",
    response_model=UserRead,
    status_code=201,
    summary="Create a new user",
    description="Creates a new user account with unique username and email",
    responses={
        201: {"description": "User created successfully"},
        400: {"description": "Username or email already exists"},
        422: {"description": "Validation error"}
    }
)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """
    Create a new user with the following information:
    
    - **username**: Unique username (3-50 chars, alphanumeric with _ or -)
    - **email**: Valid email address
    - **full_name**: User's full name (1-100 chars)
    """
    pass
```

## 🎨 Response Formatting

### Consistent Response Structure
```python
class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T | None = None
    message: str | None = None
    errors: dict | None = None

@router.post("/users/", response_model=ApiResponse[UserRead])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return ApiResponse(
        success=True,
        data=user,
        message="User created successfully"
    )
```

## 🔄 Background Tasks

### Task Processing Pattern
```python
from fastapi import BackgroundTasks

def send_welcome_email(email: str):
    # Simulate email sending
    logger.info(f"Sending welcome email to {email}")

@router.post("/users/")
def create_user(
    payload: UserCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    user = User(**payload.model_dump())
    db.add(user)
    db.commit()
    
    background_tasks.add_task(send_welcome_email, user.email)
    
    return user
```

## ⚙️ Configuration Management

### Settings with Pydantic
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AndresFit Tracker"
    database_url: str = "sqlite:///./andresfit.db"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
```

## 📝 Code Quality Rules

### Always Include:
- ✅ Type hints on all functions
- ✅ Docstrings for complex logic
- ✅ Error handling with specific exceptions
- ✅ Input validation with Pydantic
- ✅ Database session cleanup (try/finally or Depends)
- ✅ Logging for important operations
- ✅ Tests for each endpoint

### Never Do:
- ❌ Hardcode configuration values
- ❌ Return raw SQLAlchemy models (always use Pydantic)
- ❌ Use `SELECT *` without explicit fields
- ❌ Ignore error cases
- ❌ Skip input validation
- ❌ Store sensitive data in logs
- ❌ Use synchronous blocking operations in async routes

## 🌐 CORS Configuration

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🔧 Port Configuration

- API Server: `8000`
- Use Codespace-aware URLs when `CODESPACE_NAME` is set
- Health check accessible at `/health` (no auth required)
