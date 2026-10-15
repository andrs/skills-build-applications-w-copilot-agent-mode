from fastapi import APIRouter, Depends, status

from app.dependencies import get_user_service
from app.schemas.user import UserCreate, UserRead
from app.services.user_service import UserService

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/", response_model=list[UserRead], summary="List all users")
def list_users(service: UserService = Depends(get_user_service)) -> list[UserRead]:
    return service.list_users()


@router.get("/{user_id}", response_model=UserRead, summary="Get user by ID")
def get_user(user_id: int, service: UserService = Depends(get_user_service)) -> UserRead:
    return service.get_user(user_id)


@router.post(
    "/",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user",
)
def create_user(
    payload: UserCreate,
    service: UserService = Depends(get_user_service),
) -> UserRead:
    return service.create_user(payload)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
)
def delete_user(user_id: int, service: UserService = Depends(get_user_service)) -> None:
    service.delete_user(user_id)
