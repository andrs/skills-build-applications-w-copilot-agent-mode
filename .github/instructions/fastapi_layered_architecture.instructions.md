---
applyTo: "andresfit-tracker/backend/**"
---
# FastAPI Layered Microservice Architecture — Copilot Instructions

## Role

You are acting as a **Principal Backend Architect and Lead Python Engineer**.
Your task is to design, scaffold, and fully implement production-ready, highly maintainable microservices using **Python 3.11+**, **FastAPI**, and a strict **Layered Microservice Architecture (API / Service / Repository / Model)**.

---

## 1. Mandatory Project Structure

Always scaffold every microservice with this exact directory layout:

```
src/
├── api/                        # Presentation layer
│   ├── __init__.py
│   ├── dependencies.py         # Dependency injection wiring
│   ├── exception_handlers.py   # Map service exceptions → HTTP codes
│   └── v1/
│       ├── __init__.py
│       └── routers/
│           ├── __init__.py
│           ├── health.py       # /healthz and /ready endpoints
│           └── <resource>.py   # One router per domain resource
│
├── services/                   # Business logic layer
│   ├── __init__.py
│   ├── exceptions.py           # Custom service exception classes
│   └── <resource>_service.py
│
├── repositories/               # Data access layer
│   ├── __init__.py
│   ├── base.py                 # Generic async repository base class
│   └── <resource>_repository.py
│
├── models/                     # SQLAlchemy ORM models
│   ├── __init__.py
│   ├── base.py                 # DeclarativeBase + TimestampMixin
│   └── <resource>.py
│
├── schemas/                    # Pydantic v2 schemas
│   ├── __init__.py
│   ├── common.py               # Paginated response, API envelope
│   └── <resource>.py           # Create / Read / Update schemas
│
├── clients/                    # External service integrations
│   ├── __init__.py
│   └── <external>_client.py
│
├── config.py                   # Pydantic Settings (env-driven)
├── database.py                 # Async SQLAlchemy engine + session
└── main.py                     # FastAPI app factory
```

---

## 2. Layer Rules — Strict Enforcement

### LAYER 1 — API / Presentation (`src/api/`)

**Responsibilities:**
- HTTP routing, API versioning under `/api/v1/`
- Request/response serialization via Pydantic schemas
- Map service-layer exceptions to HTTP status codes (never catch raw DB errors here)
- Kubernetes health probes: `GET /healthz` (liveness) and `GET /ready` (readiness)
- Inject services and DB sessions using `Depends()`

**Rules:**
- ✅ Call service layer only — NEVER call repositories or ORM models directly
- ✅ Always declare `response_model` and `status_code` on every endpoint
- ✅ Use `status.HTTP_*` constants, never bare integers
- ❌ NEVER write business logic inside routers
- ❌ NEVER import SQLAlchemy session or models inside routers

```python
# CORRECT
@router.post(
    "/",
    response_model=OrderRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new order",
)
async def create_order(
    payload: OrderCreate,
    service: OrderService = Depends(get_order_service),
) -> OrderRead:
    return await service.create_order(payload)

# WRONG — never do this in a router
async def create_order(payload: OrderCreate, db: AsyncSession = Depends(get_db)):
    order = Order(**payload.model_dump())
    db.add(order)
    await db.commit()
    return order
```

**Exception Handler pattern:**
```python
# src/api/exception_handlers.py
from fastapi import Request
from fastapi.responses import JSONResponse
from src.services.exceptions import (
    NotFoundError, PaymentFailedError, InvalidOrderError, DuplicateResourceError
)

def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": "not_found", "message": str(exc), "resource": exc.resource}
        )

    @app.exception_handler(PaymentFailedError)
    async def payment_failed_handler(request: Request, exc: PaymentFailedError):
        return JSONResponse(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            content={"error": "payment_failed", "message": str(exc), "code": exc.code}
        )

    @app.exception_handler(InvalidOrderError)
    async def invalid_order_handler(request: Request, exc: InvalidOrderError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "invalid_order", "message": str(exc)}
        )

    @app.exception_handler(DuplicateResourceError)
    async def duplicate_handler(request: Request, exc: DuplicateResourceError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": "conflict", "message": str(exc), "field": exc.field}
        )
```

