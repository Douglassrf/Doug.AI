#!/usr/bin/env python3
"""Cerebro de Decisao Doug.AI — CLI.

Pergunta ao Doug, AGORA, o que ele faria em cada par (100%% paper):

  python scripts/doug_decide.py --pairs 5
  python scripts/doug_decide.py --symbols R_25 R_50 frxEURUSD
"""
from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
except Exception:
    pass

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from training.decision_engine import decide_many  # noqa: E402
from training.pair_universe import DERIV_PAIRS_100 as ALL_PAIRS  # noqa: E402

LEVEL_TAG = {
    "OPERAR": "[OPERAR ]",
    "OBSERVAR": "[OBSERVA]",
    "FICAR_DE_FORA": "[DE FORA]",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Doug.AI — decisao viva explicada (paper)")
    parser.add_argument("--pairs", type=int, default=5, help="Primeiros N pares do universo (default 5)")
    parser.add_argument("--symbols", nargs="*", default=None, help="Simbolos especificos (ex: R_25 R_50)")
    parser.add_argument("--candles", type=int, default=120, help="Candles de contexto (default 120)")
    parser.add_argument("--granularity", type=int, default=60, help="Segundos por candle (default 60)")
    parser.add_argument("--verbose", action="store_true", help="Mostra o voto de cada estrategia")
    args = parser.parse_args()

    symbols = tuple(args.symbols) if args.symbols else tuple(ALL_PAIRS[: max(1, args.pairs)])
    print(f"Doug.AI pensando em {len(symbols)} pares (paper, dados reais)...\n")

    decisions = decide_many(symbols, candles=args.candles, granularity=args.granularity)

    operar = observar = fora = 0
    for d in decisions:
        tag = LEVEL_TAG.get(d.level, d.level)
        conf = f"{d.confidence*100:.1f}%" if d.confidence is not None else "--"
        stake = f" | stake {d.stake_pct}%" if d.stake_pct else ""
        print(f"{tag} {d.pair} [{d.scenario}] -> {d.direction.upper()} | confianca {conf}{stake}")
        for r in d.reasons:
            print(f"    - {r}")
        if args.verbose:
            for v in d.votes:
                wr = f"{v.win_rate*100:.0f}%" if v.win_rate is not None else "sem historico"
                print(f"      voto {v.strategy_id}: {v.direction} (WR {wr}, {v.trades} trades, peso {v.weight:+.3f})")
        print()
        if d.level == "OPERAR":
            operar += 1
        elif d.level == "OBSERVAR":
            observar += 1
        else:
            fora += 1

    print(
        f"Resumo: OPERAR {operar} | OBSERVAR {observar} | DE FORA {fora} — "
        "abstencao e disciplina, nao fraqueza."
    )
    print("Decisoes registradas em data/training/live_decisions.jsonl (auditavel).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
