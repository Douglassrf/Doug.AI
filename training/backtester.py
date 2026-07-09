"""Missao 38 — Backtest walk-forward com candles REAIS da Deriv.

Diferenca em relacao ao treino por tick (continuous_trainer):

- Busca N candles reais de uma vez (1 chamada de rede) e extrai CENTENAS de
  trades de aprendizado por par (walk-forward), em vez de 1 trade por chamada.
- Preve a direcao no horizonte de H candles (minutos), onde existe padrao real,
  em vez do proximo tick (ruido de microestrutura).
- Nunca ha look-ahead: o sinal ve apenas closes[:i]; a saida e closes[i+H-1].
- Alimenta um leaderboard proprio (backtest_leaderboard.json) com win rate E
  expectancy (media do movimento % na direcao operada) por bucket
  estrategia|par|cenario — a base honesta para o gate de confianca decidir
  onde o Doug tem vantagem real e onde deve ficar de fora.

Modo seguro: somente leitura de dados publicos; nenhuma ordem e enviada.
"""
from __future__ import annotations

import asyncio
import json
import os
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import websockets

from integrations.deriv_demo import DEFAULT_APP_ID, _recv_for_req, _ws_url, load_config
from training.confidence_gate import gate_decision
from training.scenarios import detect_scenario
from training.strategies import SIGNAL_FNS, STRATEGIES, evaluate_signal

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
TRAINING_DIR = DATA / "training"
BACKTEST_LEADERBOARD_PATH = TRAINING_DIR / "backtest_leaderboard.json"
BACKTEST_SCORECARD_PATH = TRAINING_DIR / "backtest_scorecard.json"

# Janela minima de historico antes do primeiro sinal (maior exigencia entre as estrategias)
MIN_HISTORY = 20
# Janela usada para classificar o cenario corrente (ultimos N closes)
SCENARIO_WINDOW = 30


@dataclass
class BucketStats:
    strategy_id: str
    pair: str
    scenario: str
    wins: int = 0
    losses: int = 0
    trades: int = 0
    sum_move_pct: float = 0.0  # movimento % na direcao operada (positivo = a favor)
    # Momentos 2o/3o/4o grau do movimento %, em torno de ZERO (nao da media) —
    # permite computar variancia/skew/kurtosis via momentos brutos ao final,
    # sem guardar cada trade individual (custa 3 floats a mais por bucket).
    sum_sq_move_pct: float = 0.0
    sum_cube_move_pct: float = 0.0
    sum_quad_move_pct: float = 0.0

    @property
    def win_rate(self) -> float:
        return self.wins / self.trades if self.trades else 0.0

    @property
    def expectancy_pct(self) -> float:
        """Media do movimento % na direcao operada. >0 = vantagem real."""
        return self.sum_move_pct / self.trades if self.trades else 0.0

    @property
    def variance_pct(self) -> float:
        """Variancia do movimento % (momentos centrais a partir de momentos brutos)."""
        if self.trades < 2:
            return 0.0
        mean = self.expectancy_pct
        m2 = self.sum_sq_move_pct / self.trades - mean**2
        return max(m2, 0.0)

    @property
    def sharpe(self) -> float:
        """Sharpe por trade (nao anualizado): vantagem / dispersao do resultado.

        Duas estrategias podem ter o mesmo expectancy_pct mas uma delas ganha
        pouco quase sempre e perde MUITO raramente (perfil de risco tipico de
        CRASH/BOOM) — o Sharpe captura essa diferenca, expectancy sozinho nao."""
        from training.stats_validation import sharpe_from_moments

        return sharpe_from_moments(self.expectancy_pct, self.variance_pct)

    @property
    def skew(self) -> float:
        from training.stats_validation import skewness_from_moments

        if self.trades < 3:
            return 0.0
        mean = self.expectancy_pct
        m3 = self.sum_cube_move_pct / self.trades - 3 * mean * self.variance_pct - mean**3
        return skewness_from_moments(mean, self.variance_pct, m3)

    @property
    def kurtosis(self) -> float:
        from training.stats_validation import kurtosis_from_moments

        if self.trades < 4 or self.variance_pct <= 0:
            return 3.0
        mean = self.expectancy_pct
        m4 = (
            self.sum_quad_move_pct / self.trades
            - 4 * mean * self.sum_cube_move_pct / self.trades
            + 6 * mean**2 * self.sum_sq_move_pct / self.trades
            - 3 * mean**4
        )
        return kurtosis_from_moments(self.variance_pct, m4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "pair": self.pair,
            "scenario": self.scenario,
            "wins": self.wins,
            "losses": self.losses,
            "trades": self.trades,
            "win_rate": round(self.win_rate, 4),
            "expectancy_pct": round(self.expectancy_pct, 6),
            "sharpe": round(self.sharpe, 4),
            "skew": round(self.skew, 4),
            "kurtosis": round(self.kurtosis, 4),
        }


