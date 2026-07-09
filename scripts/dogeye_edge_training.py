#!/usr/bin/env python3
"""Treino de EDGE REAL — liga o Professor corrigido ao backtester M38.

Diferenca do treino por tick (dogeye_continuous_training):
- O tick preve o PROXIMO tick = cara-ou-coroa (win rate gruda em 50%).
- Aqui o M38 faz walk-forward em candles reais num HORIZONTE de varios candles,
  onde existe PADRAO para aprender. Sai centenas de trades por par de uma vez.

O Professor entao analisa esses resultados com estatistica honesta:
  - PLAYBOOK: combinacoes com >= 80% de acerto e amostra >= 30 (vantagem elite)
  - PROBLEMAS: combinacoes que PERDEM (< 45%) com amostra significativa
  - Ignora o ruido de amostra pequena (o que empesteava o log antigo)

Uso:
  python scripts/dogeye_edge_training.py --pairs 10 --candles 800
  python scripts/dogeye_edge_training.py --report
"""
from __future__ import annotations

import argparse
import io
import json
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

from training.backtester import BACKTEST_LEADERBOARD_PATH, run_backtest  # noqa: E402
from training.coach import PLAYBOOK_PATH, TrainingCoach  # noqa: E402
from training.pair_universe import DERIV_PAIRS_100 as ALL_PAIRS  # noqa: E402


def _load_backtest_stats() -> dict:
    if not BACKTEST_LEADERBOARD_PATH.exists():
        return {}
    try:
        return json.loads(BACKTEST_LEADERBOARD_PATH.read_text(encoding="utf-8")).get("stats", {})
    except (json.JSONDecodeError, OSError):
        return {}


def _print_playbook() -> None:
    if not PLAYBOOK_PATH.exists():
        print("Nenhum playbook ainda. Rode o treino primeiro.")
        return
    data = json.loads(PLAYBOOK_PATH.read_text(encoding="utf-8"))
    edges = data.get("edges", [])
    print(f"\n=== PLAYBOOK — vantagens comprovadas ({data.get('min_trades',30)}+ trades) ===")
    elite = [e for e in edges if e.get("nivel") == "ELITE"]
    bom = [e for e in edges if e.get("nivel") == "BOM"]
    if not edges:
        print("  Nenhuma combinacao >= 60% com amostra suficiente ainda.")
        print("  Isso e HONESTO — o edge aparece acumulando mais dados. Rode mais pares/candles.")
    if elite:
        print("  --- ELITE (>= 80%) — o creme do creme ---")
        for e in elite[:10]:
            print(f"    ⭐ {e['strategy_id']} em {e['scenario']} ({e['pair']}) — {e['win_rate']*100:.0f}% ({e['trades']} trades)")
    if bom:
        print("  --- BOM (60-80%) — ONDE O DINHEIRO REAL ESTA ---")
        for e in bom[:12]:
            print(f"    💰 {e['strategy_id']} em {e['scenario']} ({e['pair']}) — {e['win_rate']*100:.0f}% ({e['trades']} trades)")


def main() -> int:
    p = argparse.ArgumentParser(description="Treino de edge real (M38 + Professor)")
    p.add_argument("--pairs", type=int, default=10, help="Quantos pares usar")
    p.add_argument("--candles", type=int, default=800, help="Candles por par")
    p.add_argument("--granularity", type=int, default=60, help="Segundos por candle")
    p.add_argument("--horizon", type=int, default=3, help="Horizonte de saida em candles")
    p.add_argument("--report", action="store_true", help="So mostra o playbook salvo")
    args = p.parse_args()

    if args.report:
        _print_playbook()
        return 0

    pairs = tuple(ALL_PAIRS[: max(1, args.pairs)])
    print(f"=== Treino de EDGE REAL — {len(pairs)} pares, {args.candles} candles (M38) ===")
    print("Buscando candles reais e rodando walk-forward...")
    summary = run_backtest(pairs, candles=args.candles, granularity=args.granularity, horizon=args.horizon)
    print(f"  {summary['total_learning_trades']} trades de aprendizado gerados em {len(summary['pairs_ok'])} pares.")
    print(f"  Win rate geral (sem filtro): {summary['overall_win_rate']*100:.1f}%")

    # O Professor analisa os resultados REAIS com estatistica honesta
    stats = _load_backtest_stats()
    coach = TrainingCoach()
    lessons = coach.review_cycle(summary["overall_win_rate"], stats)

    problemas = [l for l in lessons if l.kind == "intervention"]
    print(f"\n=== PROFESSOR — analise honesta ({len(stats)} buckets, {len(problemas)} problemas reais) ===")
    if not problemas:
        print("  Nenhuma estrategia PERDE com amostra significativa. Sem ruido, sem falso alarme.")
    for l in problemas[:8]:
        print(f"  ⚠️ {l.message[:120]}")

    _print_playbook()
    print(f"\nPlaybook salvo em: {PLAYBOOK_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
