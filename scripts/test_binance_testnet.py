#!/usr/bin/env python3
"""Test Binance connection for Doug.AI apprentices (testnet recommended)."""
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

from integrations.binance_apprentice import (  # noqa: E402
    APPRENTICE_PAIRS,
    BinanceApprenticeClient,
    save_binance_status,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test Binance apprentice API")
    parser.add_argument("--symbols", nargs="+", default=list(APPRENTICE_PAIRS[:5]))
    parser.add_argument("--public-only", action="store_true", help="Ping + prices without API keys")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    client = BinanceApprenticeClient()
    st = client.status()
    print(f"Binance Doug.AI | testnet={st['testnet']} | keys={'sim' if st['has_key'] else 'nao'}")

    if args.public_only or not st["has_key"]:
        print("[Publico] ping + precos sem chave API...")
        try:
            client.ping()
            prices = client.prices(tuple(args.symbols))
        except Exception as exc:
            print(f"[ERRO] {exc}")
            return 2
        snap_dict = {
            "connected": True,
            "testnet": st["testnet"],
            "prices": prices,
            "mode": "public",
        }
        if args.json:
            print(json.dumps(snap_dict, indent=2))
        else:
            for sym, px in prices.items():
                print(f"  {sym}: {px}")
        print("[OK] Precos publicos Binance testnet/mainnet")
        return 0

    snap = client.snapshot(tuple(args.symbols))
    save_binance_status(snap)
    if args.json:
        print(json.dumps(snap.to_dict(), indent=2, ensure_ascii=False))
    else:
        if snap.error:
            print(f"[ERRO] {snap.error}")
            return 2
        print(f"[OK] Conectado | testnet={snap.testnet}")
        for sym, px in snap.prices.items():
            print(f"  {sym}: {px}")
        if snap.account:
            balances = [b for b in snap.account.get("balances", []) if float(b.get("free", 0)) > 0]
            print(f"  Saldos testnet com valor: {len(balances)} ativos")
    return 0 if snap.connected else 2


if __name__ == "__main__":
    raise SystemExit(main())
