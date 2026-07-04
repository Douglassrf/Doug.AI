#!/usr/bin/env python3
"""Generate sample audit log entries every N seconds (optional demo feed)."""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from dashboard.data_store import append_audit_entry, load_settings  # noqa: E402

ASSETS = ["BTC/USDT", "ETH/USDT", "EUR/USD", "GOLD", "SOL/USDT", "GBP/USD", "XRP/USDT"]
ACTIONS = ["BUY", "SELL", "HOLD"]
RED_TEAM = ["PASS", "REDUCE", "BLOCK", "—", "—", "—"]


def generate_once(mode: str = "PAPER") -> None:
    rng = random.Random()
    action = rng.choice(ACTIONS)
    confidence = round(rng.uniform(0.45, 0.92), 2)
    layer_score = int(confidence * 100 + rng.uniform(-10, 10))
    layer_score = max(20, min(98, layer_score))
    rt = rng.choice(RED_TEAM) if action == "BUY" else "—"
    append_audit_entry(
        "trade_decision",
        {
            "asset": rng.choice(ASSETS),
            "action": action,
            "confidence": confidence,
            "mode": mode,
            "red_team": rt,
            "layer_score": layer_score,
            "cycle_id": f"cyc_{rng.randbytes(3).hex()}",
        },
    )
    print(f"[demo] {action} entry appended (layer_score={layer_score})")


def main() -> None:
    parser = argparse.ArgumentParser(description="Doug.AI preflight demo log generator")
    parser.add_argument("--interval", type=int, default=None, help="Seconds between entries")
    parser.add_argument("--once", action="store_true", help="Generate a single entry and exit")
    args = parser.parse_args()

    settings = load_settings()
    interval = args.interval or settings.get("refresh_interval_sec", 30)
    mode = settings.get("mode", "PAPER")

    if args.once:
        generate_once(mode)
        return

    print(f"Generating audit entries every {interval}s (mode={mode}). Ctrl+C to stop.")
    while True:
        generate_once(mode)
        time.sleep(interval)


if __name__ == "__main__":
    main()
