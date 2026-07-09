"""Deflated Sharpe Ratio (DSR) — Bailey & Lopez de Prado, "The Deflated Sharpe
Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality"
(Journal of Portfolio Management, 2014).

Por que isto existe: o treino de edge testa ~10 estrategias x dezenas de
pares x 5 cenarios = centenas de combinacoes (buckets). Quanto mais
combinacoes voce testa, maior a chance de um bucket parecer bom so por
coincidencia estatistica (data snooping / selection bias) — mesmo sem
vantagem real nenhuma. O DSR corrige o Sharpe Ratio observado de cada bucket
pelo numero de combinacoes testadas no mesmo lote, penalizando "vantagens"
que sao estatisticamente indistinguiveis de sorte.

DSR e uma probabilidade (0..1): quanto mais proximo de 1, mais confianca de
que o Sharpe observado supera o que se esperaria so por acaso, dado quantos
testes foram feitos. Nao mexe em nenhuma trava de risco existente (Playbook,
gate de confianca) — e uma camada estatistica ADICIONAL.
"""
from __future__ import annotations

import math
from statistics import NormalDist
from typing import Any

_EULER_MASCHERONI = 0.5772156649015329
_NORMAL = NormalDist()


def sharpe_from_moments(mean: float, variance: float) -> float:
    """Sharpe ratio por trade (nao anualizado): media / desvio padrao."""
    std = math.sqrt(variance) if variance > 0 else 0.0
    return mean / std if std > 0 else 0.0


def skewness_from_moments(mean: float, variance: float, m3: float) -> float:
    std = math.sqrt(variance) if variance > 0 else 0.0
    return (m3 / std**3) if std > 0 else 0.0


def kurtosis_from_moments(variance: float, m4: float) -> float:
    """Kurtosis NAO-excedente (normal = 3), como usado na formula original do DSR."""
    return (m4 / variance**2) if variance > 0 else 3.0


def expected_max_sharpe(trials: int, sharpe_std: float) -> float:
    """E[max SR_N] — o maior Sharpe que se esperaria achar so por sorte, testando
    `trials` combinacoes independentes, dado que a variabilidade de estimativa de
    Sharpe entre elas e `sharpe_std` (desvio padrao dos Sharpes observados no lote)."""
    if trials <= 1 or sharpe_std <= 0:
        return 0.0
    n = float(trials)
    z1 = _NORMAL.inv_cdf(max(min(1.0 - 1.0 / n, 1 - 1e-12), 1e-12))
    z2 = _NORMAL.inv_cdf(max(min(1.0 - 1.0 / (n * math.e), 1 - 1e-12), 1e-12))
    return sharpe_std * ((1 - _EULER_MASCHERONI) * z1 + _EULER_MASCHERONI * z2)


def deflated_sharpe_ratio(
    sharpe: float,
    *,
    trials: int,
    sharpe_std: float,
    skew: float,
    kurtosis: float,
    n_obs: int,
) -> float:
    """DSR — probabilidade do Sharpe observado ser real, corrigido pelo numero de
    combinacoes testadas (trials) e pela nao-normalidade dos retornos (skew/kurtosis).

    Retorna 0.0 se nao ha amostra suficiente pra estimar (n_obs <= 1)."""
    if n_obs <= 1:
        return 0.0
    sr0 = expected_max_sharpe(trials, sharpe_std)
    variance_term = 1.0 - skew * sharpe + ((kurtosis - 1.0) / 4.0) * sharpe**2
    if variance_term <= 0:
        variance_term = 1e-9
    se = math.sqrt(variance_term / (n_obs - 1))
    if se <= 0:
        return 0.0
    return _NORMAL.cdf((sharpe - sr0) / se)


def annotate_with_dsr(stats: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """Recebe {key: bucket_dict} (cada um com sharpe/skew/kurtosis/trades ja
    calculados) e devolve os mesmos dicts com 'dsr' adicionado — corrigido pelo
    numero TOTAL de buckets testados neste lote (= trials)."""
    trials = len(stats)
    sharpes = [b["sharpe"] for b in stats.values() if b.get("trades", 0) > 1]
    sharpe_std = (
        (sum((s - sum(sharpes) / len(sharpes)) ** 2 for s in sharpes) / len(sharpes)) ** 0.5
        if len(sharpes) > 1
        else 0.0
    )
    for bucket in stats.values():
        n_obs = bucket.get("trades", 0)
        bucket["dsr"] = round(
            deflated_sharpe_ratio(
                bucket.get("sharpe", 0.0),
                trials=trials,
                sharpe_std=sharpe_std,
                skew=bucket.get("skew", 0.0),
                kurtosis=bucket.get("kurtosis", 3.0),
                n_obs=n_obs,
            ),
            4,
        )
    return stats
