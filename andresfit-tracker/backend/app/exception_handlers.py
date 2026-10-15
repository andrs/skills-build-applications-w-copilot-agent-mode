from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.services.exceptions import (
    DuplicateResourceError,
    InvalidOperationError,
    NotFoundError,
    ServiceError,
)


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": "not_found",
                "message": str(exc),
                "resource": exc.resource,
                "id": exc.id,
            },
        )

    @app.exception_handler(DuplicateResourceError)
    async def duplicate_handler(request: Request, exc: DuplicateResourceError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": "duplicate_resource",
                "message": str(exc),
                "resource": exc.resource,
                "field": exc.field,
            },
        )

    @app.exception_handler(InvalidOperationError)
    async def invalid_op_handler(request: Request, exc: InvalidOperationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": "invalid_operation", "message": str(exc)},
        )

    @app.exception_handler(ServiceError)
    async def generic_service_handler(request: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": "service_error", "message": str(exc)},
        )
