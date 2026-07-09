#!/usr/bin/env python3
"""Binance apprentice training — pairs + professor + paper simulation."""
from __future__ import annotations

import argparse
import json
import random
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from integrations.binance_apprentice import APPRENTICE_PAIRS, BinanceApprenticeClient  # noqa: E402
from training.coach import TrainingCoach, SCENARIO_BEST_PRACTICE  # noqa: E402
from training.scenarios import detect_scenario  # noqa: E402
from training.strategies import STRATEGIES, SIGNAL_FNS, evaluate_signal  # noqa: E402

DATA = ROOT / "data" / "training"
BINANCE_LOG = DATA / "binance_apprentice.jsonl"


def run_cycle(samples: int = 15) -> dict:
    client = BinanceApprenticeClient()
    coach = TrainingCoach()
    DATA.mkdir(parents=True, exist_ok=True)

    wins = losses = skipped = 0
    lessons: list[str] = []

    for _ in range(samples):
        symbol = random.choice(APPRENTICE_PAIRS)
        try:
            px = client.price(symbol)
            # Simula historico minimo a partir do preco atual (treino pedagogico)
            jitter = [px * (1 + random.uniform(-0.002, 0.002)) for _ in range(25)]
            jitter.append(px)
            scenario = detect_scenario(jitter)
            strat = random.choice(STRATEGIES)
            if coach.remedial_mode:
                best = SCENARIO_BEST_PRACTICE.get(scenario, ("S09",))
                strat = next((s for s in STRATEGIES if s.id in best), strat)

            direction = SIGNAL_FNS[strat.id](jitter)
            entry, exit_p = jitter[-2], jitter[-1]
            won = evaluate_signal(direction, entry, exit_p)

            row = {
                "ts": datetime.now(timezone.utc).isoformat(),
                "exchange": "binance_testnet",
                "symbol": symbol,
                "price": px,
                "scenario": scenario,
                "strategy": strat.id,
                "direction": direction,
                "won": won,
            }
            with BINANCE_LOG.open("a", encoding="utf-8") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")

            if won is True:
                wins += 1
            elif won is False:
                losses += 1
                les = coach.review_result(
                    strategy_id=strat.id, scenario=scenario, pair=symbol, won=False, direction=direction
                )
                if les:
                    lessons.append(les.message)
            else:
                skipped += 1
        except Exception as exc:
            skipped += 1
            lessons.append(f"Erro {symbol}: {exc}")

    wr = wins / (wins + losses) if (wins + losses) else 0.0
    return {
        "cycle_at": datetime.now(timezone.utc).isoformat(),
        "exchange": "binance",
        "samples": samples,
        "wins": wins,
        "losses": losses,
        "skipped": skipped,
        "win_rate": round(wr, 4),
        "lessons": lessons[-5:],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--samples", type=int, default=15)
    parser.add_argument("--interval", type=int, default=120)
    args = parser.parse_args()

    if args.once:
        print(json.dumps(run_cycle(args.samples), indent=2, ensure_ascii=False))
        return 0

    print("Binance apprentice training — Ctrl+C para parar", flush=True)
    n = 0
    while True:
        n += 1
        summary = run_cycle(args.samples)
        print(
            f"[BNB {n}] W:{summary['wins']} L:{summary['losses']} WR:{summary['win_rate']*100:.1f}%",
            flush=True,
        )
        time.sleep(args.interval)


if __name__ == "__main__":
    raise SystemExit(main())