**Health endpoints:**
```python
# src/api/v1/routers/health.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from src.database import get_db

router = APIRouter(tags=["health"])

@router.get("/healthz", summary="Liveness probe")
async def liveness():
    return {"status": "alive"}

@router.get("/ready", summary="Readiness probe")
async def readiness(db: AsyncSession = Depends(get_db)):
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "ok"}
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "database": str(exc)}
        )
```

---

### LAYER 2 — Service / Business Logic (`src/services/`)

**Responsibilities:**
- All business rules, domain lifecycle flows (e.g., order creation, payment, cancellation)
- Transaction coordination across multiple repository calls
- Calling external clients (e.g., payment gateway)
- Raising typed custom exceptions on failures

**Rules:**
- ✅ Accept Pydantic schemas as input, return Pydantic schemas or domain objects
- ✅ Call repositories and external clients only
- ✅ Raise custom exceptions from `src/services/exceptions.py`
- ✅ Coordinate `async with db.begin()` transactions when spanning multiple repos
- ❌ NEVER import FastAPI, `Request`, or HTTP-related objects
- ❌ NEVER directly instantiate or query ORM models — use repositories

```python
# src/services/<resource>_service.py
from src.repositories.order_repository import OrderRepository
from src.schemas.order import OrderCreate, OrderRead, OrderUpdate
from src.clients.payment_client import PaymentClient
from src.services.exceptions import NotFoundError, PaymentFailedError, InvalidOrderError

class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        payment_client: PaymentClient,
    ) -> None:
        self._order_repo = order_repo
        self._payment_client = payment_client

    async def create_order(self, payload: OrderCreate) -> OrderRead:
        # Business rule: order must have at least one item
        if not payload.items:
            raise InvalidOrderError("Order must contain at least one item")

        # Call external payment gateway
        payment_result = await self._payment_client.authorize(
            amount=payload.total_amount,
            customer_id=payload.customer_id,
        )
        if not payment_result.authorized:
            raise PaymentFailedError(
                message=payment_result.message,
                code=payment_result.error_code,
            )

        order = await self._order_repo.create(payload, payment_id=payment_result.id)
        return OrderRead.model_validate(order)

    async def cancel_order(self, order_id: int) -> OrderRead:
        order = await self._order_repo.get_by_id(order_id)
        if order is None:
            raise NotFoundError(resource="Order", id=order_id)
        if order.status not in ("pending", "confirmed"):
            raise InvalidOrderError(f"Cannot cancel order in status '{order.status}'")

        updated = await self._order_repo.update_status(order_id, "cancelled")
        return OrderRead.model_validate(updated)
```

**Custom exceptions:**
```python
# src/services/exceptions.py

class ServiceError(Exception):
    """Base class for all service-layer exceptions."""

class NotFoundError(ServiceError):
    def __init__(self, resource: str, id: int | str):
        self.resource = resource
        self.id = id
        super().__init__(f"{resource} with id '{id}' not found")

class DuplicateResourceError(ServiceError):
    def __init__(self, resource: str, field: str, value: str):
        self.resource = resource
        self.field = field
        self.value = value
        super().__init__(f"{resource} with {field}='{value}' already exists")

class InvalidOrderError(ServiceError):
    """Raised when business rules for an order are violated."""

class PaymentFailedError(ServiceError):
    def __init__(self, message: str, code: str | None = None):
        self.code = code
        super().__init__(message)

class InsufficientInventoryError(ServiceError):
    def __init__(self, product_id: int, requested: int, available: int):
        self.product_id = product_id
        super().__init__(
            f"Insufficient inventory for product {product_id}: "
            f"requested {requested}, available {available}"
        )
```

