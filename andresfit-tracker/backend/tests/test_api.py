# Integration tests — full request → service → repository → response cycle

import pytest


# ── Root ──────────────────────────────────────────────────────────────────────

def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "AndresFit" in r.json()["message"]


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_ready(client):
    r = client.get("/ready")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"


# ── Users ─────────────────────────────────────────────────────────────────────

def test_create_user(client):
    r = client.post("/api/users/", json={"username": "alice", "email": "alice@test.com", "full_name": "Alice"})
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert "id" in data
    assert "created_at" in data


def test_create_user_duplicate_username_returns_400(client):
    client.post("/api/users/", json={"username": "bob", "email": "bob@test.com", "full_name": "Bob"})
    r = client.post("/api/users/", json={"username": "bob", "email": "other@test.com", "full_name": "Bob2"})
    assert r.status_code == 400
    assert r.json()["error"] == "duplicate_resource"


def test_create_user_duplicate_email_returns_400(client):
    client.post("/api/users/", json={"username": "usr1", "email": "shared@test.com", "full_name": "Usr1"})
    r = client.post("/api/users/", json={"username": "usr2", "email": "shared@test.com", "full_name": "Usr2"})
    assert r.status_code == 400


def test_create_user_invalid_payload_returns_422(client):
    r = client.post("/api/users/", json={"username": "x"})
    assert r.status_code == 422


@pytest.mark.parametrize("username,email,expected", [
    ("ab", "valid@test.com", 422),     # username too short
    ("alice", "x@x", 422),             # invalid email — fails min_length (< 5 chars)
    ("", "valid@test.com", 422),       # empty username
])
def test_create_user_validation(client, username, email, expected):
    r = client.post("/api/users/", json={"username": username, "email": email, "full_name": "Test"})
    assert r.status_code == expected


def test_list_users(client):
    client.post("/api/users/", json={"username": "usr1", "email": "usr1@t.com", "full_name": "Usr1"})
    r = client.get("/api/users/")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_user(client):
    uid = client.post("/api/users/", json={"username": "usr2", "email": "usr2@t.com", "full_name": "Usr2"}).json()["id"]
    r = client.get(f"/api/users/{uid}")
    assert r.status_code == 200
    assert r.json()["username"] == "usr2"


def test_get_user_not_found_returns_404(client):
    r = client.get("/api/users/9999")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"
    assert r.json()["resource"] == "User"


def test_delete_user(client):
    uid = client.post("/api/users/", json={"username": "usr3", "email": "usr3@t.com", "full_name": "Usr3"}).json()["id"]
    assert client.delete(f"/api/users/{uid}").status_code == 204
    assert client.get(f"/api/users/{uid}").status_code == 404


def test_delete_user_not_found_returns_404(client):
    r = client.delete("/api/users/9999")
    assert r.status_code == 404


# ── Activities ────────────────────────────────────────────────────────────────

def _make_user(client, username="runner"):
    return client.post("/api/users/", json={
        "username": username, "email": f"{username}@t.com", "full_name": username.title()
    }).json()


def test_create_activity(client):
    user = _make_user(client)
    r = client.post("/api/activities/", json={
        "user_id": user["id"], "activity_type": "running", "duration_minutes": 30, "calories_burned": 300
    })
    assert r.status_code == 201
    assert r.json()["activity_type"] == "running"
    assert "created_at" in r.json()


def test_create_activity_invalid_user_returns_404(client):
    r = client.post("/api/activities/", json={
        "user_id": 9999, "activity_type": "running", "duration_minutes": 30, "calories_burned": 300
    })
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_create_activity_invalid_payload_returns_422(client):
    r = client.post("/api/activities/", json={
        "user_id": 1, "activity_type": "running", "duration_minutes": -5, "calories_burned": 300
    })
    assert r.status_code == 422


def test_list_activities(client):
    user = _make_user(client)
    client.post("/api/activities/", json={"user_id": user["id"], "activity_type": "walking", "duration_minutes": 20, "calories_burned": 100})
    r = client.get("/api/activities/")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_delete_activity(client):
    user = _make_user(client)
    act = client.post("/api/activities/", json={"user_id": user["id"], "activity_type": "strength", "duration_minutes": 45, "calories_burned": 350}).json()
    assert client.delete(f"/api/activities/{act['id']}").status_code == 204


def test_delete_activity_not_found_returns_404(client):
    assert client.delete("/api/activities/9999").status_code == 404


# ── Teams ─────────────────────────────────────────────────────────────────────

