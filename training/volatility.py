"""Volatilidade adaptativa (EWMA, estilo RiskMetrics) e deteccao de mudanca de
regime (CUSUM) — leve, sem dependencia de ML, complementa (nao substitui) a
classificacao de cenario existente em training/scenarios.py.

Nota de engenharia: existia uma versao de EWMA numa pasta antiga do projeto
(fase_xvii_predictive_intelligence/missions/mission_271...) com a recursao
aplicada na ORDEM INVERTIDA — isso faz o dado mais ANTIGO pesar mais que o
mais recente, o oposto do que EWMA deveria fazer. Nao foi portada; esta e
uma implementacao correta, com a recursao aplicada em ordem cronologica.
"""
from __future__ import annotations

import math

# lambda=0.94 e o valor classico do RiskMetrics (J.P. Morgan) para dados
# diarios/intraday — decai a influencia de um retorno antigo pela metade a
# cada ~11 observacoes (ln(0.5)/ln(0.94)).
EWMA_LAMBDA = 0.94


def ewma_volatility(returns: list[float], *, lam: float = EWMA_LAMBDA) -> float:
    """Volatilidade EWMA (desvio padrao), dando mais peso a retornos recentes.

    Recursao aplicada em ORDEM CRONOLOGICA (do mais antigo pro mais recente):
    var_t = lam * var_{t-1} + (1-lam) * r_t^2 — cada retorno pesa mais quanto
    mais recente for. Seed = variancia simples de TODA a serie (neutro, nao
    da peso especial a nenhuma observacao especifica so por ser a primeira —
    um seed ingenuo tipo `returns[0]**2` faria o primeiro dado persistir como
    se fosse "a variancia inicial" e decair devagar por lam^n, distorcendo o
    resultado nas primeiras dezenas de observacoes; achado real ao testar
    esta funcao: um choque no INICIO da serie aparecia com vol maior que o
    mesmo choque no FIM, o oposto do que EWMA deveria fazer)."""
    if len(returns) < 2:
        return 0.0
    var = sum(r**2 for r in returns) / len(returns)
    for r in returns:
        var = lam * var + (1 - lam) * r**2
    return math.sqrt(max(var, 0.0))


def cusum_change_points(
    returns: list[float],
    *,
    threshold: float | None = None,
    drift: float = 0.0,
) -> list[int]:
    """CUSUM (soma cumulativa) para deteccao de mudanca de regime na media dos
    retornos — mais rapido pra perceber uma quebra de tendencia/volatilidade
    do que esperar uma janela fixa "rolar" inteira (o que scenarios.py faz
    hoje). Retorna os indices onde um alarme de mudanca disparou.

    `threshold` default = 5x o desvio padrao dos retornos (regra pratica
    comum p/ CUSUM em series financeiras ruidosas — evita alarme falso em
    ruido normal). `drift` e a tolerancia de deriva esperada (0 = detecta
    qualquer desvio persistente da media movel)."""
    if len(returns) < 10:
        return []
    if threshold is None:
        mean = sum(returns) / len(returns)
        var = sum((r - mean) ** 2 for r in returns) / len(returns)
        std = math.sqrt(var)
        # Piso minimo: com std proximo de zero por ruido de ponto flutuante
        # (ex.: serie geometrica "perfeita", sem ruido real), um threshold
        # baseado so em "std > 0" fica infinitesimal e dispara alarme falso
        # a qualquer desvio de arredondamento. 1e-8 e bem abaixo de qualquer
        # volatilidade financeira real, entao so pega o caso degenerado.
        threshold = 5 * std if std > 1e-8 else 0.01

    change_points: list[int] = []
    s_pos = s_neg = 0.0
    mean = sum(returns) / len(returns)
    for i, r in enumerate(returns):
        deviation = r - mean - drift
        s_pos = max(0.0, s_pos + deviation)
        s_neg = min(0.0, s_neg + deviation)
        if s_pos > threshold or -s_neg > threshold:
            change_points.append(i)
            s_pos = s_neg = 0.0  # reseta apos alarme, senao dispara toda hora
    return change_points


def regime_shift_alert(prices: list[float]) -> dict[str, float | bool]:
    """Resumo pratico pra usar no ciclo de decisao: houve um ponto de mudanca
    de regime nos ultimos retornos, e qual a volatilidade EWMA atual (pra
    contexto, nao pra substituir o cenario ja classificado por scenarios.py)."""
    if len(prices) < 12:
        return {"shift_detected": False, "ewma_vol": 0.0, "last_change_idx": -1}
    returns = [(prices[i] - prices[i - 1]) / prices[i - 1] if prices[i - 1] else 0.0 for i in range(1, len(prices))]
    points = cusum_change_points(returns)
    # So importa se a mudanca foi RECENTE (nos ultimos 20% da janela) — uma
    # mudanca antiga ja deve ter sido absorvida pela classificacao normal.
    recent_cutoff = len(returns) - max(3, len(returns) // 5)
    recent_shift = any(p >= recent_cutoff for p in points)
    return {
        "shift_detected": recent_shift,
        "ewma_vol": round(ewma_volatility(returns), 6),
        "last_change_idx": points[-1] if points else -1,
    }