---

### LAYER 3 — Repository / Data Access (`src/repositories/`)

**Responsibilities:**
- All SQLAlchemy async queries, inserts, updates, deletes
- Paginated listing, filtering, and ordering
- NO business logic — pure data persistence and retrieval

**Rules:**
- ✅ Use `AsyncSession` exclusively
- ✅ Use `select()`, `update()`, `delete()` from `sqlalchemy` (not `session.query()`)
- ✅ Accept and return ORM model instances or primitives
- ❌ NEVER raise service-level exceptions — return `None` for not-found cases
- ❌ NEVER import FastAPI or Pydantic schemas

```python
# src/repositories/base.py
from typing import Generic, TypeVar
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession

ModelT = TypeVar("ModelT")

class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, id: int) -> ModelT | None:
        result = await self._session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        *,
        offset: int = 0,
        limit: int = 50,
        filters: list | None = None,
    ) -> tuple[list[ModelT], int]:
        base_query = select(self.model)
        if filters:
            for f in filters:
                base_query = base_query.where(f)

        total_result = await self._session.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = total_result.scalar_one()

        rows = await self._session.execute(base_query.offset(offset).limit(limit))
        return rows.scalars().all(), total

    async def delete(self, id: int) -> bool:
        result = await self._session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self._session.commit()
        return result.rowcount > 0
```

```python
# src/repositories/<resource>_repository.py
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.models.order import Order
from src.repositories.base import BaseRepository
from src.schemas.order import OrderCreate

class OrderRepository(BaseRepository[Order]):
    model = Order

    async def create(self, payload: OrderCreate, payment_id: str) -> Order:
        order = Order(
            customer_id=payload.customer_id,
            total_amount=payload.total_amount,
            payment_id=payment_id,
            status="pending",
        )
        self._session.add(order)
        await self._session.flush()
        await self._session.refresh(order)
        return order

    async def get_with_items(self, order_id: int) -> Order | None:
        result = await self._session.execute(
            select(Order)
            .options(selectinload(Order.items))
            .where(Order.id == order_id)
        )
        return result.scalar_one_or_none()

    async def update_status(self, order_id: int, status: str) -> Order | None:
        await self._session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(status=status)
        )
        await self._session.commit()
        return await self.get_by_id(order_id)
```

---

### LAYER 4 — Models (`src/models/`)

**Rules:**
- ✅ Use SQLAlchemy 2.0 `mapped_column()` and `Mapped[]` type annotations
- ✅ Include `TimestampMixin` on every model
- ✅ Define explicit `__tablename__`
- ✅ Use `ForeignKey` with `ondelete` cascade rules
- ✅ Define relationships with `back_populates`
- ❌ NEVER import Pydantic inside model files

```python
# src/models/base.py
from datetime import datetime
from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
```

```python
# src/models/<resource>.py
from sqlalchemy import String, Numeric, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from src.models.base import Base, TimestampMixin

class Order(Base, TimestampMixin):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

class OrderItem(Base, TimestampMixin):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    order_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int] = mapped_column(Integer, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)

    order: Mapped["Order"] = relationship(back_populates="items")
```

---

### LAYER 5 — Schemas (`src/schemas/`)

**Rules:**
- ✅ Use Pydantic v2 (`model_config = ConfigDict(from_attributes=True)` on Read schemas)
- ✅ Separate `Create`, `Read`, `Update` schemas per resource
- ✅ Use `Field()` with constraints: `min_length`, `max_length`, `gt`, `ge`, `pattern`
- ✅ Use `model_validator` for cross-field validation
- ❌ NEVER import SQLAlchemy inside schema files

```python
# src/schemas/common.py
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

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
```

