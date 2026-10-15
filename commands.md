# AndresFit Tracker — Run Commands

## Backend (FastAPI)

### Setup (first time only)
```bash
python3 -m venv andresfit-tracker/backend/.venv
andresfit-tracker/backend/.venv/bin/pip install -r andresfit-tracker/backend/requirements.txt
```

### Seed the database
```bash
cd andresfit-tracker/backend && .venv/bin/python -m app.seed
```

### Start the API server (port 8000)
```bash
cd andresfit-tracker/backend && .venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Run backend tests
```bash
cd andresfit-tracker/backend && .venv/bin/python -m pytest tests/ -v
```

---

## Frontend (React + Vite)

### Setup (first time only)
```bash
npm install --prefix andresfit-tracker/frontend
```

### Start the dev server (port 5173)
```bash
npm run dev --prefix andresfit-tracker/frontend
```

### Build for production
```bash
npm run build --prefix andresfit-tracker/frontend
```

---

## Access

| Service  | URL                       |
|----------|---------------------------|
| Frontend | http://localhost:5173      |
| Backend  | http://localhost:8000      |
| API docs | http://localhost:8000/docs |
