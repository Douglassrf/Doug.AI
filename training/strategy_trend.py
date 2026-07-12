"""Deteccao precoce de tendencia de performance por bucket (estrategia+par+
cenario) via regressao linear sobre o historico cronologico real de pnl_pct --
sinal complementar a training/coach.py (TrainingCoach), que so age quando o win
rate ABSOLUTO cai abaixo de LOSING_BAR com amostra minima (MIN_TRADES_FOR_
JUDGMENT=30). Uma inclinacao negativa pode aparecer bem antes disso, enquanto o
nivel absoluto ainda esta na zona "neutra" (0.45-0.65) -- este modulo so cobre
esse angulo de TENDENCIA, sem duplicar o que o Coach ja faz (remedial mode,
broken_combos, wisdom rules, Playbook).

Baseado na ideia de fase_xxi/mission_309 (StrategyLifecycleManager) -- a parte de
regressao linear (np.polyfit) ja era matematica real, mantida aqui. Os 5 estagios
birth/growth/maturity/decline/retired do original viraram um rotulo continuo
simples (declining/stable/improving) sem maquina de estados nem persistencia
propria -- o Coach ja e o dono do estado de cada estrategia (remedial, streaks);
duplicar isso aqui criaria duas fontes de verdade divergentes.
"""
from __future__ import annotations

import numpy as np

# Amostra minima para um ajuste de regressao ser confiavel (abaixo disso, o
# slope oscila por acaso — mesmo principio de MIN_TRADES_FOR_JUDGMENT do Coach,
# so que aplicado a tendencia em vez de nivel absoluto).
MIN_SAMPLES_FOR_TREND = 10
RECENT_WINDOW = 20

# Limiares de inclinacao (pnl_pct por trade, na unidade em que ja e armazenado
# em data/training/paper_trades.jsonl). Nao sao os mesmos numeros do rascunho
# original (que usava outra escala de "performance" generica) -- calibrados
# para pnl_pct real via simulacao contra o historico do projeto.
DECLINE_SLOPE = -0.01
GROWTH_SLOPE = 0.01


def trend_slope(performance_history: list[float]) -> float | None:
    """Inclinacao (regressao linear, np.polyfit grau 1) do historico
    cronologico recente de performance (ex.: pnl_pct por trade, na ordem em que
    aconteceram). None se a amostra for insuficiente para um ajuste confiavel."""
    recent = performance_history[-RECENT_WINDOW:]
    if len(recent) < MIN_SAMPLES_FOR_TREND:
        return None
    x = np.arange(len(recent))
    slope, _ = np.polyfit(x, recent, 1)
    return float(slope)


def trend_label(slope: float | None) -> str:
    if slope is None:
        return "insufficient_data"
    if slope <= DECLINE_SLOPE:
        return "declining"
    if slope >= GROWTH_SLOPE:
        return "improving"
    return "stable"


def bucket_trend(performance_history: list[float]) -> dict[str, object]:
    """Resumo pratico: inclinacao real + rotulo + tamanho da amostra usada."""
    slope = trend_slope(performance_history)
    return {
        "slope": round(slope, 6) if slope is not None else None,
        "label": trend_label(slope),
        "samples": min(len(performance_history), RECENT_WINDOW),
    }
