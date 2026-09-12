"""Skill trees + XP — progressão derivada das sessões (Spec 002).

O XP **não é armazenado**: é função pura sobre as sessões já persistidas, como a
Floresta e a Árvore. Isso significa que o histórico ganha XP retroativo, que não
existe drift entre sessão e XP, e que mudar uma constante aqui recalcula o passado
inteiro. As constantes são o contrato com `docs/specs/002-skill-trees-xp.md` —
mexer nelas muda níveis que o usuário já viu.
"""

from __future__ import annotations

import math
from datetime import date, timedelta

# --- Fórmula (Decisão 2 da spec 002) ---------------------------------------
XP_POR_MINUTO = 1
BONUS_FLOOR_PLAN = 1.25  # multiplica a base: recompensa o "não depender de motivação"
BONUS_TELEMETRIA = 10  # por sessão com metrics não vazio
XP_POR_DIA_DE_STREAK = 2
TETO_DIAS_DE_STREAK = 5  # bônus de constância satura em 5 dias


def _arredonda_half_up(valor: float) -> int:
    """Arredonda para cima no .5.

    `round()` do Python é *half-even* (12.5 → 12, 0.5 → 0), o que daria XP
    inconsistente conforme o valor caia em par ou ímpar.
    """
    return math.floor(valor + 0.5)


def xp_of_session(
    duration_min: int,
    floor_plan_used: bool,
    metrics: dict,
    streak_no_dia: int,
) -> float:
    """XP de uma única sessão (float; o arredondamento é feito no total, uma vez)."""
    xp = duration_min * XP_POR_MINUTO
    if floor_plan_used:
        xp *= BONUS_FLOOR_PLAN
    if metrics:
        xp += BONUS_TELEMETRIA
    dias_bonus = min(max(streak_no_dia - 1, 0), TETO_DIAS_DE_STREAK)
    xp += dias_bonus * XP_POR_DIA_DE_STREAK
    return float(xp)


def _xp_do_inicio_do_nivel(nivel: int) -> int:
    """XP acumulado necessário para *começar* o nível (curva triangular)."""
    return 50 * nivel * (nivel - 1)


def nivel_de_xp(xp: int) -> dict:
    """Nível, XP dentro do nível, faixa total e progresso (0..1)."""
    nivel = 1
    while _xp_do_inicio_do_nivel(nivel + 1) <= xp:
        nivel += 1
    inicio = _xp_do_inicio_do_nivel(nivel)
    faixa = _xp_do_inicio_do_nivel(nivel + 1) - inicio
    return {
        "level": nivel,
        "xp_no_nivel": xp - inicio,
        "xp_para_proximo": faixa,
        "progresso": round((xp - inicio) / faixa, 2),
    }


# --- Árvores (Decisão 4 da spec 002) ---------------------------------------
#
# `category` do hábito é string livre; o fallback `geral` garante que um hábito
# novo (ex.: `reading`) nunca fique de fora — absorve sem deploy. Revisável se
# o usuário criar uma 4ª árvore fixa.
TREES: list[dict] = [
    {"id": "tech", "name": "Tech", "categories": {"study_tech"}},
    {"id": "exercicio", "name": "Exercício", "categories": {"running", "exercise", "gym", "workout"}},
    {"id": "hidratacao", "name": "Hidratação", "categories": {"water", "hydration"}},
    {"id": "geral", "name": "Geral", "categories": set()},
]


def tree_for_category(category: str) -> str:
    """Id da árvore para uma categoria de hábito (fallback: `geral`)."""
    for arvore in TREES:
        if category.lower() in arvore["categories"]:
            return arvore["id"]
    return "geral"


# --- Agregação (Decisão 1: XP derivado) -------------------------------------


def _streak_por_habito(
    sessoes: list[dict], end_on: date
) -> dict[int, dict[date, int]]:
    """Sequência do dia para cada sessão, por hábito.

    Uma passada ordenada por (habit, data) — o streak do dia N depende das
    sessões dos dias anteriores; janelas parciais (por ex. "só a última
    semana") produziriam streaks errados na borda.
    """
    por_habito: dict[int, list[tuple[date, int]]] = {}
    for s in sessoes:
        if s["date"] <= end_on:
            por_habito.setdefault(s["habit_id"], []).append((s["date"], s["duration_min"]))

    resultado: dict[int, dict[date, int]] = {}
    for habit_id, itens in por_habito.items():
        itens.sort(key=lambda t: t[0])
        streak = 0
        dia_anterior: date | None = None
        for dia, _ in itens:
            if dia_anterior is not None and dia - dia_anterior == timedelta(days=1):
                streak += 1
            else:
                streak = 1
            resultado.setdefault(habit_id, {})[dia] = streak
            dia_anterior = dia
    return resultado


