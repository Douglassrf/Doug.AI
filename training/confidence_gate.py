"""Filtro de confianca — so deixa uma estrategia 'operar' (buy/sell) quando o
historico REAL acumulado daquela combinacao (estrategia + par + cenario) mostra
uma taxa de acerto observada de pelo menos CONFIDENCE_THRESHOLD, com amostra
minima para nao confiar em sorte.

Isso nao inventa numero nenhum: o "grau de confianca" e literalmente o win_rate
ja calculado pelo Leaderboard (training/continuous_trainer.py), a partir de
resultados reais registrados. Se nao ha dado suficiente, ou o historico nao
bate a meta, a decisao vira 'hold' (nao opera) — igual pediu Douglas: so
operar quando tiver ~90% de chance real de acerto, e ficar de fora quando a
chance de perda for alta.
"""
from __future__ import annotations

from typing import Any

CONFIDENCE_THRESHOLD = 0.90  # so opera se o historico real mostrar >=90% de acerto
MIN_SAMPLES_FOR_CONFIDENCE = 30  # amostra minima antes de confiar no numero (evita sorte/ruido)


def confidence_for(bucket_key: str, leaderboard_stats: dict[str, dict[str, Any]]) -> tuple[float | None, int]:
    """Retorna (win_rate_real, n_trades) para uma combinacao estrategia|par|cenario.

    Retorna (None, n) quando ainda nao ha amostra suficiente para confiar no numero
    (n < MIN_SAMPLES_FOR_CONFIDENCE) — nesse caso o chamador deve tratar como
    'ainda nao sei', nao como 'baixa confianca'.
    """
    bucket = leaderboard_stats.get(bucket_key)
    if not bucket:
        return None, 0
    trades = int(bucket.get("trades", 0))
    if trades < MIN_SAMPLES_FOR_CONFIDENCE:
        return None, trades
    return float(bucket.get("win_rate", 0.0)), trades


def gate_decision(
    direction: str,
    bucket_key: str,
    leaderboard_stats: dict[str, dict[str, Any]],
    *,
    threshold: float = CONFIDENCE_THRESHOLD,
    min_samples: int = MIN_SAMPLES_FOR_CONFIDENCE,
) -> dict[str, Any]:
    """Decide se o sinal (buy/sell) deveria ter sido executado como operacao real.

    Retorna dict com:
      would_operate: bool — True somente se historico real >= threshold com amostra suficiente
      reason: "signal_hold" | "insufficient_data" | "below_confidence" | "confidence_ok"
      confidence: float | None — win_rate real observado, ou None se sem amostra
      samples: int — quantos trades reais ja existem nessa combinacao
    """
    if direction == "hold":
        return {"would_operate": False, "reason": "signal_hold", "confidence": None, "samples": 0}

    wr, trades = confidence_for(bucket_key, leaderboard_stats)
    if wr is None:
        return {
            "would_operate": False,
            "reason": "insufficient_data",
            "confidence": None,
            "samples": trades,
        }
    if wr < threshold:
        return {
            "would_operate": False,
            "reason": "below_confidence",
            "confidence": wr,
            "samples": trades,
        }
    return {"would_operate": True, "reason": "confidence_ok", "confidence": wr, "samples": trades}
