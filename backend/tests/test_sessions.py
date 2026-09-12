def test_create_session_requires_valid_habit(client):
    resp = client.post(
        "/api/sessions",
        json={"habit_id": 999, "date": "2026-09-14", "duration_min": 60},
    )
    assert resp.status_code == 404


def test_create_and_list_sessions(client):
    h = client.post("/api/habits", json={"name": "Estudo", "category": "study"}).json()
    resp = client.post(
        "/api/sessions",
        json={
            "habit_id": h["id"],
            "date": "2026-09-14",
            "duration_min": 60,
            "metrics": {"topic": "SQL Window Functions"},
            "floor_plan_used": False,
        },
    )
    assert resp.status_code == 201
    assert resp.json()["metrics"] == {"topic": "SQL Window Functions"}

    sessions = client.get("/api/sessions").json()
    assert len(sessions) == 1
    assert sessions[0]["habit_id"] == h["id"]


def test_session_requires_positive_duration(client):
    h = client.post("/api/habits", json={"name": "Yoga", "category": "wellness"}).json()
    resp = client.post(
        "/api/sessions",
        json={"habit_id": h["id"], "date": "2026-09-14", "duration_min": 0},
    )
    assert resp.status_code == 422