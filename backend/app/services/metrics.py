"""Validação e coerção de `metrics` contra o `metrics_schema` de um hábito.

O schema é uma **dica, não uma jaula**: só o tipo declarado e violado gera erro.
Métricas livres (não declaradas) passam — é o "schema evolutivo" do projeto.

A coerção existe porque a fronteira HTTP entrega `str` (inputs HTML) e queremos o
dado persistido já no tipo certo.
"""

from __future__ import annotations

from typing import Any

_TIPOS_SUPORTADOS = ("int", "float", "number", "str", "bool")

_TRUE = {"true", "1", "yes", "sim", "on"}
_FALSE = {"false", "0", "no", "nao", "não", "off"}


class MetricTypeError(ValueError):
    """Tipo de métrica incompatível com o declarado no schema do hábito."""


def _erro(chave: str, declarado: str, valor: Any) -> MetricTypeError:
    return MetricTypeError(
        f"métrica '{chave}': esperado {declarado}, recebido {type(valor).__name__} ({valor!r})"
    )


def _para_int(chave: str, valor: Any) -> int:
    if isinstance(valor, (bool, dict, list)):
        raise _erro(chave, "int", valor)
    if isinstance(valor, int):
        return valor
    if isinstance(valor, float):
        if valor.is_integer():
            return int(valor)
        raise _erro(chave, "int", valor)
    if isinstance(valor, str):
        texto = valor.strip()
        try:
            return int(texto)
        except ValueError:
            try:
                numero = float(texto)
            except ValueError:
                raise _erro(chave, "int", valor) from None
            if numero.is_integer():
                return int(numero)
            raise _erro(chave, "int", valor) from None
    raise _erro(chave, "int", valor)


def _para_float(chave: str, valor: Any) -> float:
    if isinstance(valor, (bool, dict, list)):
        raise _erro(chave, "float", valor)
    if isinstance(valor, (int, float)):
        return float(valor)
    if isinstance(valor, str):
        try:
            return float(valor.strip())
        except ValueError:
            raise _erro(chave, "float", valor) from None
    raise _erro(chave, "float", valor)


def _para_bool(chave: str, valor: Any) -> bool:
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, int) and valor in (0, 1):
        return bool(valor)
    if isinstance(valor, str):
        texto = valor.strip().lower()
        if texto in _TRUE:
            return True
        if texto in _FALSE:
            return False
    raise _erro(chave, "bool", valor)


def _para_str(chave: str, valor: Any) -> str:
    if isinstance(valor, (dict, list)):
        raise _erro(chave, "str", valor)
    return valor if isinstance(valor, str) else str(valor)


_COERCERS = {
    "int": _para_int,
    "float": _para_float,
    "number": _para_float,
    "str": _para_str,
    "bool": _para_bool,
}


def validate_metrics(metrics: dict | None, schema: dict | None) -> dict:
    """Coage `metrics` conforme `schema`.

    Levanta `MetricTypeError` (subclasse de `ValueError`) quando uma métrica
    **declarada** tem tipo incompatível, ou quando o schema declara um tipo
    desconhecido. Não muta a entrada.
    """
    metrics = dict(metrics or {})
    schema = schema or {}
    if not schema:
        return metrics

    for chave, declarado in schema.items():
        if chave not in metrics:
            continue
        if declarado not in _COERCERS:
            raise MetricTypeError(
                f"métrica '{chave}': tipo declarado '{declarado}' não é suportado "
                f"(use um de: {', '.join(_TIPOS_SUPORTADOS)})"
            )
        metrics[chave] = _COERCERS[declarado](chave, metrics[chave])

    return metrics
