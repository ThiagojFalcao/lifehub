"""Testes de API do /api/skills (Spec 002).

XP é derivado das sessões; o router só converte ORMs para dict e chama
`compute_skills`. Aqui cobrimos a fronteira HTTP: status, shape da resposta,
arborização por categoria, end_on e banco vazio.
"""


def test_skills_banco_vazio_devolve_200_com_quatro_arvores(client):
    resp = client.get("/api/skills")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_xp"] == 0
    assert body["level"] == 1
    assert [t["id"] for t in body["trees"]] == ["tech", "exercicio", "hidratacao", "geral"]
    assert all(t["xp"] == 0 and t["level"] == 1 for t in body["trees"])


def test_skills_agrega_xp_por_arvore_e_breakdown(client):
    h_tech = client.post(
        "/api/habits", json={"name": "Estudo", "category": "study_tech"}
    ).json()
    h_run = client.post(
        "/api/habits", json={"name": "Corrida", "category": "running"}
    ).json()
    client.post(
        "/api/sessions",
        json={"habit_id": h_tech["id"], "date": "2026-09-11", "duration_min": 20},
    )
    client.post(
        "/api/sessions",
        json={
            "habit_id": h_tech["id"],
            "date": "2026-09-12",
            "duration_min": 40,
            "metrics": {"focus_minutes": 40},
            "floor_plan_used": True,
        },
    )
    client.post(
        "/api/sessions",
        json={"habit_id": h_run["id"], "date": "2026-09-12", "duration_min": 30},
    )

    body = client.get("/api/skills", params={"end_on": "2026-09-12"}).json()
    tech = next(t for t in body["trees"] if t["id"] == "tech")
    ex = next(t for t in body["trees"] if t["id"] == "exercicio")

    # 20 (streak 1, dia 09-11)
    # 40 + 10 (floor plan) + 10 (metrics) + 2 (streak dia 2) = 62
    assert tech["xp"] == 82
    assert tech["level"] == 1
    assert tech["breakdown"] == {"base": 60, "floor_plan": 10, "metrics": 10, "streak": 2}
    assert tech["habits"][0]["name"] == "Estudo"
    assert tech["habits"][0]["xp"] == 82

    assert ex["xp"] == 30
    assert ex["level"] == 1

    assert body["total_xp"] == 112


def test_skills_habito_sem_sessao_aparece_na_arvore_com_xp_zero(client):
    client.post("/api/habits", json={"name": "Ler", "category": "reading"})
    body = client.get("/api/skills").json()
    geral = next(t for t in body["trees"] if t["id"] == "geral")
    assert geral["habits"] == [
        {
            "id": geral["habits"][0]["id"],
            "name": "Ler",
            "xp": 0,
            "level": 1,
            "xp_no_nivel": 0,
            "xp_para_proximo": 100,
            "progresso": 0.0,
        }
    ]


def test_skills_end_on_limita_o_calculo(client):
    h = client.post("/api/habits", json={"name": "Estudo", "category": "study_tech"}).json()
    client.post("/api/sessions", json={"habit_id": h["id"], "date": "2026-09-11", "duration_min": 50})
    client.post("/api/sessions", json={"habit_id": h["id"], "date": "2026-09-20", "duration_min": 999})

    body = client.get("/api/skills", params={"end_on": "2026-09-11"}).json()
    assert body["total_xp"] == 50


def test_skills_nivel_geral_soma_todas_as_arvores(client):
    h1 = client.post("/api/habits", json={"name": "Estudo", "category": "study_tech"}).json()
    h2 = client.post("/api/habits", json={"name": "Corrida", "category": "running"}).json()
    for h in (h1, h2):
        client.post("/api/sessions", json={"habit_id": h["id"], "date": "2026-09-12", "duration_min": 60})

    body = client.get("/api/skills", params={"end_on": "2026-09-12"}).json()
    assert body["total_xp"] == 120
    assert body["level"] == 2
    assert body["xp_no_nivel"] == 20
    assert body["progresso"] == 0.1