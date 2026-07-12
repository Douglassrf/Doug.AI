#!/usr/bin/env python3
"""Torre de Controle Doug.AI — roda as 4 camadas como UM SO sistema.

  python scripts/doug_orchestrate.py --symbols BOOM1000 R_75 R_25 R_50
  python scripts/doug_orchestrate.py --report
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

from core.orchestrator import load_state, run_orchestration_cycle  # noqa: E402
from integrations.deriv_demo import RealAccountDetectedAbort  # noqa: E402
from training.decision_engine import load_playbook  # noqa: E402
from training.pair_universe import DERIV_PAIRS_100 as ALL_PAIRS  # noqa: E402


def pairs_with_proven_edge() -> tuple[str, ...]:
    """Pares que JA aparecem no Playbook (algum edge comprovado, qualquer nivel).

    Sem isto, a Torre podia ficar de olho num par que nunca foi treinado
    (achado real 2026-07-07: monitorava BOOM1000+R_75+R_25+R_50+R_100, mas o
    Playbook so tinha edges em BOOM1000/CRASH500/BOOM500/CRASH1000 — 4 dos 5
    pares nunca tinham chance de dar OPERAR/OBSERVAR)."""
    playbook = load_playbook()
    pairs = sorted({e.get("pair") for e in playbook.values() if e.get("pair")})
    return tuple(pairs)


def main() -> int:
    p = argparse.ArgumentParser(description="Torre de Controle Doug.AI (4 camadas unificadas)")
    p.add_argument("--symbols", nargs="*", default=None, help="Pares especificos")
    p.add_argument("--pairs", type=int, default=6, help="Primeiros N pares do universo (so usado sem Playbook)")
    p.add_argument("--report", action="store_true", help="Mostra o ultimo estado salvo")
    args = p.parse_args()

    if args.report:
        st = load_state()
        if not st:
            print("Nenhum estado ainda. Rode a Torre de Controle primeiro.")
            return 1
        print(f"=== Torre de Controle · ultimo estado ({str(st['ran_at'])[:19].replace('T',' ')} UTC) ===")
        print(f"Pares: {st['pairs_analisados']} · {st['resumo']} · Playbook: {st['playbook_edges']} edges")
        for pl in st["planos"]:
            tag = {"OPERAR":"🟢","OBSERVAR":"🟡","FICAR_DE_FORA":"⚪"}.get(pl["decision"],"?")
            print(f"  {tag} {pl['pair']} [{pl['regime']}] · melhor: {pl['best_strategy'] or '—'} · {pl['decision']}")
        return 0

    if args.symbols:
        symbols = tuple(args.symbols)
    else:
        symbols = pairs_with_proven_edge()
        if not symbols:
            # Playbook ainda vazio (nunca rodou o treino de edge) — usa o
            # universo padrao so como fallback, nao como escolha informada.
            symbols = tuple(ALL_PAIRS[: max(1, args.pairs)])
            print("Aviso: Playbook vazio — monitorando universo padrao (sem edge comprovado ainda).")
        else:
            print(f"Monitorando {len(symbols)} pares com edge comprovado no Playbook: {', '.join(symbols)}")

    print("=== Doug.AI · Torre de Controle (4 camadas · paper) ===")
    run_orchestration_cycle(symbols)
    print("Estado unificado salvo em data/orchestrator_state.json")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RealAccountDetectedAbort as exc:
        print(f"\n🛑 ABORT DE SEGURANCA — processo interrompido: {exc}\n")
        raise SystemExit(1)
