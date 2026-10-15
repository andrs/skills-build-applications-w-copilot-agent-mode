# Unit tests — service layer with mocked repositories

from unittest.mock import MagicMock

import pytest

from app.services.exceptions import DuplicateResourceError, NotFoundError
from app.services.user_service import UserService
from app.services.activity_service import ActivityService
from app.services.team_service import TeamService
from app.services.workout_service import WorkoutService
from app.schemas.user import UserCreate, UserRead
from app.schemas.activity import ActivityCreate
from app.schemas.team import TeamCreate
from app.schemas.workout import WorkoutCreate
from app.models.user import User
from app.models.activity import Activity
from app.models.workout import Workout
from datetime import datetime


def _fake_user(id=1, username="alice", email="alice@t.com"):
    u = MagicMock(spec=User)
    u.id = id
    u.username = username
    u.email = email
    u.full_name = "Alice"
    u.created_at = datetime.utcnow()
    u.updated_at = datetime.utcnow()
    u.teams = []
    return u


def _fake_activity(id=1, user_id=1):
    a = MagicMock(spec=Activity)
    a.id = id
    a.user_id = user_id
    a.activity_type = "running"
    a.duration_minutes = 30
    a.calories_burned = 300.0
    a.date = datetime.utcnow()
    a.created_at = datetime.utcnow()
    a.updated_at = datetime.utcnow()
    return a


# ── UserService ───────────────────────────────────────────────────────────────

class TestUserService:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = UserService(self.repo)

    def test_get_user_raises_not_found(self):
        self.repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError) as exc:
            self.service.get_user(99)
        assert exc.value.resource == "User"
        assert exc.value.id == 99

    def test_create_user_raises_on_duplicate_username(self):
        self.repo.get_by_username.return_value = _fake_user()
        with pytest.raises(DuplicateResourceError) as exc:
            self.service.create_user(UserCreate(username="alice", email="new@t.com", full_name="Alice"))
        assert exc.value.field == "username"

    def test_create_user_raises_on_duplicate_email(self):
        self.repo.get_by_username.return_value = None
        self.repo.get_by_email.return_value = _fake_user()
        with pytest.raises(DuplicateResourceError) as exc:
            self.service.create_user(UserCreate(username="new", email="alice@t.com", full_name="New"))
        assert exc.value.field == "email"

    def test_create_user_succeeds(self):
        self.repo.get_by_username.return_value = None
        self.repo.get_by_email.return_value = None
        fake = _fake_user()
        self.repo.create.return_value = fake
        result = self.service.create_user(UserCreate(username="alice", email="alice@t.com", full_name="Alice"))
        assert isinstance(result, UserRead)
        assert result.username == "alice"

    def test_delete_user_raises_not_found(self):
        self.repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            self.service.delete_user(99)

    def test_delete_user_calls_repo(self):
        self.repo.get_by_id.return_value = _fake_user()
        self.service.delete_user(1)
        self.repo.delete.assert_called_once_with(1)


# ── ActivityService ───────────────────────────────────────────────────────────

class TestActivityService:
    def setup_method(self):
        self.activity_repo = MagicMock()
        self.user_repo = MagicMock()
        self.service = ActivityService(self.activity_repo, self.user_repo)

    def test_create_activity_raises_when_user_not_found(self):
        self.user_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError) as exc:
            self.service.create_activity(ActivityCreate(user_id=99, activity_type="running", duration_minutes=30, calories_burned=300))
        assert exc.value.resource == "User"

    def test_create_activity_succeeds(self):
        self.user_repo.get_by_id.return_value = _fake_user()
        fake_act = _fake_activity()
        self.activity_repo.create.return_value = fake_act
        result = self.service.create_activity(
            ActivityCreate(user_id=1, activity_type="running", duration_minutes=30, calories_burned=300)
        )
        assert result.activity_type == "running"

    def test_delete_activity_raises_not_found(self):
        self.activity_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            self.service.delete_activity(99)


# ── TeamService ───────────────────────────────────────────────────────────────

class TestTeamService:
    def setup_method(self):
        self.team_repo = MagicMock()
        self.user_repo = MagicMock()
        self.service = TeamService(self.team_repo, self.user_repo)

    def test_create_team_raises_on_duplicate_name(self):
        self.team_repo.get_by_name.return_value = MagicMock()
        with pytest.raises(DuplicateResourceError) as exc:
            self.service.create_team(TeamCreate(name="Dup", member_ids=[]))
        assert exc.value.field == "name"

    def test_create_team_raises_when_member_not_found(self):
        self.team_repo.get_by_name.return_value = None
        self.user_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError) as exc:
            self.service.create_team(TeamCreate(name="T", member_ids=[99]))
        assert exc.value.resource == "User"

    def test_get_team_raises_not_found(self):
        self.team_repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            self.service.get_team(99)


# ── WorkoutService ────────────────────────────────────────────────────────────

class TestWorkoutService:
    def setup_method(self):
        self.repo = MagicMock()
        self.service = WorkoutService(self.repo)

    def test_get_workout_raises_not_found(self):
        self.repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError) as exc:
            self.service.get_workout(99)
        assert exc.value.resource == "Workout"

    def test_delete_workout_raises_not_found(self):
        self.repo.get_by_id.return_value = None
        with pytest.raises(NotFoundError):
            self.service.delete_workout(99)

    def test_list_workouts_with_filters_delegates_to_repo(self):
        self.repo.list_filtered.return_value = []
        self.service.list_workouts(difficulty="beginner", activity_type="running")
        self.repo.list_filtered.assert_called_once_with(difficulty="beginner", activity_type="running")
