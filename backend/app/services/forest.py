from __future__ import annotations

from datetime import date, timedelta


def _color(completed: int, avg_7d: float) -> str:
    if completed == 0:
        return "red"
    if avg_7d <= 0:
        return "green"
    if completed >= avg_7d:
        return "green"
    return "yellow"


def compute_forest(
    completed_by_date: dict[date, int],
    end_on: date,
    days: int = 7,
) -> list[dict]:
    """Um item por dia para os últimos `days` dias (terminando em `end_on`),
    com contagem de completados, média móvel de 7 dias e cor."""
    result: list[dict] = []
    start = end_on - timedelta(days=days - 1)
    for offset in range(days):
        d = start + timedelta(days=offset)
        window = [completed_by_date.get(d - timedelta(days=i), 0) for i in range(7)]
        avg = sum(window) / 7.0
        completed = completed_by_date.get(d, 0)
        result.append(
            {
                "date": d,
                "completed": completed,
                "avg_7d": round(avg, 2),
                "color": _color(completed, avg),
            }
        )
    return result