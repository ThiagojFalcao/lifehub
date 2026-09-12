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


def test_metrics_invalidas_retornam_422(client):
    h = client.post(
        "/api/habits",
        json={"name": "Foco", "category": "study", "metrics_schema": {"focus_minutes": "int"}},
    ).json()
    resp = client.post(
        "/api/sessions",
        json={
            "habit_id": h["id"],
            "date": "2026-09-14",
            "duration_min": 30,
            "metrics": {"focus_minutes": "muito"},
        },
    )
    assert resp.status_code == 422
    assert "focus_minutes" in resp.json()["detail"]


def test_metrics_validas_sao_coeridas_na_persistencia(client):
    h = client.post(
        "/api/habits",
        json={"name": "Foco2", "category": "study", "metrics_schema": {"focus_minutes": "int"}},
    ).json()
    resp = client.post(
        "/api/sessions",
        json={
            "habit_id": h["id"],
            "date": "2026-09-14",
            "duration_min": 30,
            "metrics": {"focus_minutes": "45"},
        },
    )
    assert resp.status_code == 201
    assert resp.json()["metrics"]["focus_minutes"] == 45
    assert isinstance(resp.json()["metrics"]["focus_minutes"], int)


def test_metrica_livre_passa(client):
    h = client.post(
        "/api/habits",
        json={"name": "Foco3", "category": "study", "metrics_schema": {"focus_minutes": "int"}},
    ).json()
    resp = client.post(
        "/api/sessions",
        json={
            "habit_id": h["id"],
            "date": "2026-09-14",
            "duration_min": 30,
            "metrics": {"extra": "livre"},
        },
    )
    assert resp.status_code == 201
    assert resp.json()["metrics"] == {"extra": "livre"}


def test_habito_sem_schema_aceita_qualquer_metrica(client):
    h = client.post("/api/habits", json={"name": "Solto", "category": "misc"}).json()
    resp = client.post(
        "/api/sessions",
        json={
            "habit_id": h["id"],
            "date": "2026-09-14",
            "duration_min": 30,
            "metrics": {"qualquer": [1, 2, 3]},
        },
    )
    assert resp.status_code == 201
