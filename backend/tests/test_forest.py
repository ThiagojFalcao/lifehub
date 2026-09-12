from datetime import date, timedelta

from app.services.forest import _color, compute_forest


def test_color_rules():
    assert _color(2, 4.0) == "yellow"   # positivo mas abaixo da média
    assert _color(3, 2.0) == "green"    # >= média
    assert _color(0, 2.0) == "red"      # nada feito
    assert _color(1, 0.0) == "green"    # sem histórico -> não penalizar


def test_forest_returns_ordered_days_with_colors():
    today = date(2026, 9, 14)
    data = {today - timedelta(days=1): 3}
    days = compute_forest(data, end_on=today, days=7)
    assert len(days) == 7
    assert days[0]["date"] == today - timedelta(days=6)
    assert days[-1]["date"] == today
    assert days[-2]["completed"] == 3
    assert days[-2]["color"] == "green"
    assert days[-1]["completed"] == 0
    assert days[-1]["color"] == "red"


def test_moving_average_window():
    today = date(2026, 9, 14)
    # 1 completado em cada um dos últimos 7 dias
    data = {today - timedelta(days=i): 1 for i in range(7)}
    days = compute_forest(data, end_on=today, days=7)
    assert days[-1]["avg_7d"] == 1.0