#!/usr/bin/env python3
"""Missao 38 — CLI do backtest walk-forward com candles reais da Deriv.

Exemplos:
  python scripts/run_backtest.py --pairs 5
  python scripts/run_backtest.py --pairs 10 --candles 800 --granularity 300 --horizon 2
  python scripts/run_backtest.py --report
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from integrations.deriv_demo import RealAccountDetectedAbort  # noqa: E402
from training.backtester import (  # noqa: E402
    BACKTEST_SCORECARD_PATH,
    run_backtest,
)
from training.pair_universe import DERIV_PAIRS_100 as ALL_PAIRS  # noqa: E402


def _print_summary(summary: dict) -> None:
    p = summary["params"]
    print(
        f"\n=== Missao 38 — Backtest walk-forward ===\n"
        f"Candles/par: {p['candles']} x {p['granularity_sec']}s | horizonte: {p['horizon_candles']} candles\n"
        f"Pares OK: {len(summary['pairs_ok'])} | falharam: {len(summary['pairs_failed'])}\n"
        f"Trades de aprendizado: {summary['total_learning_trades']}\n"
        f"Win rate geral (todas estrategias, sem filtro): {summary['overall_win_rate']*100:.1f}%\n"
        f"Buckets avaliados: {summary['buckets']}"
    )

    top = summary.get("top_buckets", [])
    if top:
        print("\n--- TOP buckets (estrategia + par + cenario) ---")
        for row in top[:10]:
            print(
                f"  {row['strategy_id']} + {row['pair']} [{row['scenario']}] — "
                f"WR {row['win_rate']*100:.1f}% | exp {row['expectancy_pct']:+.4f}%/trade | {row['trades']} trades"
            )

    approved = summary.get("gate_approved_buckets", [])
    print(f"\n--- Aprovados pelo gate de confianca (>=90% + amostra minima + expectancy>0): {len(approved)} ---")
    for row in approved[:10]:
        print(
            f"  OPERAVEL: {row['strategy_id']} + {row['pair']} [{row['scenario']}] — "
            f"WR {row['win_rate']*100:.1f}% | exp {row['expectancy_pct']:+.4f}% | {row['trades']} trades"
        )
    if not approved:
        print(
            "  Nenhum bucket atingiu o padrao ainda — o Doug fica em HOLD nesses casos.\n"
            "  Isso e o sistema sendo HONESTO: so opera onde a vantagem for comprovada."
        )
    print(f"\nScorecard salvo em: {BACKTEST_SCORECARD_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Backtest walk-forward Doug.AI (Missao 38)")
    parser.add_argument("--pairs", type=int, default=5, help="Quantos pares do universo usar (default 5)")
    parser.add_argument("--candles", type=int, default=500, help="Candles por par (default 500)")
    parser.add_argument("--granularity", type=int, default=60, help="Segundos por candle (default 60)")
    parser.add_argument("--horizon", type=int, default=3, help="Horizonte de saida em candles (default 3)")
    parser.add_argument("--report", action="store_true", help="Reimprime o ultimo scorecard salvo")
    args = parser.parse_args()

    if args.report:
        if not BACKTEST_SCORECARD_PATH.exists():
            print("Nenhum backtest registrado ainda. Rode sem --report primeiro.")
            return 1
        summary = json.loads(BACKTEST_SCORECARD_PATH.read_text(encoding="utf-8"))
        _print_summary(summary)
        return 0

    pairs = ALL_PAIRS[: max(1, args.pairs)]
    print(f"Buscando {args.candles} candles reais de {len(pairs)} pares na Deriv...")
    summary = run_backtest(
        tuple(pairs),
        candles=args.candles,
        granularity=args.granularity,
        horizon=args.horizon,
    )
    _print_summary(summary)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RealAccountDetectedAbort as exc:
        print(f"\n🛑 ABORT DE SEGURANCA — processo interrompido: {exc}\n")
        raise SystemExit(1)