```python
# src/schemas/<resource>.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, model_validator

class OrderItemCreate(BaseModel):
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=100)
    unit_price: float = Field(..., gt=0)

class OrderCreate(BaseModel):
    customer_id: int = Field(..., gt=0)
    items: list[OrderItemCreate] = Field(..., min_length=1)

    @model_validator(mode="after")
    def compute_total(self) -> "OrderCreate":
        self.total_amount = sum(i.unit_price * i.quantity for i in self.items)
        return self

    total_amount: float = Field(default=0.0)

class OrderItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    product_id: int
    quantity: int
    unit_price: float

class OrderRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    customer_id: int
    status: str
    total_amount: float
    payment_id: str | None
    items: list[OrderItemRead] = []
    created_at: datetime
    updated_at: datetime

class OrderUpdate(BaseModel):
    status: str | None = Field(None, pattern="^(pending|confirmed|shipped|cancelled)$")
```

---

### LAYER 6 — External Clients (`src/clients/`)

**Rules:**
- ✅ Use `httpx.AsyncClient` for all HTTP calls
- ✅ Wrap external responses in typed dataclasses or Pydantic schemas
- ✅ Handle timeouts, retries, and connection errors
- ✅ Raise `ServiceError` subclasses on unrecoverable failures
- ❌ NEVER leak raw `httpx` errors into the service layer

```python
# src/clients/<external>_client.py
from dataclasses import dataclass
import httpx
from src.config import settings
from src.services.exceptions import PaymentFailedError

@dataclass
class PaymentResult:
    authorized: bool
    id: str | None = None
    message: str | None = None
    error_code: str | None = None

class PaymentClient:
    def __init__(self) -> None:
        self._base_url = settings.payment_gateway_url
        self._api_key = settings.payment_gateway_key

    async def authorize(self, amount: float, customer_id: int) -> PaymentResult:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self._base_url}/authorize",
                    headers={"Authorization": f"Bearer {self._api_key}"},
                    json={"amount": amount, "customer_id": customer_id},
                )
            if response.status_code == 200:
                data = response.json()
                return PaymentResult(authorized=True, id=data["payment_id"])
            else:
                data = response.json()
                return PaymentResult(
                    authorized=False,
                    message=data.get("message", "Payment declined"),
                    error_code=data.get("code"),
                )
        except httpx.TimeoutException:
            raise PaymentFailedError("Payment gateway timed out", code="TIMEOUT")
        except httpx.RequestError as exc:
            raise PaymentFailedError(f"Payment gateway unreachable: {exc}", code="CONNECTION_ERROR")
```

---

## 3. Dependency Injection Wiring

```python
# src/api/dependencies.py
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.database import get_db
from src.repositories.order_repository import OrderRepository
from src.services.order_service import OrderService
from src.clients.payment_client import PaymentClient

def get_payment_client() -> PaymentClient:
    return PaymentClient()

def get_order_repository(db: AsyncSession = Depends(get_db)) -> OrderRepository:
    return OrderRepository(db)

def get_order_service(
    order_repo: OrderRepository = Depends(get_order_repository),
    payment_client: PaymentClient = Depends(get_payment_client),
) -> OrderService:
    return OrderService(order_repo, payment_client)
```

---

## 4. Async Database Setup

```python
# src/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from src.config import settings

engine = create_async_engine(
    settings.database_url,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
    echo=settings.db_echo,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
```

---

## 5. Configuration Management

```python
# src/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "Order Management Service"
    version: str = "1.0.0"
    debug: bool = False
    api_v1_prefix: str = "/api/v1"

    database_url: str = "sqlite+aiosqlite:///./andresfit.db"
    db_echo: bool = False

    payment_gateway_url: str
    payment_gateway_key: str

    default_page_size: int = 50
    max_page_size: int = 100

settings = Settings()
```

---

## 6. Application Factory

```python
# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings
from src.api.exception_handlers import add_exception_handlers
from src.api.v1.routers import health, orders

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_exception_handlers(app)

    app.include_router(health.router)
    app.include_router(orders.router, prefix=settings.api_v1_prefix)

    return app

app = create_app()
```

