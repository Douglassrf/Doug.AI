#!/usr/bin/env python3
"""DogEye continuous training — run all week, auto-simulate pairs × strategies."""
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

from training.continuous_trainer import (  # noqa: E402
    ALL_PAIRS,
    LEADERBOARD_PATH,
    STATE_PATH,
    run_continuous,
    run_training_cycle,
    Leaderboard,
)
from training.coach import TrainingCoach  # noqa: E402
from training.strategies import STRATEGIES  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="DogEye continuous paper training")
    parser.add_argument("--interval", type=int, default=90, help="Seconds between cycles (default 90)")
    parser.add_argument("--samples", type=int, default=25, help="Simulations per cycle")
    parser.add_argument("--cycles", type=int, default=0, help="Max cycles (0 = infinite / all week)")
    parser.add_argument(
        "--pair-count", type=int, default=0, help="Restrict to first N pairs (0 = all pairs, default)"
    )
    parser.add_argument("--once", action="store_true", help="Single cycle and exit")
    parser.add_argument("--report", action="store_true", help="Print leaderboard summary")
    parser.add_argument("--coach", action="store_true", help="Print professor report (students, wisdom, lessons)")
    args = parser.parse_args()

    if args.coach:
        coach = TrainingCoach()
        rep = coach.report()
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        lessons_path = ROOT / "data" / "training" / "lessons.jsonl"
        if lessons_path.exists():
            lines = lessons_path.read_text(encoding="utf-8").strip().splitlines()
            print("\n=== Ultimas licoes do professor ===")
            for line in lines[-8:]:
                try:
                    obj = json.loads(line)
                    print(f"  [{obj.get('kind')}] {obj.get('message', '')[:150]}")
                except json.JSONDecodeError:
                    pass
        return 0

    if args.report:
        lb = Leaderboard.load()
        if not lb.stats:
            print("Nenhum treino registrado ainda.")
            return 0
        for scenario in ("trending_up", "trending_down", "ranging", "high_volatility", "low_volatility"):
            top = lb.best_for_scenario(scenario, 5)
            if top:
                print(f"\n=== Melhor para {scenario} ===")
                for row in top:
                    print(
                        f"  {row['strategy_id']} + {row['pair']} — "
                        f"WR {row['win_rate']*100:.1f}% ({row['wins']}/{row['trades']})"
                    )
        if STATE_PATH.exists():
            print(f"\nUltimo ciclo: {STATE_PATH}")
        print(f"Leaderboard: {LEADERBOARD_PATH}")
        return 0

    active_pairs = ALL_PAIRS[: args.pair_count] if args.pair_count > 0 else None

    if args.once:
        summary = run_training_cycle(
            pairs=active_pairs, samples_per_cycle=args.samples
        )
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0

    max_cycles = args.cycles if args.cycles > 0 else None
    run_continuous(
        interval_sec=args.interval,
        samples_per_cycle=args.samples,
        max_cycles=max_cycles,
        pairs=active_pairs,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
