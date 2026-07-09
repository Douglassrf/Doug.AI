#!/usr/bin/env python3
"""Radar de noticias Doug.AI — busca manchetes reais e salva o snapshot.

  python scripts/fetch_news.py           # busca e mostra o resumo
  python scripts/fetch_news.py --show    # so mostra o snapshot salvo
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from training.news_feed import (  # noqa: E402
    NEWS_SNAPSHOT_PATH,
    fetch_news_snapshot,
    load_news_snapshot,
)


def _print_snapshot(snap: dict) -> None:
    print(f"Snapshot: {str(snap.get('fetched_at', ''))[:19].replace('T', ' ')} UTC")
    print(f"Fontes OK: {snap.get('sources_ok', 0)} | falharam: {snap.get('sources_failed', 0)}\n")
    for topic, s in (snap.get("summary") or {}).items():
        print(
            f"[{topic.upper()}] vies {s.get('bias', 0):+.2f} | risco {s.get('risk', 0):.2f} | "
            f"{s.get('recent_count', 0)} manchetes recentes"
        )
        if s.get("top_headline"):
            print(f"  destaque: {s['top_headline']}")
    print(f"\nSalvo em: {NEWS_SNAPSHOT_PATH}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Radar de noticias Doug.AI")
    parser.add_argument("--show", action="store_true", help="Mostra o snapshot salvo sem buscar")
    args = parser.parse_args()

    if args.show:
        snap = load_news_snapshot(max_age_hours=24 * 365)
        if not snap:
            print("Nenhum snapshot salvo. Rode sem --show para buscar.")
            return 1
        _print_snapshot(snap)
        return 0

    print("Buscando manchetes reais (Google News + CoinDesk)...")
    snap = fetch_news_snapshot(save=True)
    _print_snapshot(snap)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
