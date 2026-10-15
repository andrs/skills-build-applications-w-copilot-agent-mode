def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["message"] == "Welcome to AndresFit Tracker API"


# --- Users ---

def test_create_user(client):
    r = client.post("/api/users/", json={"username": "alice", "email": "alice@test.com", "full_name": "Alice Test"})
    assert r.status_code == 201
    data = r.json()
    assert data["username"] == "alice"
    assert "id" in data


def test_create_user_duplicate_username(client):
    client.post("/api/users/", json={"username": "bob", "email": "bob@test.com", "full_name": "Bob"})
    r = client.post("/api/users/", json={"username": "bob", "email": "other@test.com", "full_name": "Bob2"})
    assert r.status_code == 400


def test_create_user_invalid_payload(client):
    r = client.post("/api/users/", json={"username": ""})
    assert r.status_code == 422


def test_list_users(client):
    client.post("/api/users/", json={"username": "u1", "email": "u1@t.com", "full_name": "U1"})
    r = client.get("/api/users/")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_get_user(client):
    create = client.post("/api/users/", json={"username": "u2", "email": "u2@t.com", "full_name": "U2"})
    uid = create.json()["id"]
    r = client.get(f"/api/users/{uid}")
    assert r.status_code == 200
    assert r.json()["username"] == "u2"


def test_get_user_not_found(client):
    r = client.get("/api/users/9999")
    assert r.status_code == 404


def test_delete_user(client):
    create = client.post("/api/users/", json={"username": "u3", "email": "u3@t.com", "full_name": "U3"})
    uid = create.json()["id"]
    r = client.delete(f"/api/users/{uid}")
    assert r.status_code == 204
    r = client.get(f"/api/users/{uid}")
    assert r.status_code == 404


# --- Activities ---

def test_create_activity(client):
    user = client.post("/api/users/", json={"username": "runner", "email": "r@t.com", "full_name": "Runner"}).json()
    r = client.post("/api/activities/", json={
        "user_id": user["id"], "activity_type": "running", "duration_minutes": 30, "calories_burned": 300
    })
    assert r.status_code == 201
    assert r.json()["activity_type"] == "running"


def test_create_activity_invalid_user(client):
    r = client.post("/api/activities/", json={
        "user_id": 9999, "activity_type": "running", "duration_minutes": 30, "calories_burned": 300
    })
    assert r.status_code == 404


def test_create_activity_invalid_payload(client):
    r = client.post("/api/activities/", json={"user_id": 1, "activity_type": "running", "duration_minutes": -5, "calories_burned": 300})
    assert r.status_code == 422


def test_list_activities(client):
    user = client.post("/api/users/", json={"username": "a1", "email": "a1@t.com", "full_name": "A1"}).json()
    client.post("/api/activities/", json={"user_id": user["id"], "activity_type": "walking", "duration_minutes": 20, "calories_burned": 100})
    r = client.get("/api/activities/")
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_delete_activity(client):
    user = client.post("/api/users/", json={"username": "a2", "email": "a2@t.com", "full_name": "A2"}).json()
    act = client.post("/api/activities/", json={"user_id": user["id"], "activity_type": "strength", "duration_minutes": 45, "calories_burned": 350}).json()
    r = client.delete(f"/api/activities/{act['id']}")
    assert r.status_code == 204


# --- Teams ---

def test_create_team(client):
    u = client.post("/api/users/", json={"username": "t1", "email": "t1@t.com", "full_name": "T1"}).json()
    r = client.post("/api/teams/", json={"name": "Team A", "description": "Test", "member_ids": [u["id"]]})
    assert r.status_code == 201
    assert r.json()["name"] == "Team A"
    assert len(r.json()["members"]) == 1


def test_create_team_duplicate_name(client):
    client.post("/api/teams/", json={"name": "Dup", "member_ids": []})
    r = client.post("/api/teams/", json={"name": "Dup", "member_ids": []})
    assert r.status_code == 400


def test_create_team_invalid_member(client):
    r = client.post("/api/teams/", json={"name": "Bad", "member_ids": [9999]})
    assert r.status_code == 404


def test_list_teams(client):
    client.post("/api/teams/", json={"name": "Solo", "member_ids": []})
    r = client.get("/api/teams/")
    assert r.status_code == 200
    assert len(r.json()) >= 1


def test_get_team(client):
    create = client.post("/api/teams/", json={"name": "Get Me", "member_ids": []})
    tid = create.json()["id"]
    r = client.get(f"/api/teams/{tid}")
    assert r.status_code == 200


def test_delete_team(client):
    create = client.post("/api/teams/", json={"name": "Del Me", "member_ids": []})
    tid = create.json()["id"]
    r = client.delete(f"/api/teams/{tid}")
    assert r.status_code == 204


# --- Leaderboard ---

def test_leaderboard_empty(client):
    r = client.get("/api/leaderboard/")
    assert r.status_code == 200
    assert r.json() == []


def test_leaderboard_ranking(client):
    u1 = client.post("/api/users/", json={"username": "lb1", "email": "lb1@t.com", "full_name": "LB1"}).json()
    u2 = client.post("/api/users/", json={"username": "lb2", "email": "lb2@t.com", "full_name": "LB2"}).json()
    client.post("/api/activities/", json={"user_id": u1["id"], "activity_type": "running", "duration_minutes": 30, "calories_burned": 100})
    client.post("/api/activities/", json={"user_id": u2["id"], "activity_type": "running", "duration_minutes": 60, "calories_burned": 500})
    r = client.get("/api/leaderboard/")
    lb = r.json()
    assert lb[0]["user"]["username"] == "lb2"
    assert lb[0]["total_calories"] == 500
    assert lb[1]["user"]["username"] == "lb1"


# --- Workouts ---

def test_create_workout(client):
    r = client.post("/api/workouts/", json={
        "name": "Test Run", "description": "A test", "activity_type": "running",
        "duration_minutes": 30, "difficulty": "beginner"
    })
    assert r.status_code == 201
    assert r.json()["name"] == "Test Run"


def test_create_workout_invalid_difficulty(client):
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


def test_delete_workout(client):
    w = client.post("/api/workouts/", json={"name": "Del", "activity_type": "walking", "duration_minutes": 20, "difficulty": "beginner"}).json()
    r = client.delete(f"/api/workouts/{w['id']}")
    assert r.status_code == 204