def compute_skills(
    habits: list[dict],
    sessions: list[dict],
    end_on: date,
) -> dict:
    """Deriva árvores, níveis e breakdown de todas as sessões até `end_on`.

    `habits` e `sessions` são dicionários (o router converte os ORMs); a função
    é pura, sem tocar no banco — mesma arquitetura de `compute_forest`.
    """
    streaks = _streak_por_habito(sessions, end_on)

    # XP por hábito (arredondado uma única vez no total: 3 x 12.5 min de base
    # não pode virar somas de 13+15+17=45, tem que ser 44).
    xp_habito: dict[int, dict] = {}
    for h in habits:
        xp_habito[h["id"]] = {"xp": 0.0, "base": 0, "floor_plan": 0, "metrics": 0, "streak": 0}

    for s in sessions:
        if s["date"] > end_on:
            continue
        habit_id = s["habit_id"]
        if habit_id not in xp_habito:
            continue
        streak = streaks.get(habit_id, {}).get(s["date"], 1)
        base = s["duration_min"] * XP_POR_MINUTO
        floor_plan = (
            round(base * (BONUS_FLOOR_PLAN - 1), 4) if s.get("floor_plan_used") else 0
        )
        bonus_metrics = BONUS_TELEMETRIA if s.get("metrics") else 0
        bonus_streak = (
            min(max(streak - 1, 0), TETO_DIAS_DE_STREAK) * XP_POR_DIA_DE_STREAK
        )
        contas = xp_habito[habit_id]
        contas["base"] += base
        contas["floor_plan"] += floor_plan
        contas["metrics"] += bonus_metrics
        contas["streak"] += bonus_streak
        contas["xp"] += base + floor_plan + bonus_metrics + bonus_streak

    arvores: dict[str, dict] = {
        t["id"]: {
            "id": t["id"],
            "name": t["name"],
            "xp": 0,
            "level": 1,
            "xp_no_nivel": 0,
            "xp_para_proximo": 100,
            "progresso": 0.0,
            "breakdown": {"base": 0, "floor_plan": 0, "metrics": 0, "streak": 0},
            "habits": [],
        }
        for t in TREES
    }

    for h in habits:
        contas = xp_habito.get(h["id"])
        if contas is None:
            habit_xp = 0
            nivel_info = nivel_de_xp(0)
            exp = {**nivel_info, "xp": 0}
            contas = {"base": 0, "floor_plan": 0, "metrics": 0, "streak": 0}
        else:
            habit_xp = _arredonda_half_up(contas["xp"])
            nivel_info = nivel_de_xp(habit_xp)
            exp = {**nivel_info, "xp": habit_xp}

        tree_id = tree_for_category(h["category"])
        t = arvores[tree_id]
        t["habits"].append(
            {"id": h["id"], "name": h["name"], **exp}
        )
        t["xp"] += habit_xp
        for chave in ("base", "floor_plan", "metrics", "streak"):
            t["breakdown"][chave] += round(contas[chave])

    total_xp = sum(t["xp"] for t in arvores.values())
    total = nivel_de_xp(total_xp)

    for t in arvores.values():
        nivel = nivel_de_xp(t["xp"])
        t.update(
            {
                "level": nivel["level"],
                "xp_no_nivel": nivel["xp_no_nivel"],
                "xp_para_proximo": nivel["xp_para_proximo"],
                "progresso": nivel["progresso"],
            }
        )
        t["habits"].sort(key=lambda hh: hh["name"])

    return {
        "total_xp": total_xp,
        "level": total["level"],
        "xp_no_nivel": total["xp_no_nivel"],
        "xp_para_proximo": total["xp_para_proximo"],
        "progresso": total["progresso"],
        "trees": [arvores[t["id"]] for t in TREES],
    }
