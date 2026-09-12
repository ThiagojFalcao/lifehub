"""Testes da pontuação de XP (Spec 002).

O XP é **derivado** das sessões — nada aqui toca no banco.
"""

from datetime import date

from app.services.skills import (
    TREES,
    _arredonda_half_up,
    compute_skills,
    nivel_de_xp,
    tree_for_category,
    xp_of_session,
)


def test_xp_base_e_um_por_minuto():
    assert xp_of_session(50, floor_plan_used=False, metrics={}, streak_no_dia=1) == 50.0


def test_bonus_floor_plan_e_25_por_cento():
    # 40 * 1.25 = 50
    assert xp_of_session(40, floor_plan_used=True, metrics={}, streak_no_dia=1) == 50.0


def test_bonus_telemetria_rica_por_presenca_de_metrics():
    assert xp_of_session(40, floor_plan_used=False, metrics={"paginas": 20}, streak_no_dia=1) == 50.0


def test_metrics_com_valor_nao_numerico_ainda_pontua():
    # o bônus é pela *presença* de telemetria, não pelo tipo do valor
    assert xp_of_session(40, floor_plan_used=False, metrics={"humor": "bom"}, streak_no_dia=1) == 50.0


def test_metrics_vazio_nao_pontua():
    assert xp_of_session(40, floor_plan_used=False, metrics={}, streak_no_dia=1) == 40.0


def test_bonus_constancia_so_a_partir_do_segundo_dia():
    # streak 4 -> 2 XP * (4-1) = 6
    assert xp_of_session(10, floor_plan_used=False, metrics={}, streak_no_dia=4) == 16.0


def test_bonus_constancia_tem_teto_de_cinco_dias():
    # streak 99 -> 2 XP * 5 = 10 (teto), nunca 196
    assert xp_of_session(10, floor_plan_used=False, metrics={}, streak_no_dia=99) == 20.0


def test_componentes_somam():
    # 30 min com floor plan (37.5) + 10 metrics + 2*(3-1)=4
    assert xp_of_session(30, floor_plan_used=True, metrics={"x": 1}, streak_no_dia=3) == 51.5


def test_arredondamento_half_up_nao_e_banker():
    # round(12.5) em Python dá 12 (half-even); XP precisa dar 13
    assert _arredonda_half_up(12.5) == 13
    assert _arredonda_half_up(0.5) == 1
    assert _arredonda_half_up(50.0) == 50


# --- Curva de nível (Decisão 3) --------------------------------------------


def test_nivel_1_comeca_em_zero():
    assert nivel_de_xp(0) == {
        "level": 1,
        "xp_no_nivel": 0,
        "xp_para_proximo": 100,
        "progresso": 0.0,
    }


def test_limites_de_nivel_sao_fechados():
    assert nivel_de_xp(99)["level"] == 1
    assert nivel_de_xp(100)["level"] == 2
    assert nivel_de_xp(299)["level"] == 2
    assert nivel_de_xp(300)["level"] == 3


def test_curva_triangular():
    assert [nivel_de_xp(x)["level"] for x in (0, 100, 300, 600, 1000, 1500)] == [1, 2, 3, 4, 5, 6]


def test_progresso_dentro_do_nivel():
    n = nivel_de_xp(150)
    assert n["level"] == 2
    assert n["xp_no_nivel"] == 50
    assert n["xp_para_proximo"] == 200
    assert n["progresso"] == 0.25


def test_xp_grande_nao_estoura():
    n = nivel_de_xp(10_000)
    assert n["level"] == 14  # 50*14*13 = 9100 <= 10000 < 50*15*14 = 10500
    assert 0.0 <= n["progresso"] < 1.0


# --- Categoria -> árvore (Decisão 4) ---------------------------------------


def test_arvores_fixas_na_ordem_esperada():
    assert [t["id"] for t in TREES] == ["tech", "exercicio", "hidratacao", "geral"]
    assert [t["name"] for t in TREES] == ["Tech", "Exercício", "Hidratação", "Geral"]


def test_categorias_conhecidas_mapeiam_para_sua_arvore():
    assert tree_for_category("study_tech") == "tech"
    assert tree_for_category("running") == "exercicio"
    assert tree_for_category("gym") == "exercicio"
    assert tree_for_category("water") == "hidratacao"


def test_categoria_desconhecida_cai_em_geral():
    assert tree_for_category("reading") == "geral"
    assert tree_for_category("jardinagem") == "geral"


# --- Agregação (compute_skills) -------------------------------------------


def _habito(id_: int, nome: str, categoria: str) -> dict:
    return {"id": id_, "name": nome, "category": categoria}


def _sessao(
    habit_id: int,
    dia: date,
    minutos: int,
    metrics: dict | None = None,
    floor_plan: bool = False,
) -> dict:
    return {
        "habit_id": habit_id,
        "date": dia,
        "duration_min": minutos,
        "metrics": metrics or {},
        "floor_plan_used": floor_plan,
    }


