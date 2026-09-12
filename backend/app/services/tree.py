"""Árvore — histórico de um único hábito.

Diferente da Floresta (quantos hábitos distintos foram regados por dia), a Árvore
olha a **intensidade por hábito**: quantos minutos foram investidos em cada dia e
se isso está acima ou abaixo da média móvel recente do próprio hábito.

Função pura: recebe `by_date` já agregado (`{date: (n_sessoes, minutos)}`) e não
toca no banco — é por isso que a janela de exibição (`days`) pode ser pequena
enquanto os totais do `summary` continuam cumulativos sobre todo o histórico.
"""

from __future__ import annotations

from datetime import date, timedelta

# Mesmo vocabulário de cores da Floresta: verde = no ritmo, amarelo = abaixo,
# vermelho = parado.
VERDE = "green"
AMARELO = "yellow"
VERMELHO = "red"

_JANELA_MEDIA = 7


def _cor(duration_min: int, avg_7d_min: float) -> str:
    if duration_min <= 0:
        return VERMELHO
    if duration_min >= avg_7d_min:
        return VERDE
    return AMARELO


def _streak_atual(dias_ativos: set[date], end_on: date) -> int:
    """Dias consecutivos com sessão, terminando em `end_on`."""
    streak = 0
    dia = end_on
    while dia in dias_ativos:
        streak += 1
        dia -= timedelta(days=1)
    return streak


def _melhor_streak(dias_ativos: set[date]) -> int:
    """Maior sequência de dias consecutivos com sessão em todo o histórico."""
    melhor = 0
    atual = 0
    anterior: date | None = None
    for dia in sorted(dias_ativos):
        atual = atual + 1 if anterior is not None and dia - anterior == timedelta(days=1) else 1
        melhor = max(melhor, atual)
        anterior = dia
    return melhor


def compute_tree(
    by_date: dict[date, tuple[int, int]],
    end_on: date,
    days: int = 30,
) -> dict:
    """Monta a Árvore de um hábito.

    `by_date` deve conter **todo o histórico** do hábito: é dele que sai tanto o
    *lookback* da média móvel de 7 dias quanto os totais cumulativos.
    """
    dias_ativos = {dia for dia, (_, minutos) in by_date.items() if minutos > 0}

    janela: list[dict] = []
    for offset in range(days - 1, -1, -1):
        dia = end_on - timedelta(days=offset)
        sessoes, minutos = by_date.get(dia, (0, 0))
        ultimos = [by_date.get(dia - timedelta(days=i), (0, 0))[1] for i in range(_JANELA_MEDIA)]
        media = round(sum(ultimos) / _JANELA_MEDIA, 2)
        janela.append(
            {
                "date": dia,
                "sessions": sessoes,
                "duration_min": minutos,
                "avg_7d_min": media,
                "color": _cor(minutos, media),
            }
        )

    total_sessions = sum(sessoes for sessoes, _ in by_date.values())
    total_min = sum(minutos for _, minutos in by_date.values())
    n_ativos = len(dias_ativos)

    summary = {
        "total_sessions": total_sessions,
        "total_min": total_min,
        "total_hours": round(total_min / 60, 1),
        "active_days": n_ativos,
        "current_streak": _streak_atual(dias_ativos, end_on),
        "best_streak": _melhor_streak(dias_ativos),
        "avg_min_per_active_day": round(total_min / n_ativos, 2) if n_ativos else 0.0,
    }

    return {"days": janela, "summary": summary}
