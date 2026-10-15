from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(tags=["health"])


@router.get("/health", summary="Liveness probe")
def liveness() -> dict:
    return {"status": "ok", "service": "andresfit-tracker-api"}


@router.get("/ready", summary="Readiness probe — checks DB connectivity")
def readiness(db: Session = Depends(get_db)) -> JSONResponse:
    try:
        db.execute(text("SELECT 1"))
        return JSONResponse(content={"status": "ready", "database": "ok"})
    except Exception as exc:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"status": "not_ready", "database": str(exc)},
        )
