def test_tree_404_para_habito_inexistente(client):
    resp = client.get("/api/habits/999/tree")
    assert resp.status_code == 404


def test_tree_retorna_habito_janela_e_summary(client):
    h = client.post("/api/habits", json={"name": "Corrida", "category": "gym"}).json()
    client.post(
        "/api/sessions",
        json={"habit_id": h["id"], "date": "2026-09-14", "duration_min": 30},
    )

    resp = client.get(f"/api/habits/{h['id']}/tree", params={"end_on": "2026-09-14", "days": 7})
    assert resp.status_code == 200
    body = resp.json()

    assert body["habit"]["id"] == h["id"]
    assert body["habit"]["name"] == "Corrida"
    assert len(body["days"]) == 7
    assert body["days"][-1]["date"] == "2026-09-14"
    assert body["days"][-1]["duration_min"] == 30
    assert body["days"][-1]["sessions"] == 1
    assert body["summary"]["total_min"] == 30


def test_tree_agrega_multiplas_sessoes_do_mesmo_dia(client):
    h = client.post("/api/habits", json={"name": "Leitura", "category": "study"}).json()
    for dur in (20, 25):
        client.post(
            "/api/sessions",
            json={"habit_id": h["id"], "date": "2026-09-14", "duration_min": dur},
        )

    body = client.get(
        f"/api/habits/{h['id']}/tree", params={"end_on": "2026-09-14", "days": 1}
    ).json()
    assert body["days"][0]["sessions"] == 2
    assert body["days"][0]["duration_min"] == 45


def test_tree_nao_vaza_sessoes_de_outro_habito(client):
    h1 = client.post("/api/habits", json={"name": "A1", "category": "gym"}).json()
    h2 = client.post("/api/habits", json={"name": "B1", "category": "gym"}).json()
    client.post("/api/sessions", json={"habit_id": h1["id"], "date": "2026-09-14", "duration_min": 30})
    client.post("/api/sessions", json={"habit_id": h2["id"], "date": "2026-09-14", "duration_min": 90})

    body = client.get(
        f"/api/habits/{h1['id']}/tree", params={"end_on": "2026-09-14", "days": 1}
    ).json()
    assert body["days"][0]["duration_min"] == 30
    assert body["summary"]["total_min"] == 30


def test_tree_summary_e_cumulativo_mesmo_com_janela_curta(client):
    h = client.post("/api/habits", json={"name": "Meditar", "category": "wellness"}).json()
    client.post("/api/sessions", json={"habit_id": h["id"], "date": "2026-06-01", "duration_min": 50})
    client.post("/api/sessions", json={"habit_id": h["id"], "date": "2026-09-14", "duration_min": 10})

    body = client.get(
        f"/api/habits/{h['id']}/tree", params={"end_on": "2026-09-14", "days": 1}
    ).json()
    assert body["days"][0]["duration_min"] == 10
    assert body["summary"]["total_min"] == 60
    assert body["summary"]["total_hours"] == 1.0
    assert body["summary"]["active_days"] == 2


def test_tree_streak_conta_dias_consecutivos(client):
    h = client.post("/api/habits", json={"name": "Água", "category": "wellness"}).json()
    for dia in ("2026-09-12", "2026-09-13", "2026-09-14"):
        client.post("/api/sessions", json={"habit_id": h["id"], "date": dia, "duration_min": 5})

    body = client.get(
        f"/api/habits/{h['id']}/tree", params={"end_on": "2026-09-14", "days": 7}
    ).json()
    assert body["summary"]["current_streak"] == 3
    assert body["summary"]["best_streak"] == 3


def test_tree_rejeita_dias_fora_do_limite(client):
    h = client.post("/api/habits", json={"name": "Limite", "category": "misc"}).json()
    assert client.get(f"/api/habits/{h['id']}/tree", params={"days": 0}).status_code == 422
    assert client.get(f"/api/habits/{h['id']}/tree", params={"days": 999}).status_code == 422


def test_tree_sem_sessoes_retorna_janela_zerada(client):
    h = client.post("/api/habits", json={"name": "Novo", "category": "misc"}).json()
    body = client.get(
        f"/api/habits/{h['id']}/tree", params={"end_on": "2026-09-14", "days": 3}
    ).json()
    assert all(dia["duration_min"] == 0 and dia["color"] == "red" for dia in body["days"])
    assert body["summary"]["current_streak"] == 0
    assert body["summary"]["total_min"] == 0
