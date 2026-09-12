def test_create_and_get_habit(client):
    resp = client.post(
        "/api/habits",
        json={
            "name": "Estudo Tech",
            "category": "study_tech",
            "metrics_schema": {"focus_minutes": "int", "topic": "str"},
            "floor_plan": "abrir editor + 1 parágrafo",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"] == 1
    assert body["name"] == "Estudo Tech"

    got = client.get(f"/api/habits/{body['id']}")
    assert got.status_code == 200
    assert got.json()["category"] == "study_tech"


def test_list_habits_sorted_by_name(client):
    client.post("/api/habits", json={"name": "Corrida", "category": "running"})
    client.post("/api/habits", json={"name": "Academia", "category": "gym"})
    names = [h["name"] for h in client.get("/api/habits").json()]
    assert names == ["Academia", "Corrida"]


def test_get_missing_habit_returns_404(client):
    assert client.get("/api/habits/999").status_code == 404