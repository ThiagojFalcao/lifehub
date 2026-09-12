"""Testes do router /api/journal (F2 — Journal híbrido: markdown + frontmatter)."""

from datetime import date


def test_journal_upsert_and_get(client):
    """PUT cria; GET devolve; PUT de novo atualiza (upsert por data)."""
    today = date.today().isoformat()

    # PUT inicial (create)
    r = client.put(
        f"/api/journal/{today}",
        json={
            "content": "# Dia 1\n\nBem produtivo.",
            "mood": "good",
            "tags": ["foco", "tech"],
        },
    )
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["date"] == today
    assert data["content"] == "# Dia 1\n\nBem produtivo."
    assert data["mood"] == "good"
    assert data["tags"] == ["foco", "tech"]

    # GET devolve o que foi criado
    g = client.get(f"/api/journal/{today}")
    assert g.status_code == 200
    assert g.json()["content"] == "# Dia 1\n\nBem produtivo."

    # PUT de novo (update) — upsert
    r2 = client.put(
        f"/api/journal/{today}",
        json={"content": "# Dia 1\n\nAtualizado.", "mood": "neutral", "tags": []},
    )
    assert r2.status_code == 200
    assert r2.json()["content"] == "# Dia 1\n\nAtualizado."
    assert r2.json()["mood"] == "neutral"

    # Só uma entrada para a mesma data
    all_ = client.get("/api/journal").json()
    assert len(all_) == 1


def test_journal_list_returns_entries_sorted_desc(client):
    """GET /api/journal lista entradas ordenadas por data desc."""
    client.put("/api/journal/2026-01-02", json={"content": "segundo", "mood": "bad", "tags": []})
    client.put("/api/journal/2026-01-01", json={"content": "primeiro", "mood": "good", "tags": []})
    client.put("/api/journal/2026-01-03", json={"content": "tercero", "mood": "neutral", "tags": []})

    all_ = client.get("/api/journal").json()
    assert [e["date"] for e in all_] == ["2026-01-03", "2026-01-02", "2026-01-01"]


def test_journal_get_missing_returns_404(client):
    """GET de uma data sem entrada devolve 404."""
    r = client.get("/api/journal/1999-12-31")
    assert r.status_code == 404


def test_journal_content_slice(client):
    """GET /api/journal suporta ?limit= para paginar (lista curta primeiro)."""
    for i in range(1, 6):
        client.put(f"/api/journal/2026-02-0{i}", json={"content": f"dia {i}", "mood": "good", "tags": []})

    page = client.get("/api/journal?limit=3").json()
    assert len(page) == 3
    # Mais recente primeiro: 2026-02-05, 04, 03
    assert page[0]["date"] == "2026-02-05"
    assert page[2]["date"] == "2026-02-03"


def test_journal_blank_put_removes_entry(client):
    """PUT com todo vazio elimina a entrada (diário físico: limpar = apagar)."""
    client.put("/api/journal/2026-03-01", json={"content": "algo", "mood": "good", "tags": ["x"]})

    # Vazio elimina
    r = client.put("/api/journal/2026-03-01", json={"content": "", "mood": None, "tags": []})
    assert r.status_code == 404

    # Ya no existe
    assert client.get("/api/journal/2026-03-01").status_code == 404
    assert client.get("/api/journal").json() == []


def test_journal_blank_put_on_missing_does_not_create(client):
    """PUT vazio sobre una fecha sin entrada NO crea nada (404)."""
    r = client.put("/api/journal/2026-04-01", json={"content": "  ", "mood": None, "tags": []})
    assert r.status_code == 404
    assert client.get("/api/journal").json() == []