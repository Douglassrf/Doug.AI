#!/usr/bin/env python3
"""CLI de eficiencia de saida (MFE/MAE) sobre os trades paper ja resolvidos.

Observabilidade pura -- le data/training/paper_trades.jsonl e busca o caminho
real de candles (high/low) da janela de holding de cada trade para avaliar se a
saida em horizonte fixo (180s, ver training/paper_ledger.py) capturou o
essencial do movimento favoravel disponivel ou deixou dinheiro na mesa
(gave_back). Nao entra no caminho de decisao ao vivo -- so leitura e relatorio.

Exemplos:
  python scripts/trade_efficiency_report.py
  python scripts/trade_efficiency_report.py --limit 20
"""
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

from integrations.deriv_demo import RealAccountDetectedAbort  # noqa: E402
from training.paper_ledger import LEDGER_PATH  # noqa: E402
from training.trade_efficiency import analyze_trade, fetch_trade_path  # noqa: E402


def _load_trades(limit: int) -> list[dict]:
    if not LEDGER_PATH.exists():
        return []
    lines = LEDGER_PATH.read_text(encoding="utf-8").strip().splitlines()
    rows = []
    for line in lines[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description="Relatorio de eficiencia de saida (MFE/MAE) dos trades paper")
    parser.add_argument("--limit", type=int, default=50, help="Quantos trades recentes analisar (default 50)")
    args = parser.parse_args()

    trades = _load_trades(args.limit)
    if not trades:
        print("Nenhum trade resolvido ainda em data/training/paper_trades.jsonl.")
        return 0

    print(f"=== Eficiencia de saida — ultimos {len(trades)} trades resolvidos ===\n")
    analyzed = []
    skipped = 0
    for t in trades:
        highs, lows = fetch_trade_path(t["pair"], t["opened_at"], t["closed_at"])
        if not highs:
            skipped += 1
            continue
        report = analyze_trade(
            direction=t["direction"],
            entry=t["entry"],
            exit_price=t["exit"],
            realized_move_pct=t["move_pct"],
            path_highs=highs,
            path_lows=lows,
        )
        report["pair"] = t["pair"]
        report["strategy_id"] = t.get("strategy_id")
        analyzed.append(report)
        print(
            f"  {t['pair']:<10} {t['direction']:<4} {t.get('strategy_id', '?'):<4} "
            f"realized {report['realized_move_pct']:+.4f}% | mfe {report['mfe_pct']:.4f}% | "
            f"eficiencia {report['exit_efficiency']*100:.0f}% | deixou na mesa {report['gave_back_pct']:.4f}%"
        )

    if analyzed:
        avg_eff = sum(r["exit_efficiency"] for r in analyzed) / len(analyzed)
        avg_gave_back = sum(r["gave_back_pct"] for r in analyzed) / len(analyzed)
        print(f"\nMedia de eficiencia de saida: {avg_eff*100:.1f}% | media deixada na mesa: {avg_gave_back:.4f}%")
    if skipped:
        print(f"\n{skipped} trade(s) sem candles historicos disponiveis (fora da janela do provedor) — ignorados.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RealAccountDetectedAbort as exc:
        print(f"\n🛑 ABORT DE SEGURANCA — processo interrompido: {exc}\n")
        raise SystemExit(1)