async def _fetch_candles(symbol: str, count: int, granularity: int) -> list[dict[str, Any]]:
    _, app_id = load_config()
    app_id = app_id or DEFAULT_APP_ID
    async with websockets.connect(_ws_url(app_id, live=False), open_timeout=20) as ws:
        await ws.send(
            json.dumps(
                {
                    "ticks_history": symbol,
                    "count": count,
                    "end": "latest",
                    "style": "candles",
                    "granularity": granularity,
                    "req_id": 1,
                }
            )
        )
        data = await _recv_for_req(ws, 1)
        return [
            {
                "epoch": c.get("epoch"),
                "open": float(c.get("open", 0)),
                "high": float(c.get("high", 0)),
                "low": float(c.get("low", 0)),
                "close": float(c.get("close", 0)),
            }
            for c in data.get("candles", [])
        ]


def fetch_candles_sync(symbol: str, count: int = 500, granularity: int = 60) -> list[dict[str, Any]]:
    """Busca candles reais (publico, sem token). Lista vazia em caso de erro."""
    try:
        return asyncio.run(_fetch_candles(symbol, count, granularity))
    except Exception:
        return []


def walk_forward_pair(
    pair: str,
    closes: list[float],
    *,
    horizon: int = 3,
    stats: dict[str, BucketStats] | None = None,
) -> dict[str, BucketStats]:
    """Replay walk-forward de todas as estrategias sobre uma serie de closes reais.

    Para cada instante i, o sinal enxerga apenas closes[:i] (sem look-ahead);
    a entrada e closes[i-1] e a saida closes[i-1+horizon].
    """
    out = stats if stats is not None else {}
    n = len(closes)
    for i in range(MIN_HISTORY, n - horizon):
        history = closes[:i]
        scenario = detect_scenario(history[-SCENARIO_WINDOW:])
        entry = closes[i - 1]
        exit_price = closes[i - 1 + horizon]
        if not entry:
            continue
        for spec in STRATEGIES:
            fn = SIGNAL_FNS.get(spec.id)
            if fn is None:
                continue
            direction = fn(history)
            won = evaluate_signal(direction, entry, exit_price)
            if won is None:
                continue
            key = f"{spec.id}|{pair}|{scenario}"
            bucket = out.get(key)
            if bucket is None:
                bucket = out[key] = BucketStats(spec.id, pair, scenario)
            bucket.trades += 1
            if won:
                bucket.wins += 1
            else:
                bucket.losses += 1
            move_pct = (exit_price - entry) / entry * 100.0
            signed_move = move_pct if direction == "buy" else -move_pct
            bucket.sum_move_pct += signed_move
            bucket.sum_sq_move_pct += signed_move**2
            bucket.sum_cube_move_pct += signed_move**3
            bucket.sum_quad_move_pct += signed_move**4
    return out


def run_backtest(
    pairs: tuple[str, ...],
    *,
    candles: int = 500,
    granularity: int = 60,
    horizon: int = 3,
) -> dict[str, Any]:
    """Roda o backtest walk-forward para varios pares e salva leaderboard + scorecard."""
    stats: dict[str, BucketStats] = {}
    fetched: list[str] = []
    failed: list[str] = []

    for pair in pairs:
        series = fetch_candles_sync(pair, candles, granularity)
        closes = [c["close"] for c in series if c.get("close")]
        if len(closes) < MIN_HISTORY + horizon + 5:
            failed.append(pair)
            continue
        walk_forward_pair(pair, closes, horizon=horizon, stats=stats)
        fetched.append(pair)

    leaderboard_stats = {k: v.to_dict() for k, v in stats.items()}
    # DSR (Deflated Sharpe Ratio): corrige cada bucket pelo numero TOTAL de
    # combinacoes testadas neste lote (len(stats) buckets = "trials"). Sem
    # isto, testar centenas de combinacoes garante que algumas parecam boas
    # so por coincidencia estatistica (data snooping) — o DSR e a defesa
    # contra isso, adicional ao gate de expectancy/confianca ja existente.
    from training.stats_validation import annotate_with_dsr

    leaderboard_stats = annotate_with_dsr(leaderboard_stats)
    total_trades = sum(v.trades for v in stats.values())
    total_wins = sum(v.wins for v in stats.values())

    # Buckets onde o gate de confianca liberaria operacao (com expectancy positiva)
    approved: list[dict[str, Any]] = []
    for key, bucket in stats.items():
        gate = gate_decision("buy", key, leaderboard_stats)  # direcao generica: avalia o bucket
        if gate["would_operate"] and bucket.expectancy_pct > 0:
            approved.append({**leaderboard_stats[key], "gate": gate["reason"]})
    approved.sort(key=lambda r: (r["win_rate"], r["trades"]), reverse=True)

    ranked = sorted(
        leaderboard_stats.values(),
        key=lambda r: (r["win_rate"], r["trades"]),
        reverse=True,
    )

    summary = {
        "mission": "M38_walk_forward_backtest",
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "params": {"candles": candles, "granularity_sec": granularity, "horizon_candles": horizon},
        "pairs_ok": fetched,
        "pairs_failed": failed,
        "total_learning_trades": total_trades,
        "overall_win_rate": round(total_wins / total_trades, 4) if total_trades else 0.0,
        "buckets": len(stats),
        "gate_approved_buckets": approved[:50],
        "top_buckets": ranked[:20],
    }

    TRAINING_DIR.mkdir(parents=True, exist_ok=True)
    BACKTEST_LEADERBOARD_PATH.write_text(
        json.dumps(
            {"updated_at": summary["ran_at"], "params": summary["params"], "stats": leaderboard_stats},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    BACKTEST_SCORECARD_PATH.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return summary
