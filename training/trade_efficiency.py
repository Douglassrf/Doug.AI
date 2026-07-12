"""Eficiencia de saida de trades resolvidos via MFE/MAE (Maximum Favorable/Adverse
Excursion) sobre os candles reais da janela de holding -- nao os campos
fabricados do rascunho original (fase_xvi/mission_262: slippage_bps,
execution_delay_ms, "optimal_price" nao existem num sistema 100% paper sem
corretora real, entao nao sao calculados aqui).

MFE/MAE e um conceito real de analise pos-trade: dado o preco de entrada e o
caminho de precos ate a saida, MFE = o quanto o preco chegou a favorecer a
posicao antes de fechar (oportunidade que passou), MAE = o quanto chegou a
prejudicar (risco que foi tolerado). Um trade "eficiente" fecha perto do MFE;
um trade que aguentou queda evitavel fecha perto do MAE mesmo tendo ganho.
"""
from __future__ import annotations

from datetime import datetime
from typing import Any


def _to_epoch(iso_ts: str) -> int:
    return int(datetime.fromisoformat(iso_ts).timestamp())


def mfe_mae(direction: str, entry: float, path_highs: list[float], path_lows: list[float]) -> dict[str, float]:
    """MFE/MAE em % sobre o preco de entrada, para o LADO realmente operado."""
    if not path_highs or not path_lows or not entry:
        return {"mfe_pct": 0.0, "mae_pct": 0.0}
    if direction == "buy":
        mfe = (max(path_highs) - entry) / entry * 100.0
        mae = (entry - min(path_lows)) / entry * 100.0
    else:  # sell
        mfe = (entry - min(path_lows)) / entry * 100.0
        mae = (max(path_highs) - entry) / entry * 100.0
    return {"mfe_pct": round(max(mfe, 0.0), 6), "mae_pct": round(max(mae, 0.0), 6)}


def exit_efficiency(realized_move_pct: float, mfe_pct: float) -> float:
    """Fracao do movimento favoravel maximo disponivel que o trade realmente
    capturou (0 = nao capturou nada do que era possivel; 1 = saiu no auge do
    movimento). Clampado em [0, 1] -- um resultado negativo (perda) ou sem
    nenhuma excursao favoravel (mfe_pct<=0) nao "captura" nada, por definicao."""
    if mfe_pct <= 0:
        return 0.0
    return round(max(0.0, min(1.0, realized_move_pct / mfe_pct)), 4)


def analyze_trade(
    *,
    direction: str,
    entry: float,
    exit_price: float,
    realized_move_pct: float,
    path_highs: list[float],
    path_lows: list[float],
) -> dict[str, Any]:
    """Analise completa de um trade ja resolvido, com o caminho de precos real
    da janela de holding (path_highs/path_lows dos candles entre abertura e
    fechamento -- ver fetch_trade_path)."""
    excursion = mfe_mae(direction, entry, path_highs, path_lows)
    efficiency = exit_efficiency(realized_move_pct, excursion["mfe_pct"])
    gave_back_pct = round(max(0.0, excursion["mfe_pct"] - realized_move_pct), 6)
    return {
        "direction": direction,
        "entry": entry,
        "exit": exit_price,
        "realized_move_pct": round(realized_move_pct, 6),
        "mfe_pct": excursion["mfe_pct"],
        "mae_pct": excursion["mae_pct"],
        "exit_efficiency": efficiency,
        "gave_back_pct": gave_back_pct,
    }


def fetch_trade_path(
    pair: str, opened_at: str, closed_at: str, *, granularity: int = 60
) -> tuple[list[float], list[float]]:
    """Busca os candles reais entre opened_at e closed_at (via
    training.backtester.fetch_candles_sync com `end` historico) e retorna
    (highs, lows) da janela. Lista vazia se o provedor nao tiver mais o
    historico dessa janela (trades antigos demais) ou em erro de rede -- quem
    chama deve tratar isso como "sem dado", nao como MFE/MAE igual a zero."""
    from training.backtester import fetch_candles_sync

    start_epoch = _to_epoch(opened_at)
    end_epoch = _to_epoch(closed_at)
    duration = max(end_epoch - start_epoch, granularity)
    count = min(max(duration // granularity + 2, 2), 500)
    candles = fetch_candles_sync(pair, count=count, granularity=granularity, end=end_epoch)
    window = [c for c in candles if start_epoch <= c.get("epoch", 0) <= end_epoch + granularity]
    if not window:
        return [], []
    return [c["high"] for c in window], [c["low"] for c in window]
