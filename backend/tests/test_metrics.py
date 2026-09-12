import pytest

from app.services.metrics import validate_metrics

SCHEMA = {"focus_minutes": "int", "topic": "str", "focado": "bool", "km": "float"}


def test_schema_vazio_aceita_qualquer_coisa():
    assert validate_metrics({"x": 1}, {}) == {"x": 1}


def test_metrica_livre_e_aceita():
    assert validate_metrics({"hackathon": "sim"}, SCHEMA) == {"hackathon": "sim"}


def test_coerce_string_numerica_para_int():
    assert validate_metrics({"focus_minutes": "60"}, SCHEMA)["focus_minutes"] == 60


def test_coerce_float_inteiro_para_int():
    assert validate_metrics({"focus_minutes": 60.0}, SCHEMA)["focus_minutes"] == 60


def test_coerce_string_para_float():
    assert validate_metrics({"km": "5.2"}, SCHEMA)["km"] == 5.2


def test_coerce_string_booleana():
    assert validate_metrics({"focado": "true"}, SCHEMA)["focado"] is True


def test_coerce_bool_a_partir_de_int():
    assert validate_metrics({"focado": 1}, SCHEMA)["focado"] is True


def test_str_aceita_valor_nao_textual():
    assert validate_metrics({"topic": 42}, SCHEMA)["topic"] == "42"


def test_tipo_invalido_levanta_erro():
    with pytest.raises(ValueError):
        validate_metrics({"focus_minutes": "muito"}, SCHEMA)


def test_float_nao_inteiro_em_int_levanta_erro():
    with pytest.raises(ValueError):
        validate_metrics({"focus_minutes": 60.5}, SCHEMA)


def test_booleano_nao_vira_int():
    with pytest.raises(ValueError):
        validate_metrics({"focus_minutes": True}, SCHEMA)


def test_tipo_declarado_desconhecido_levanta_erro():
    with pytest.raises(ValueError):
        validate_metrics({"x": 1}, {"x": "data"})


def test_nao_muta_o_dicionario_original():
    original = {"focus_minutes": "60"}
    validate_metrics(original, SCHEMA)
    assert original == {"focus_minutes": "60"}


def test_metrica_declarada_ausente_nao_quebra():
    assert validate_metrics({}, SCHEMA) == {}


def test_dict_em_campo_str_levanta_erro():
    with pytest.raises(ValueError):
        validate_metrics({"topic": {"a": 1}}, SCHEMA)


def test_mensagem_de_erro_cita_a_metrica():
    with pytest.raises(ValueError, match="focus_minutes"):
        validate_metrics({"focus_minutes": "muito"}, SCHEMA)
