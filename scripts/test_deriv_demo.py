#!/usr/bin/env python3
"""Test Deriv demo connection — DEMO accounts only."""
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

from integrations.deriv_demo import (  # noqa: E402
    DEFAULT_SYMBOLS,
    is_doug_demo_mode,
    load_config,
    run_public_demo_snapshot,
    run_snapshot,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Deriv demo WebSocket connection")
    parser.add_argument("--symbols", nargs="+", default=list(DEFAULT_SYMBOLS))
    parser.add_argument("--no-paper-log", action="store_true", help="Skip audit_log paper signals")
    parser.add_argument("--json", action="store_true", help="Print full JSON snapshot")
    parser.add_argument(
        "--public-only",
        action="store_true",
        help="Force public demo (app_id 1089) without token",
    )
    args = parser.parse_args()

    token, app_id = load_config()
    symbols = tuple(args.symbols)
    use_public = args.public_only or (not token and is_doug_demo_mode())

    if not token and not use_public:
        print("[ERRO] DERIV_API_TOKEN nao encontrado.")
        print("   1. Copie .env.example -> .env")
        print("   2. Cole seu token DEMO em DERIV_API_TOKEN")
        print("   3. Ou defina DOUG_MODE=demo para ticks publicos (app_id 1089)")
        print("   4. Rode: python scripts/setup_deriv_api.py")
        return 1

    if use_public and not token:
        print(f"[Demo publico] app_id={app_id} (sem token, DOUG_MODE=demo)")
        snap = run_public_demo_snapshot(
            app_id=app_id,
            symbols=symbols,
            log_paper=not args.no_paper_log,
        )
    else:
        print(f"Conectando Deriv demo (app_id={app_id})...")
        snap = run_snapshot(
            token=token,
            app_id=app_id,
            symbols=symbols,
            log_paper=not args.no_paper_log,
        )

    if args.json:
        print(json.dumps(snap.to_dict(), indent=2, ensure_ascii=False))
    else:
        if snap.error:
            print(f"[ERRO] {snap.error}")
            return 2
        acct = snap.account
        assert acct is not None
        print(f"[OK] Conta DEMO: {acct.loginid} | Saldo: {acct.balance:.2f} {acct.currency}")
        print(f"     Virtual: {acct.is_virtual} | Verificado: {snap.checked_at}")
        for sym, tick in snap.ticks.items():
            if "quote" in tick:
                src = tick.get("source", "auth")
                print(f"   Tick {sym}: {tick['quote']} ({src})")
            else:
                print(f"   Tick {sym}: ERRO — {tick.get('error', '?')}")
        if snap.paper_signals:
            print(f"   Paper signals logged: {len(snap.paper_signals)}")

    if snap.error:
        return 2
    print("[OK] Teste concluido — status salvo em data/deriv_status.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