def test_create_team(client):
    u = _make_user(client, "member1")
    r = client.post("/api/teams/", json={"name": "Team A", "description": "Test", "member_ids": [u["id"]]})
    assert r.status_code == 201
    assert r.json()["name"] == "Team A"
    assert len(r.json()["members"]) == 1
    assert "created_at" in r.json()


def test_create_team_duplicate_name_returns_400(client):
    client.post("/api/teams/", json={"name": "Dup", "member_ids": []})
    r = client.post("/api/teams/", json={"name": "Dup", "member_ids": []})
    assert r.status_code == 400
    assert r.json()["error"] == "duplicate_resource"


def test_create_team_invalid_member_returns_404(client):
    r = client.post("/api/teams/", json={"name": "Bad", "member_ids": [9999]})
    assert r.status_code == 404


def test_list_teams(client):
    client.post("/api/teams/", json={"name": "Solo", "member_ids": []})
    r = client.get("/api/teams/")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_team(client):
    tid = client.post("/api/teams/", json={"name": "Get Me", "member_ids": []}).json()["id"]
    assert client.get(f"/api/teams/{tid}").status_code == 200


def test_get_team_not_found_returns_404(client):
    assert client.get("/api/teams/9999").status_code == 404


def test_delete_team(client):
    tid = client.post("/api/teams/", json={"name": "Del Me", "member_ids": []}).json()["id"]
    assert client.delete(f"/api/teams/{tid}").status_code == 204


# ── Leaderboard ───────────────────────────────────────────────────────────────

def test_leaderboard_empty(client):
    r = client.get("/api/leaderboard/")
    assert r.status_code == 200
    assert r.json() == []


def test_leaderboard_ranking(client):
    u1 = _make_user(client, "lb1")
    u2 = _make_user(client, "lb2")
    client.post("/api/activities/", json={"user_id": u1["id"], "activity_type": "running", "duration_minutes": 30, "calories_burned": 100})
    client.post("/api/activities/", json={"user_id": u2["id"], "activity_type": "running", "duration_minutes": 60, "calories_burned": 500})
    lb = client.get("/api/leaderboard/").json()
    assert lb[0]["user"]["username"] == "lb2"
    assert lb[0]["total_calories"] == 500
    assert lb[1]["user"]["username"] == "lb1"


def test_leaderboard_entry_fields(client):
    u = _make_user(client, "lbf")
    client.post("/api/activities/", json={"user_id": u["id"], "activity_type": "running", "duration_minutes": 30, "calories_burned": 200})
    entry = client.get("/api/leaderboard/").json()[0]
    assert "user" in entry
    assert "total_duration" in entry
    assert "total_calories" in entry
    assert "activity_count" in entry


# ── Workouts ──────────────────────────────────────────────────────────────────

def test_create_workout(client):
    r = client.post("/api/workouts/", json={
        "name": "Test Run", "description": "A test", "activity_type": "running",
        "duration_minutes": 30, "difficulty": "beginner"
    })
    assert r.status_code == 201
    assert r.json()["name"] == "Test Run"
    assert "created_at" in r.json()


def test_create_workout_invalid_difficulty_returns_422(client):
    r = client.post("/api/workouts/", json={
        "name": "Bad", "activity_type": "running", "duration_minutes": 30, "difficulty": "extreme"
    })
    assert r.status_code == 422


def test_filter_workouts_by_difficulty(client):
    client.post("/api/workouts/", json={"name": "E1", "activity_type": "running", "duration_minutes": 30, "difficulty": "beginner"})
    client.post("/api/workouts/", json={"name": "H1", "activity_type": "running", "duration_minutes": 30, "difficulty": "advanced"})
    r = client.get("/api/workouts/?difficulty=beginner")
    assert r.status_code == 200
    assert all(w["difficulty"] == "beginner" for w in r.json())


def test_filter_workouts_by_activity_type(client):
    client.post("/api/workouts/", json={"name": "R1", "activity_type": "running", "duration_minutes": 30, "difficulty": "beginner"})
    client.post("/api/workouts/", json={"name": "S1", "activity_type": "strength", "duration_minutes": 45, "difficulty": "intermediate"})
    r = client.get("/api/workouts/?activity_type=strength")
    assert all(w["activity_type"] == "strength" for w in r.json())


def test_get_workout_not_found_returns_404(client):
    r = client.get("/api/workouts/9999")
    assert r.status_code == 404
    assert r.json()["error"] == "not_found"


def test_delete_workout(client):
    w = client.post("/api/workouts/", json={"name": "Del", "activity_type": "walking", "duration_minutes": 20, "difficulty": "beginner"}).json()
    assert client.delete(f"/api/workouts/{w['id']}").status_code == 204