---

## 7. Testing Architecture

```
tests/
├── conftest.py              # pytest fixtures
├── unit/
│   ├── services/            # Unit tests for service layer (mock repositories)
│   │   └── test_order_service.py
│   └── repositories/        # Unit tests for repository queries
├── integration/
│   └── api/                 # Full API integration tests using TestClient
│       └── test_orders.py
└── fixtures/
    └── factories.py         # Test data factories
```

```python
# tests/conftest.py
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from src.main import app
from src.database import get_db
from src.models.base import Base

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def engine():
    return create_async_engine(TEST_DATABASE_URL)

@pytest.fixture(autouse=True)
async def setup_db(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db_session(engine):
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

@pytest.fixture
async def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
```

**Unit test with mocked repository:**
```python
# tests/unit/services/test_order_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from src.services.order_service import OrderService
from src.services.exceptions import InvalidOrderError, PaymentFailedError
from src.schemas.order import OrderCreate, OrderItemCreate

@pytest.fixture
def order_repo():
    return AsyncMock()

@pytest.fixture
def payment_client():
    return AsyncMock()

@pytest.fixture
def service(order_repo, payment_client):
    return OrderService(order_repo, payment_client)

async def test_create_order_raises_when_no_items(service):
    payload = OrderCreate(customer_id=1, items=[])
    with pytest.raises(InvalidOrderError, match="at least one item"):
        await service.create_order(payload)

async def test_create_order_raises_on_payment_failure(service, payment_client):
    from src.clients.payment_client import PaymentResult
    payment_client.authorize.return_value = PaymentResult(
        authorized=False, message="Declined", error_code="INSUFFICIENT_FUNDS"
    )
    payload = OrderCreate(
        customer_id=1,
        items=[OrderItemCreate(product_id=1, quantity=2, unit_price=10.0)]
    )
    with pytest.raises(PaymentFailedError):
        await service.create_order(payload)
```

---

## 8. Code Quality Rules

### Always:
- ✅ Use type hints on all function parameters and return values
- ✅ Use `async def` for all routes, services, repository methods, and clients
- ✅ Use named `status.HTTP_*` constants in routes
- ✅ Use `model_validate()` to convert ORM objects to Pydantic schemas in services
- ✅ Raise service exceptions in service layer, map them in exception handlers
- ✅ Use `selectinload` or `joinedload` to prevent N+1 queries
- ✅ Write unit tests mocking repositories, integration tests hitting real DB

### Never:
- ❌ Write DB queries inside routers
- ❌ Write HTTP code inside services or repositories
- ❌ Return raw ORM objects from routers — always go through Pydantic response_model
- ❌ Use `session.query()` — always use `select()` from SQLAlchemy 2.0 core
- ❌ Hardcode configuration values
- ❌ Catch generic `Exception` without re-raising or wrapping as typed errors
- ❌ Skip exception handlers — all service exceptions must be mapped to HTTP codes

---

## 9. Naming Conventions

| Layer | Pattern | Example |
|-------|---------|---------|
| Router file | `{resource}.py` | `orders.py` |
| Router prefix | `/{resources}` | `/orders` |
| Service class | `{Resource}Service` | `OrderService` |
| Repository class | `{Resource}Repository` | `OrderRepository` |
| Model class | `{Resource}` | `Order`, `OrderItem` |
| Schema classes | `{Resource}Create/Read/Update` | `OrderCreate` |
| Exception classes | `{Reason}Error` | `PaymentFailedError` |
| Client class | `{External}Client` | `PaymentClient` |

---

## 10. Port & Environment

- API server: `8000`
- Docs: `/api/docs` (Swagger UI) and `/api/redoc` (ReDoc)
- Health: `/healthz` (liveness), `/ready` (readiness)
- Use `CODESPACE_NAME` env var for Codespace URL awareness
- All configuration via `.env` file + Pydantic Settings
