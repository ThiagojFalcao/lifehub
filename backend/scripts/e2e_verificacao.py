"""Verificação viva do LifeHub — HTTP real, sem mock.

Sobe uma API INSTÂNCIA ISOLADA (banco em /tmp) na porta 8010, exercita todos os
caminhos novos (métricas validadas, coerção, 422, Árvore, Galhos, Journal) e
depois confere a instância real (:8000, banco do usuário) em modo leitura.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # = backend/
PY = os.path.join(ROOT, ".venv", "bin", "python")

API = "http://localhost:8010"
REAL = "http://localhost:8000"
falhas = []


def req(base, path, method="GET", body=None, esperado=None):
    url = f"{base}{path}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method)
    if data:
        r.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(r, timeout=10) as resp:
            status, payload = resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        status, payload = e.code, e.read().decode()
    try:
        payload = json.loads(payload)
    except json.JSONDecodeError:
        pass
    ok = esperado is None or status == esperado
    marca = "OK  " if ok else "FALHA"
    if not ok:
        falhas.append(f"{method} {path} -> {status} (esperado {esperado}): {payload}")
    print(f"[{marca}] {method} {path} -> {status}")
    return status, payload


def check(nome, cond, detalhe=""):
    print(f"[{'OK  ' if cond else 'FALHA'}] {nome} {detalhe}")
    if not cond:
        falhas.append(f"{nome} {detalhe}")


def espera(url, tentativas=40):
    for _ in range(tentativas):
        try:
            urllib.request.urlopen(url, timeout=2).read()
            return True
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    return False


print("=== 1. API isolada (:8010, banco /tmp) ===")
subprocess.run(["cp", os.path.join(ROOT, "lifehub.db"), "/tmp/lifehub-e2e.db"], check=True)
env = {"LIFEHUB_DATABASE_URL": "sqlite:////tmp/lifehub-e2e.db", "PATH": "/usr/bin:/bin", "HOME": "/opt/data"}
proc = subprocess.Popen(
    [
        PY,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        "8010",
    ],
    cwd=ROOT,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)
try:
    if not espera(f"{API}/api/health"):
        sys.exit("API isolada não subiu")
    req(API, "/api/health", esperado=200)

    # --- B1/B2: métricas ricas ---
    _, hab = req(
        API,
        "/api/habits",
        "POST",
        {
            "name": "E2E Foco",
            "category": "study_tech",
            "metrics_schema": {"focus_minutes": "int", "focado": "bool", "topic": "str"},
            "floor_plan": "10 min mesmo no dia ruim",
        },
        esperado=201,
    )
    hid = hab["id"]

    _, s1 = req(
        API,
        "/api/sessions",
        "POST",
        {
            "habit_id": hid,
            "date": "2026-09-12",
            "duration_min": 45,
            "metrics": {"focus_minutes": "45", "focado": "true", "topic": "pytest"},
            "floor_plan_used": True,
            "notes": "sessão e2e",
        },
        esperado=201,
    )
    check("coerção str->int persistida", s1["metrics"]["focus_minutes"] == 45 and isinstance(s1["metrics"]["focus_minutes"], int), str(s1["metrics"]))
    check("coerção str->bool persistida", s1["metrics"]["focado"] is True)
    check("floor_plan_used persistido", s1["floor_plan_used"] is True)

    _, err = req(
        API,
        "/api/sessions",
        "POST",
        {"habit_id": hid, "date": "2026-09-12", "duration_min": 30, "metrics": {"focus_minutes": "muito"}},
        esperado=422,
    )
    check("422 traz motivo legível", "focus_minutes" in str(err.get("detail", "")), str(err.get("detail"))[:80])

    _, s2 = req(
        API,
        "/api/sessions",
        "POST",
        {"habit_id": hid, "date": "2026-09-11", "duration_min": 55, "metrics": {"livre": "sim"}},
        esperado=201,
    )
    check("métrica livre passa", s2["metrics"] == {"livre": "sim"})

    # --- B3/B4: Árvore ---
    _, tree = req(API, f"/api/habits/{hid}/tree?days=30", esperado=200)
    check("Árvore devolve 30 dias", len(tree["days"]) == 30, f"len={len(tree['days'])}")
    hoje = tree["days"][-1]
    check("último dia = hoje com 45 min", hoje["duration_min"] == 45 and hoje["sessions"] == 1, str(hoje))
    su = tree["summary"]
    check("summary total_min == 100", su["total_min"] == 100, str(su))
    check("summary total_hours == 1.7", su["total_hours"] == 1.7, str(su["total_hours"]))
    check("summary active_days == 2", su["active_days"] == 2)
    # 09-11 e 09-12 são consecutivos terminando em hoje → sequência 2.
    check("summary current_streak == 2", su["current_streak"] == 2)
    check("summary best_streak == 2", su["best_streak"] == 2)
    check("summary avg_min_per_active_day == 50.0", su["avg_min_per_active_day"] == 50.0)
    check("Árvore traz o hábito", tree["habit"]["name"] == "E2E Foco")
    req(API, "/api/habits/999999/tree", esperado=404)

    # --- B5: Galhos ordenados ---
    _, galhos = req(API, f"/api/sessions?habit_id={hid}", esperado=200)
    pares = [(g["date"], g["id"]) for g in galhos]
    check("Galhos em ordem (data, id) desc", pares == sorted(pares, reverse=True), str(pares))

    # --- Journal ---
    req(API, "/api/journal/2026-09-12", "PUT", {"content": "dia e2e", "mood": "good", "tags": ["e2e"]}, esperado=200)
    _, j = req(API, "/api/journal/2026-09-12", esperado=200)
    check("journal upsert", j["content"] == "dia e2e" and j["tags"] == ["e2e"], str(j.get("tags")))
    # Espelha o diário físico: PUT em branco REMOVE a entrada e responde 404
    # ("Entry removed") — é contrato testado em tests/test_journal.py.
    _, rem = req(API, "/api/journal/2026-09-12", "PUT", {"content": "", "tags": []}, esperado=404)
    check("PUT em branco remove a entrada", rem.get("detail") == "Entry removed", str(rem))
    req(API, "/api/journal/2026-09-12", esperado=404)
    _, lista = req(API, "/api/journal?limit=5", esperado=200)
    check("entrada removida sai da listagem", all(e["date"] != "2026-09-12" for e in lista))

    # --- Skills (Spec 002) ---
    _, skills = req(API, "/api/skills?end_on=2026-09-12", esperado=200)
    check(
        "skills: 4 árvores na ordem esperada",
        [t["id"] for t in skills["trees"]] == ["tech", "exercicio", "hidratacao", "geral"],
        str([t["id"] for t in skills["trees"]]),
    )
    check("skills: total_xp > 0 no seed", skills["total_xp"] > 0, f"total_xp={skills['total_xp']}")
    check("skills: nível da árvore tech", skills["trees"][0]["level"] >= 1, str(skills["trees"][0]["level"]))
    check(
        "skills: breakdown fecha com o XP da árvore",
        sum(skills["trees"][0]["breakdown"].values()) == skills["trees"][0]["xp"],
        str(skills["trees"][0]),
    )
    check(
        "skills: hábito E2E Foco está na árvore Tech",
        any(h["name"] == "E2E Foco" for h in skills["trees"][0]["habits"]),
        str([h["name"] for h in skills["trees"][0]["habits"]]),
    )
    # Critério de aceite: banco vazio não pode dar 500 nem lista vazia.
    _, vazio = req("http://localhost:8010", "/api/skills?end_on=1999-01-01", esperado=200)
    check("skills: nenhuma sessão até 1999 -> total 0, 4 árvores nível 1", vazio["total_xp"] == 0 and all(t["level"] == 1 for t in vazio["trees"]), str(vazio["total_xp"]))
finally:
    proc.terminate()
    proc.wait(timeout=10)

print("\n=== 2. Instância real (:8000, banco do usuário) — leitura ===")
_, real_hab = req(REAL, "/api/habits", esperado=200)
check("hábitos do seed visíveis", len(real_hab) >= 3, f"{len(real_hab)} hábitos")
if real_hab:
    h0 = real_hab[0]
    _, t0 = req(REAL, f"/api/habits/{h0['id']}/tree?days=30", esperado=200)
    check(f"Árvore do hábito '{h0['name']}' responde", "summary" in t0 and len(t0["days"]) == 30)
_, fr = req(REAL, "/api/forest?days=14", esperado=200)
check("Floresta responde 14 dias", len(fr["days"]) == 14)
req(REAL, "/api/journal?limit=5", esperado=200)
_, rs = req(REAL, "/api/skills", esperado=200)
check("Skills da instância real responde", len(rs["trees"]) == 4 and rs["total_xp"] >= 0, f"total_xp={rs['total_xp']}")

print("\n=== 3. Proxy do frontend (:5173 -> :8000) ===")
req("http://localhost:5173", "/api/health", esperado=200)
_, ph = req("http://localhost:5173", "/api/habits", esperado=200)
check("proxy entrega os hábitos", isinstance(ph, list) and len(ph) >= 3, f"{len(ph) if isinstance(ph, list) else ph}")
_, ps = req("http://localhost:5173", "/api/skills", esperado=200)
check("proxy entrega as skills", isinstance(ps, dict) and len(ps["trees"]) == 4, f"{ps}")

print("\n=== RESULTADO ===")
if falhas:
    print(f"{len(falhas)} FALHA(S):")
    for f in falhas:
        print(" -", f)
    sys.exit(1)
print("Todas as verificações passaram.")
