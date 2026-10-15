<div align="center">

# 🏋️ AndresFit Tracker

**A production-ready, multi-tier fitness tracking application built with GitHub Copilot Agent Mode**

[![Python](https://img.shields.io/badge/Python-3.11%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8-646CFF?style=for-the-badge&logo=vite&logoColor=white)](https://vite.dev/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![Pydantic](https://img.shields.io/badge/Pydantic-v2-E92063?style=for-the-badge&logo=pydantic&logoColor=white)](https://docs.pydantic.dev/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![pytest](https://img.shields.io/badge/pytest-8.0%2B-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

*Log workouts · Compete on leaderboards · Train with teams · Get personalized suggestions*

</div>

---

## 🎯 What Is This?

**AndresFit Tracker** is a full-stack fitness application originally inspired by a GitHub Skills exercise and evolved into a **production-quality, layered microservice** demonstrating modern Python and React best practices.

Students and developers can:
- 📊 Log and track fitness activities (running, walking, strength training)
- 🏆 Compete on a real-time calorie-based leaderboard
- 👥 Create and manage teams for group challenges
- 💡 Discover personalized workout suggestions by difficulty and type
- 👤 Manage user profiles with full CRUD support

> 💡 **Tip:** This project also serves as a **GitHub Copilot Agent Mode showcase** — every file includes custom Copilot instructions that guided AI-assisted development through a strict layered architecture.

---

## ✨ Key Features

### 🔙 Backend
- 🏗️ **Strict 4-layer architecture** — Router → Service → Repository → Model (no layer mixing)
- ⚡ **FastAPI** with automatic OpenAPI docs at `/api/docs`
- 🗃️ **SQLAlchemy 2.0** ORM with `Mapped[]` typed models and `TimestampMixin`
- ✅ **Pydantic v2** schemas with `Field()` constraints on every attribute
- 🛡️ **Typed custom exceptions** (`NotFoundError`, `DuplicateResourceError`) mapped to HTTP codes via global handlers
- 🩺 **Health probes** at `GET /health` (liveness) and `GET /ready` (readiness)
- 🔄 **Dependency injection** wired through `app/dependencies.py`
- 🌱 **Seed script** with realistic dummy data (5 users, 8 activities, 3 teams, 5 workouts)

### 🖥️ Frontend
- ⚛️ **React 19** with functional components and hooks
- 🗺️ **react-router-dom** for client-side routing
- 🎨 **Bootstrap 5** for responsive, mobile-friendly UI
- 🔌 **Centralized API service** (`src/services/api.js`) — all fetch calls in one place
- ⏳ **Loading & error states** on every data-fetching component
- 🔀 **Vite proxy** transparently forwards `/api/*` to the backend

### 🧪 Testing
- **52 tests** — all passing
- **Integration tests** (`test_api.py`) — full HTTP request → service → DB → response cycle
- **Unit tests** (`test_services.py`) — service layer tested with mocked repositories
- 📐 Parametrized validation tests with `pytest.mark.parametrize`

---

## 🏗️ Architecture Overview

### Multi-Tier Application

```
┌─────────────────────────────────────────────────────────────┐
│                    PRESENTATION TIER                         │
│                                                             │
│   Browser ──► React 19 + Vite (port 5173)                  │
│               react-router-dom · Bootstrap 5               │
│               src/services/api.js (fetch wrapper)          │
└───────────────────────────┬─────────────────────────────────┘
                            │  HTTP /api/*  (Vite proxy)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      LOGIC TIER                              │
│                                                             │
│   FastAPI + Uvicorn (port 8000)                            │
│                                                             │
│  ┌─────────────┐   ┌─────────────┐   ┌──────────────────┐ │
│  │   Routers   │──►│  Services   │──►│  Repositories    │ │
│  │  app/routers│   │ app/services│   │ app/repositories │ │
│  │             │   │             │   │                  │ │
│  │ HTTP only   │   │ Business    │   │ SQLAlchemy 2.0   │ │
│  │ Depends()   │   │ logic +     │   │ select() queries │ │
│  │ response_   │   │ typed       │   │ Returns None on  │ │
│  │ model       │   │ exceptions  │   │ not-found        │ │
│  └─────────────┘   └─────────────┘   └──────────────────┘ │
│         │                                      │            │
│  exception_handlers.py                         │            │
│  ServiceError → HTTP status                    │            │
│  dependencies.py (DI wiring)                   │            │
└────────────────────────────────────────────────┼────────────┘
                                                 │ ORM queries
                                                 ▼
┌─────────────────────────────────────────────────────────────┐
│                       DATA TIER                              │
│                                                             │
│   SQLite · andresfit.db                                     │
│   SQLAlchemy Models with TimestampMixin                     │
│                                                             │
│   ┌────────┐  ┌──────────┐  ┌────────┐  ┌─────────┐       │
│   │  User  │  │ Activity │  │  Team  │  │ Workout │       │
│   └────────┘  └──────────┘  └────────┘  └─────────┘       │
│       │            │             │                          │
│       └────────────┘             │                          │
│        (one-to-many)             │                          │
│       └──────────────────────────┘                          │
│          (many-to-many via team_members)                     │
└─────────────────────────────────────────────────────────────┘
```

### Layer Import Rules

| Layer | Can Import | Cannot Import |
|-------|-----------|---------------|
| **Routers** | `schemas`, `services`, `Depends` | `models`, `repositories`, SQLAlchemy |
| **Services** | `schemas`, `repositories`, `exceptions` | FastAPI, `Request`, ORM models |
| **Repositories** | `models`, SQLAlchemy | `schemas`, `services`, FastAPI |
| **Models** | SQLAlchemy | Pydantic, FastAPI |
| **Schemas** | Pydantic | SQLAlchemy, FastAPI |

### API Endpoints

| Method | Endpoint | Description | Status |
|--------|----------|-------------|--------|
| `GET` | `/health` | Liveness probe | `200` |
| `GET` | `/ready` | Readiness probe (DB check) | `200 / 503` |
| `GET` | `/api/docs` | Interactive OpenAPI UI | — |
| `GET/POST` | `/api/users/` | List / Create users | `200 / 201` |
| `GET/DELETE` | `/api/users/{id}` | Get / Delete user | `200 / 204` |
| `GET/POST` | `/api/activities/` | List / Log activity | `200 / 201` |
| `GET/DELETE` | `/api/activities/{id}` | Get / Delete activity | `200 / 204` |
| `GET/POST` | `/api/teams/` | List / Create team | `200 / 201` |
| `GET/DELETE` | `/api/teams/{id}` | Get / Delete team | `200 / 204` |
| `GET` | `/api/leaderboard/` | Ranked by total calories | `200` |
| `GET/POST` | `/api/workouts/` | List (filterable) / Create | `200 / 201` |
| `GET/DELETE` | `/api/workouts/{id}` | Get / Delete workout | `200 / 204` |

### Error Response Format

All errors return a structured JSON body — never plain strings:

```json
{
  "error": "not_found",
  "message": "User with id '99' not found",
  "resource": "User",
  "id": 99
}
```

| HTTP Code | Trigger |
|-----------|---------|
| `400` | Duplicate resource (`DuplicateResourceError`) |
| `404` | Not found (`NotFoundError`) |
| `422` | Pydantic validation failure (automatic) |
| `503` | Database unavailable (readiness probe) |

---

## 📋 Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| **Python** | 3.11+ | Backend runtime |
| **Node.js** | 18+ LTS | Frontend toolchain |
| **npm** | 9+ | Package manager |
| **Git** | any | Version control |

> 💡 **Tip:** Use [GitHub Codespaces](https://github.com/features/codespaces) with the included `.devcontainer/` config to get a zero-setup environment with all prerequisites pre-installed.

---

## 🚀 Quick Start

### 1️⃣ Clone the repository

```bash
git clone https://github.com/andrs/skills-build-applications-w-copilot-agent-mode.git
cd skills-build-applications-w-copilot-agent-mode
```

### 2️⃣ Set up the backend

```bash
# Create virtual environment
python3 -m venv andresfit-tracker/backend/.venv

# Activate it
source andresfit-tracker/backend/.venv/bin/activate          # macOS/Linux
# andresfit-tracker\backend\.venv\Scripts\activate.bat       # Windows

# Install dependencies
pip install -r andresfit-tracker/backend/requirements.txt
```

### 3️⃣ Seed the database

```bash
cd andresfit-tracker/backend
.venv/bin/python -m app.seed
```

Expected output:
```
Seeding database with test data...
Database seeded successfully with test data.
```

### 4️⃣ Start the API server

```bash
cd andresfit-tracker/backend
.venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

> 💡 **Tip:** The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/api/docs`.

### 5️⃣ Set up and start the frontend

Open a **new terminal**:

```bash
# Install frontend dependencies
npm install --prefix andresfit-tracker/frontend

# Start the dev server
npm run dev --prefix andresfit-tracker/frontend
```

### 6️⃣ Open the app

| Service | URL |
|---------|-----|
| 🖥️ Frontend | http://localhost:5173 |
| ⚙️ API | http://localhost:8000 |
| 📖 API Docs (Swagger) | http://localhost:8000/api/docs |
| 📘 API Docs (ReDoc) | http://localhost:8000/api/redoc |

---

## 🔍 Verify the Installation

### Health check

```bash
curl http://localhost:8000/health
# {"status":"ok","service":"andresfit-tracker-api"}

curl http://localhost:8000/ready
# {"status":"ready","database":"ok"}
```

### Test the API with curl

```bash
# List all seeded users
curl -s http://localhost:8000/api/users/ | python3 -m json.tool

# Get the leaderboard
curl -s http://localhost:8000/api/leaderboard/ | python3 -m json.tool

# Create a new user
curl -s -X POST http://localhost:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jane_doe", "email": "jane@example.com", "full_name": "Jane Doe"}' \
  | python3 -m json.tool

# Log an activity for user ID 1
curl -s -X POST http://localhost:8000/api/activities/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "activity_type": "running", "duration_minutes": 45, "calories_burned": 420}' \
  | python3 -m json.tool

# Filter workouts by difficulty
curl -s "http://localhost:8000/api/workouts/?difficulty=beginner" | python3 -m json.tool
```

---

## 🧪 Running the Test Suite

```bash
cd andresfit-tracker/backend

# Run all 52 tests
.venv/bin/python -m pytest tests/ -v

# Run only integration tests (API layer)
.venv/bin/python -m pytest tests/test_api.py -v

# Run only unit tests (service layer with mocked repos)
.venv/bin/python -m pytest tests/test_services.py -v
```

Expected result:

```
======================== 52 passed, 1 warning in 6.69s =========================
```

### Test Coverage Breakdown

| Test File | Count | Scope |
|-----------|-------|-------|
| `tests/test_api.py` | 37 | Full HTTP → Service → DB → Response integration |
| `tests/test_services.py` | 15 | Service layer with mocked repositories |
| **Total** | **52** | **100% passing** |

---

## 📁 Repository Structure

```
skills-build-applications-w-copilot-agent-mode/
│
├── 📂 andresfit-tracker/
│   │
│   ├── 📂 backend/                         # FastAPI application
│   │   ├── 📂 app/
│   │   │   ├── 📂 models/                  # SQLAlchemy ORM models
│   │   │   │   ├── base.py                 # Base + TimestampMixin
│   │   │   │   ├── user.py
│   │   │   │   ├── activity.py
│   │   │   │   ├── team.py
│   │   │   │   └── workout.py
│   │   │   │
│   │   │   ├── 📂 schemas/                 # Pydantic v2 schemas
│   │   │   │   ├── common.py               # PaginatedResponse
│   │   │   │   ├── user.py                 # UserCreate/Read/Update
│   │   │   │   ├── activity.py
│   │   │   │   ├── team.py
│   │   │   │   ├── workout.py
│   │   │   │   └── leaderboard.py
│   │   │   │
│   │   │   ├── 📂 repositories/            # Data access layer
│   │   │   │   ├── base.py                 # BaseRepository[T]
│   │   │   │   ├── user_repository.py
│   │   │   │   ├── activity_repository.py
│   │   │   │   ├── team_repository.py
│   │   │   │   ├── workout_repository.py
│   │   │   │   └── leaderboard_repository.py
│   │   │   │
│   │   │   ├── 📂 services/                # Business logic layer
│   │   │   │   ├── exceptions.py           # NotFoundError, DuplicateResourceError
│   │   │   │   ├── user_service.py
│   │   │   │   ├── activity_service.py
│   │   │   │   ├── team_service.py
│   │   │   │   ├── workout_service.py
│   │   │   │   └── leaderboard_service.py
│   │   │   │
│   │   │   ├── 📂 routers/                 # HTTP presentation layer
│   │   │   │   ├── health.py               # /health  /ready
│   │   │   │   ├── users.py
│   │   │   │   ├── activities.py
│   │   │   │   ├── teams.py
│   │   │   │   ├── leaderboard.py
│   │   │   │   └── workouts.py
│   │   │   │
│   │   │   ├── database.py                 # SQLAlchemy engine + get_db()
│   │   │   ├── dependencies.py             # DI wiring graph
│   │   │   ├── exception_handlers.py       # ServiceError → HTTP status
│   │   │   ├── main.py                     # create_app() factory
│   │   │   └── seed.py                     # Database seed script
│   │   │
│   │   ├── 📂 tests/
│   │   │   ├── conftest.py                 # pytest fixtures
│   │   │   ├── test_api.py                 # 37 integration tests
│   │   │   └── test_services.py            # 15 unit tests
│   │   │
│   │   └── requirements.txt
│   │
│   └── 📂 frontend/                        # React application
│       ├── 📂 src/
│       │   ├── 📂 components/
│       │   │   └── Navbar.jsx
│       │   ├── 📂 pages/
│       │   │   ├── Home.jsx
│       │   │   ├── Users.jsx
│       │   │   ├── Activities.jsx
│       │   │   ├── Teams.jsx
│       │   │   ├── Leaderboard.jsx
│       │   │   └── Workouts.jsx
│       │   ├── 📂 services/
│       │   │   └── api.js                  # Centralized fetch wrapper
│       │   ├── App.jsx                     # Router + layout
│       │   └── main.jsx                    # Bootstrap + BrowserRouter
│       ├── vite.config.js                  # Proxy /api/* → :8000
│       └── package.json
│
├── 📂 .github/
│   ├── copilot-instructions.md             # ← Loaded automatically by Copilot
│   ├── 📂 instructions/                    # Per-path Copilot instructions
│   │   ├── fastapi_layered_architecture.instructions.md
│   │   ├── fastapi_backend_enhanced.instructions.md
│   │   └── octofit_tracker_*.instructions.md
│   ├── 📂 prompts/                         # Copilot Agent mode prompts
│   │   ├── scaffold-layered-microservice.prompt.md
│   │   └── fastapi-backend-advanced.prompt.md
│   ├── 📂 steps/                           # GitHub Skills tutorial steps
│   └── 📂 workflows/                       # GitHub Actions CI workflows
│
├── 📂 .devcontainer/                       # GitHub Codespaces config
│   ├── devcontainer.json
│   ├── post_create.sh
│   └── post_start.sh
│
├── commands.md                             # Quick reference for all run commands
├── backendprompt.md                        # Copilot prompt for backend generation
├── FASTAPI_IMPROVEMENTS.md                 # Architecture improvement notes
└── LICENSE
```

---

## 🤖 GitHub Copilot Integration

This repository includes a complete **Copilot context system** that makes AI assistance project-aware:

### How It Works

```
.github/copilot-instructions.md          ← Auto-loaded for every file
         │
         ├── Knows: FastAPI + React stack
         ├── Knows: 4-layer architecture rules
         ├── Knows: which layer can import what
         ├── Knows: error response format
         └── Knows: naming conventions

.github/instructions/*.instructions.md   ← Loaded by applyTo: pattern
         │
         ├── applyTo: "**"               → global rules
         ├── applyTo: "backend/**"       → FastAPI/SQLAlchemy patterns
         └── applyTo: "frontend/**"      → React/fetch patterns

.github/prompts/*.prompt.md              ← Executable Agent Mode prompts
         │
         ├── scaffold-layered-microservice.prompt.md
         │   └── Generates a full layered microservice from scratch
         └── fastapi-backend-advanced.prompt.md
             └── Production-ready backend with pagination, health checks, etc.
```

### Using the Prompts

Open GitHub Copilot Chat in **Agent mode**, then reference a prompt:

```
Generate a new Workout management microservice following the layered architecture.
Use @scaffold-layered-microservice.prompt.md as the blueprint.
```

> 💡 **Tip:** With `copilot-instructions.md` in place, Copilot automatically knows your stack and layer rules — you never need to repeat "use FastAPI" or "don't put business logic in routers" again.

---

## ⚙️ Configuration

### Backend Environment Variables

Create `andresfit-tracker/backend/.env` (copy from `.env.example` if present):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./andresfit.db` | SQLAlchemy database connection string |
| `DEBUG` | `false` | Enable debug mode |

### Frontend (Vite Proxy)

The frontend dev server proxies all `/api/*` requests to the backend. This is configured in `vite.config.js`:

```javascript
server: {
  port: 5173,
  proxy: {
    '/api': 'http://localhost:8000',
  },
}
```

No `.env` file needed for local development — the proxy handles CORS automatically.

---

## 🏃 Production Build

### Backend

```bash
# Run with Uvicorn (production-ready)
cd andresfit-tracker/backend
.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
# Build optimised static assets
npm run build --prefix andresfit-tracker/frontend

# Output: andresfit-tracker/frontend/dist/
# Serve with any static file server (nginx, Caddy, S3, etc.)
```

---

## 🏫 Background: The OctoFit Story

This project is based on a fictional high school scenario: **Paul Octo**, a PE teacher at Mergington High School, wanted to boost student fitness engagement outside class. He partnered with **Jessica Cat**, the school's IT head, to build a digital fitness tracker using GitHub Copilot Agent Mode.

The original exercise used a Django + MongoDB stack. This fork adapts the concept to a **FastAPI + SQLAlchemy + React** stack, demonstrating how Copilot instructions guide AI toward specific architectural patterns.

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/my-improvement`
3. **Follow** the layer architecture rules in `.github/copilot-instructions.md`
4. **Run** the test suite and ensure all 52 tests pass: `pytest tests/ -v`
5. **Commit** your changes: `git commit -m "feat: add workout filtering by duration"`
6. **Push** to your branch: `git push origin feature/my-improvement`
7. **Open** a Pull Request

### Code Standards

> ⚠️ **Architecture rule:** Never write SQLAlchemy queries inside routers. Always route through the service layer. PRs that violate layer boundaries will be declined.

- ✅ Type hints on every function
- ✅ Tests required for new endpoints (integration) and service methods (unit)
- ✅ `response_model` and `status_code` on every FastAPI route
- ✅ Custom exceptions raised in services, mapped to HTTP in `exception_handlers.py`

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Built with ❤️ by **Andres** using [GitHub Copilot Agent Mode](https://github.com/features/copilot)

[![GitHub Copilot](https://img.shields.io/badge/Built%20with-GitHub%20Copilot-1f883d?style=for-the-badge&logo=github&logoColor=white)](https://github.com/features/copilot)

</div>
