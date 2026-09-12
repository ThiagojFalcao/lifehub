from datetime import date, timedelta

from app.services.tree import compute_tree

D = date(2026, 9, 12)


def test_dias_da_janela_em_ordem_cronologica():
    out = compute_tree({}, end_on=D, days=3)
    assert [dia["date"] for dia in out["days"]] == [
        date(2026, 9, 10),
        date(2026, 9, 11),
        D,
    ]


def test_quantidade_de_dias_respeitada():
    assert len(compute_tree({}, end_on=D, days=14)["days"]) == 14


def test_dia_sem_sessao_zerado_e_vermelho():
    out = compute_tree({}, end_on=D, days=1)
    assert out["days"][0] == {
        "date": D,
        "sessions": 0,
        "duration_min": 0,
        "avg_7d_min": 0.0,
        "color": "red",
    }


def test_conta_sessoes_e_duracao_do_dia():
    out = compute_tree({D: (2, 90)}, end_on=D, days=1)
    dia = out["days"][0]
    assert dia["sessions"] == 2
    assert dia["duration_min"] == 90


def test_media_movel_7d_de_duracao():
    by_date = {D - timedelta(days=i): (1, 70) for i in range(7)}
    out = compute_tree(by_date, end_on=D, days=1)
    assert out["days"][0]["avg_7d_min"] == 70.0


def test_media_movel_usa_dias_anteriores_a_janela():
    by_date = {D - timedelta(days=i): (1, 60) for i in range(1, 7)}
    by_date[D] = (1, 100)
    out = compute_tree(by_date, end_on=D, days=1)
    # 100 + 6*60 = 460 -> 460/7 = 65.71 (sem o lookback seria 100/7 = 14.29)
    assert out["days"][0]["avg_7d_min"] == 65.71


def test_cor_verde_quando_atinge_a_media():
    out = compute_tree({D: (1, 100)}, end_on=D, days=1)
    assert out["days"][0]["color"] == "green"


def test_cor_amarela_quando_abaixo_da_media_mas_ativo():
    by_date = {D - timedelta(days=i): (1, 60) for i in range(1, 7)}
    by_date[D] = (1, 10)
    out = compute_tree(by_date, end_on=D, days=1)
    assert out["days"][0]["avg_7d_min"] == 52.86
    assert out["days"][0]["color"] == "yellow"


def test_cor_vermelha_quando_zero():
    by_date = {D - timedelta(days=i): (1, 60) for i in range(1, 7)}
    out = compute_tree(by_date, end_on=D, days=1)
    assert out["days"][0]["color"] == "red"


def test_summary_soma_total_do_historico():
    by_date = {D: (2, 40), D - timedelta(days=1): (1, 50)}
    summary = compute_tree(by_date, end_on=D, days=1)["summary"]
    assert summary["total_sessions"] == 3
    assert summary["total_min"] == 90
    assert summary["total_hours"] == 1.5


def test_summary_ignora_a_janela_para_os_totais():
    by_date = {D - timedelta(days=200): (1, 60)}
    summary = compute_tree(by_date, end_on=D, days=1)["summary"]
    assert summary["total_min"] == 60
    assert summary["active_days"] == 1


def test_summary_conta_dias_ativos():
    by_date = {D: (2, 40), D - timedelta(days=1): (1, 50), D - timedelta(days=5): (1, 30)}
    summary = compute_tree(by_date, end_on=D, days=1)["summary"]
    assert summary["active_days"] == 3


def test_streak_atual_conta_dias_consecutivos_ate_end_on():
    by_date = {D - timedelta(days=i): (1, 30) for i in range(3)}
    summary = compute_tree(by_date, end_on=D, days=7)["summary"]
    assert summary["current_streak"] == 3


def test_streak_atual_e_zero_quando_o_dia_de_hoje_nao_tem_sessao():
    by_date = {D - timedelta(days=i): (1, 30) for i in range(1, 4)}
    summary = compute_tree(by_date, end_on=D, days=7)["summary"]
    assert summary["current_streak"] == 0


def test_streak_atual_nao_atravessa_buraco():
    by_date = {D: (1, 30), D - timedelta(days=1): (1, 30), D - timedelta(days=3): (1, 30)}
    summary = compute_tree(by_date, end_on=D, days=7)["summary"]
    assert summary["current_streak"] == 2


def test_melhor_streak_do_historico():
    by_date = {
        D - timedelta(days=10): (1, 30),
        D - timedelta(days=9): (1, 30),
        D - timedelta(days=8): (1, 30),
        D - timedelta(days=1): (1, 30),
    }
    summary = compute_tree(by_date, end_on=D, days=7)["summary"]
    assert summary["best_streak"] == 3


def test_media_de_minutos_por_dia_ativo():
    by_date = {D: (1, 40), D - timedelta(days=1): (1, 80)}
    summary = compute_tree(by_date, end_on=D, days=7)["summary"]
    assert summary["avg_min_per_active_day"] == 60.0


def test_sem_dados_nao_divide_por_zero():
    summary = compute_tree({}, end_on=D, days=7)["summary"]
    assert summary["avg_min_per_active_day"] == 0.0
    assert summary["total_hours"] == 0.0
    assert summary["best_streak"] == 0


def test_nao_muta_a_entrada():
    by_date = {D: (1, 30)}
    compute_tree(by_date, end_on=D, days=1)
    assert by_date == {D: (1, 30)}
