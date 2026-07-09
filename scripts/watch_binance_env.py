#!/usr/bin/env python3
"""Watch .env for Binance keys — runs test when Douglas pastes them."""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"


def keys_present() -> bool:
    if not ENV.exists():
        return False
    text = ENV.read_text(encoding="utf-8")
    key = secret = ""
    for line in text.splitlines():
        if line.startswith("BINANCE_API_KEY="):
            key = line.split("=", 1)[1].strip().strip('"')
        if line.startswith("BINANCE_API_SECRET="):
            secret = line.split("=", 1)[1].strip().strip('"')
    return bool(key and secret and len(key) > 8 and len(secret) > 8)


def main() -> int:
    print("Aguardando BINANCE_API_KEY + SECRET no .env ...")
    print(f"Arquivo: {ENV}")
    print("Cole as chaves e salve. Ctrl+C para cancelar.\n")

    while True:
        if keys_present():
            print("[OK] Chaves detectadas! Testando...\n")
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "test_binance_testnet.py")],
                cwd=str(ROOT),
                env={**dict(**__import__("os").environ), "PYTHONPATH": str(ROOT)},
            )
            if proc.returncode == 0:
                print("\n[OK] Binance testnet conectada. Iniciando treino aprendiz...")
                subprocess.run(
                    [sys.executable, str(ROOT / "scripts" / "binance_apprentice_training.py"), "--once"],
                    cwd=str(ROOT),
                    env={**dict(**__import__("os").environ), "PYTHONPATH": str(ROOT)},
                )
            return proc.returncode
        time.sleep(2)


if __name__ == "__main__":
    raise SystemExit(main())
