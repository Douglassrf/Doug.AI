#!/usr/bin/env python3
"""Background worker — refreshes Deriv demo status periodically."""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from integrations.deriv_demo import load_config, run_snapshot

INTERVAL = int(os.environ.get("DERIV_REFRESH_SEC", "60"))


def main() -> None:
    token, app_id = load_config()
    if not token:
        print("[deriv-worker] DERIV_API_TOKEN ausente — worker idle (configure .env)")
        while True:
            time.sleep(INTERVAL)

    print(f"[deriv-worker] Iniciando refresh a cada {INTERVAL}s (app_id={app_id})")
    while True:
        try:
            snap = run_snapshot(token=token, app_id=app_id, log_paper=True)
            if snap.error:
                print(f"[deriv-worker] ⚠ {snap.error}")
            elif snap.account:
                print(
                    f"[deriv-worker] OK {snap.account.loginid} "
                    f"balance={snap.account.balance:.2f} ticks={len(snap.ticks)}"
                )
        except Exception as exc:  # noqa: BLE001 — worker must stay alive
            print(f"[deriv-worker] erro: {exc}")
        time.sleep(INTERVAL)


if __name__ == "__main__":
    main()
