def test_forest_endpoint_counts_distinct_habits(client):
    h1 = client.post("/api/habits", json={"name": "A", "category": "gym"}).json()
    h2 = client.post("/api/habits", json={"name": "B", "category": "study"}).json()
    client.post("/api/sessions", json={"habit_id": h1["id"], "date": "2026-09-14", "duration_min": 30})
    client.post("/api/sessions", json={"habit_id": h1["id"], "date": "2026-09-14", "duration_min": 45})
    client.post("/api/sessions", json={"habit_id": h2["id"], "date": "2026-09-14", "duration_min": 60})

    resp = client.get("/api/forest", params={"end_on": "2026-09-14", "days": 7})
    assert resp.status_code == 200
    days = resp.json()["days"]
    assert len(days) == 7
    last = days[-1]
    assert last["date"] == "2026-09-14"
    assert last["completed"] == 2  # hábitos DISTINTOS, não 3 sessões