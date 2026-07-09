#!/usr/bin/env python3
"""Guided Binance API setup for apprentices — prints steps, validates .env."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

ENV_PATH = ROOT / ".env"
EXAMPLE = ROOT / ".env.example"


def main() -> int:
    print("=" * 60)
    print("  Doug.AI / Guiai — Binance API para APRENDIZES")
    print("=" * 60)
    print()
    print("O agente NAO pode entrar na sua conta Binance.")
    print("Voce (ou cada aprendiz) cria a chave manualmente — e seguro assim.")
    print()
    print("--- PASSO 1: Testnet (DINHEIRO FALSO — ideal para treinar) ---")
    print("  1. Abra: https://testnet.binance.vision/")
    print("  2. Login com GitHub ou Google")
    print("  3. Clique em 'Generate HMAC_SHA256 Key'")
    print("  4. Copie API Key + Secret (Secret aparece UMA vez)")
    print()
    print("--- PASSO 2: Colar no .env (NUNCA no GitHub) ---")
    print("  copy .env.example .env")
    print("  Edite:")
    print("    BINANCE_USE_TESTNET=true")
    print("    BINANCE_LIVE_ENABLED=false")
    print("    BINANCE_API_KEY=sua_key_testnet")
    print("    BINANCE_API_SECRET=seu_secret_testnet")
    print()
    print("--- PASSO 3: Testar ---")
    print("  python scripts/test_binance_testnet.py")
    print("  python scripts/test_binance_testnet.py --public-only")
    print()
    print("--- Conta REAL Binance (so Douglas, depois, com gate) ---")
    print("  Dashboard: https://www.binance.com/pt-BR/my/dashboard")
    print("  API: https://www.binance.com/pt-BR/my/settings/api-management")
    print("  Permissoes: APENAS 'Leitura' para treino. SEM saque. SEM live ate certificacao.")
    print()
    print("--- Treino aprendizes ---")
    print("  python scripts/binance_apprentice_training.py --once")
    print("  python scripts/dogeye_continuous_training.py --coach")
    print()

    if not ENV_PATH.exists():
        print("[!] .env nao existe. Rode: copy .env.example .env")
        return 1

    text = ENV_PATH.read_text(encoding="utf-8")
    has_key = "BINANCE_API_KEY=" in text and not text.split("BINANCE_API_KEY=")[1].split("\n")[0].strip() in ("", '""')
    if has_key:
        print("[OK] BINANCE_API_KEY encontrada no .env local")
        print("     Rode: python scripts/test_binance_testnet.py")
    else:
        print("[ ] BINANCE_API_KEY ainda vazia — complete o Passo 1 e 2")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