def _arvore(resultado: dict, tree_id: str) -> dict:
    return next(t for t in resultado["trees"] if t["id"] == tree_id)


def test_banco_vazio_devolve_as_quatro_arvores_no_nivel_1():
    r = compute_skills(habits=[], sessions=[], end_on=date(2026, 9, 12))
    assert r["total_xp"] == 0
    assert r["level"] == 1
    assert len(r["trees"]) == 4
    assert all(t["xp"] == 0 and t["level"] == 1 and t["habits"] == [] for t in r["trees"])


def test_xp_de_habito_sem_sessao_e_zero_mas_ele_aparece():
    habitos = [_habito(1, "Ler", "reading")]
    r = compute_skills(habits=habitos, sessions=[], end_on=date(2026, 9, 12))
    geral = _arvore(r, "geral")
    assert geral["habits"] == [
        {"id": 1, "name": "Ler", "xp": 0, "level": 1, "xp_no_nivel": 0, "xp_para_proximo": 100, "progresso": 0.0}
    ]


def test_xp_agrega_por_arvore_e_chega_ao_total():
    habitos = [_habito(1, "Estudar", "study_tech"), _habito(2, "Correr", "running")]
    sessoes = [
        _sessao(1, date(2026, 9, 11), 50),
        _sessao(1, date(2026, 9, 12), 50),
        _sessao(2, date(2026, 9, 12), 30),
    ]
    r = compute_skills(habits=habitos, sessions=sessoes, end_on=date(2026, 9, 12))
    tech = _arvore(r, "tech")
    assert tech["xp"] == 102  # 50 + (50 + bônus de constância 2)
    assert tech["level"] == 2
    assert tech["habits"][0]["xp"] == 102
    assert _arvore(r, "exercicio")["xp"] == 30
    assert r["total_xp"] == 132


def test_streak_usa_o_historico_do_proprio_habito():
    habitos = [_habito(1, "Hidratar", "water")]
    sessoes = [
        _sessao(1, date(2026, 9, 10), 10),
        _sessao(1, date(2026, 9, 11), 10),
        _sessao(1, date(2026, 9, 12), 10),
    ]
    r = compute_skills(habits=habitos, sessions=sessoes, end_on=date(2026, 9, 12))
    # 10 + (10 + 2*1) + (10 + 2*2) = 36
    assert _arvore(r, "hidratacao")["xp"] == 36


def test_end_on_limita_o_calculo():
    habitos = [_habito(1, "Estudar", "study_tech")]
    sessoes = [_sessao(1, date(2026, 9, 12), 50), _sessao(1, date(2026, 9, 20), 999)]
    r = compute_skills(habits=habitos, sessions=sessoes, end_on=date(2026, 9, 12))
    assert r["total_xp"] == 50


def test_breakdown_explica_de_onde_veio_o_xp():
    habitos = [_habito(1, "Estudar", "study_tech")]
    sessoes = [
        _sessao(1, date(2026, 9, 10), 20),
        _sessao(1, date(2026, 9, 11), 20),
        _sessao(1, date(2026, 9, 12), 40, metrics={"paginas": 30}, floor_plan=True),
    ]
    r = compute_skills(habits=habitos, sessions=sessoes, end_on=date(2026, 9, 12))
    tech = _arvore(r, "tech")
    # streak 1,2,3 -> 0 + 2 + 4 de constância
    assert tech["breakdown"] == {"base": 80, "floor_plan": 10, "metrics": 10, "streak": 6}
    assert tech["xp"] == 106
    assert sum(tech["breakdown"].values()) == tech["xp"]


def test_arredondamento_half_up_acontece_no_total_do_habito():
    habitos = [_habito(1, "Correr", "running")]
    sessoes = [_sessao(1, date(2026, 9, 10 + i), 10, floor_plan=True) for i in range(3)]
    r = compute_skills(habits=habitos, sessions=sessoes, end_on=date(2026, 9, 12))
    # 3 x 12.5 = 37.5 de base + 6 de constância = 43.5 -> 44
    # (arredondar sessão por sessão daria 13 + 15 + 17 = 45)
    assert _arvore(r, "exercicio")["xp"] == 44


def test_nivel_geral_usa_a_soma_de_todas_as_arvores():
    habitos = [_habito(1, "Estudar", "study_tech"), _habito(2, "Correr", "running")]
    sessoes = [_sessao(1, date(2026, 9, 12), 60), _sessao(2, date(2026, 9, 12), 60)]
    r = compute_skills(habits=habitos, sessions=sessoes, end_on=date(2026, 9, 12))
    assert r["total_xp"] == 120
    assert r["level"] == 2
    assert r["xp_no_nivel"] == 20
    assert r["progresso"] == 0.1
