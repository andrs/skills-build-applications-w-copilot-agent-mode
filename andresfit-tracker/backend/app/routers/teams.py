from fastapi import APIRouter, Depends, status

from app.dependencies import get_team_service
from app.schemas.team import TeamCreate, TeamRead
from app.services.team_service import TeamService

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.get("/", response_model=list[TeamRead], summary="List all teams")
def list_teams(service: TeamService = Depends(get_team_service)) -> list[TeamRead]:
    return service.list_teams()


@router.get("/{team_id}", response_model=TeamRead, summary="Get team by ID")
def get_team(team_id: int, service: TeamService = Depends(get_team_service)) -> TeamRead:
    return service.get_team(team_id)


@router.post(
    "/",
    response_model=TeamRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new team",
)
def create_team(
    payload: TeamCreate,
    service: TeamService = Depends(get_team_service),
) -> TeamRead:
    return service.create_team(payload)


@router.delete(
    "/{team_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a team",
)
def delete_team(team_id: int, service: TeamService = Depends(get_team_service)) -> None:
    service.delete_team(team_id)
