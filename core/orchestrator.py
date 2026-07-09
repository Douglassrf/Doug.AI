"""Torre de Controle — o orquestrador UNICO que une as 4 camadas do Doug.AI.

O problema que isto resolve: o repo tem partes boas espalhadas que nao se
falam. Esta e a decisao explicita de qual e o sistema CANONICO — o nucleo
maduro (training/ + core/) — rodando como UM SO, em execucao continua, cada
ciclo escolhendo a melhor estrategia para o momento.

As 4 camadas (executam em sequencia, todo ciclo):

  CAMADA 1 — PERCEPCAO
    Le candles reais de cada par e detecta o regime atual (tendencia, lateral,
    volatilidade). Sem perceber o cenario, nao ha decisao.

  CAMADA 2 — CONHECIMENTO
    Carrega o Playbook (vantagens comprovadas pelo treino de edge M38) e o
    radar de noticias. E a memoria do que JA funcionou.

  CAMADA 3 — ESTRATEGIA
    Para cada par, olha o regime atual e ESCOLHE a melhor estrategia que o
    Playbook prova ter edge naquele regime. Se nenhuma tem edge comprovado ali,
    a camada ja marca abstencao — nao empurra estrategia no escuro.

  CAMADA 4 — DECISAO & RISCO
    Roda o cerebro de decisao (que ja cruza voto ponderado + gate + expectancy
    + Kelly + noticias + playbook) e aplica as travas. Produz a acao final:
    OPERAR / OBSERVAR / FICAR DE FORA — sempre em paper.

O produto de cada ciclo e um ESTADO UNIFICADO (data/orchestrator_state.json):
por par, o regime, a melhor estrategia do momento, a decisao e o porque. E o
"tudo funcionando como um so" que faltava.

Modo seguro: 100%% paper. Nenhuma ordem real. A execucao real segue o caminho
gated de sempre (graduacao + chave trade-only), nunca por aqui.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.environ.get("DOUG_DATA_DIR", ROOT / "data"))
STATE_PATH = DATA / "orchestrator_state.json"
HISTORY_PATH = DATA / "orchestrator_history.jsonl"


@dataclass
class PairPlan:
    """O plano da Torre de Controle para um par, neste ciclo."""
    pair: str
    regime: str
    best_strategy: str | None   # melhor estrategia do Playbook para este regime
    best_edge: float | None     # win rate comprovado dessa estrategia
    decision: str               # OPERAR / OBSERVAR / FICAR_DE_FORA
    direction: str
    confidence: float | None
    stake_pct: float
    reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "pair": self.pair, "regime": self.regime,
            "best_strategy": self.best_strategy, "best_edge": self.best_edge,
            "decision": self.decision, "direction": self.direction,
            "confidence": self.confidence, "stake_pct": self.stake_pct,
            "reasons": self.reasons,
        }


def _best_strategy_for_regime(pair: str, regime: str, playbook: dict[str, dict[str, Any]]) -> tuple[str | None, float | None]:
    """CAMADA 3: a melhor estrategia com edge comprovado neste par+regime."""
    from training.decision_engine import playbook_edge_for
    edge = playbook_edge_for(pair, regime, playbook)
    if edge:
        return edge.get("strategy_id"), float(edge.get("win_rate", 0))
    # fallback: melhor estrategia do Playbook para este regime em QUALQUER par
    candidatos = [
        e for e in playbook.values() if e.get("scenario") == regime
    ]
    if candidatos:
        top = max(candidatos, key=lambda e: e.get("win_rate", 0))
        return top.get("strategy_id"), float(top.get("win_rate", 0))
    return None, None


def run_orchestration_cycle(
    pairs: tuple[str, ...],
    *,
    candles: int = 120,
    granularity: int = 60,
    verbose: bool = True,
) -> dict[str, Any]:
    """Um ciclo completo das 4 camadas, para todos os pares, como UM SO sistema."""
    from training.backtester import fetch_candles_sync
    from training.decision_engine import decide_pair, load_knowledge, load_playbook
    from training.paper_ledger import equity_snapshot, resolve_pending_positions

    # ANTES de decidir qualquer coisa neste ciclo: resolve posicoes OPERAR de
    # ciclos anteriores cujo horizonte ja passou (training/paper_ledger.py).
    # Sem isto o sistema nunca saberia se um OPERAR passado teria ganhado ou
    # perdido de verdade — nao havia curva de capital nem drawdown agregado.
    def _price_lookup(pair: str) -> float | None:
        series = fetch_candles_sync(pair, count=2, granularity=granularity)
        closes = [c["close"] for c in series if c.get("close")]
        return closes[-1] if closes else None

    resolved_trades = resolve_pending_positions(_price_lookup)

    # CAMADA 2 (uma vez por ciclo): conhecimento compartilhado
    backtest_stats, tick_stats = load_knowledge()
    playbook = load_playbook()

    plans: list[PairPlan] = []
    for pair in pairs:
        # CAMADAS 1 + 4 juntas: o decision_engine ja faz percepcao (candles+regime)
        # e decisao+risco. A Torre adiciona a CAMADA 3 (escolha de estrategia).
        d = decide_pair(
            pair, candles=candles, granularity=granularity,
            backtest_stats=backtest_stats, tick_stats=tick_stats,
        )
        best_strat, best_edge = _best_strategy_for_regime(pair, d.scenario, playbook)

        reasons = list(d.reasons)
        if best_strat:
            reasons.insert(0, f"CAMADA 3 — melhor estrategia p/ {d.scenario}: {best_strat} "
                              f"({best_edge*100:.0f}% comprovado no Playbook).")
        else:
            reasons.insert(0, f"CAMADA 3 — nenhuma estrategia tem edge comprovado em {d.scenario}. Cautela.")

        plans.append(PairPlan(
            pair=pair, regime=d.scenario, best_strategy=best_strat, best_edge=best_edge,
            decision=d.level, direction=d.direction, confidence=d.confidence,
            stake_pct=d.stake_pct, reasons=reasons,
        ))

    operar = [p for p in plans if p.decision == "OPERAR"]
    observar = [p for p in plans if p.decision == "OBSERVAR"]
    fora = [p for p in plans if p.decision == "FICAR_DE_FORA"]
    equity = equity_snapshot()

    state = {
        "ran_at": datetime.now(timezone.utc).isoformat(),
        "mode": "PAPER",
        "pairs_analisados": len(plans),
        "resumo": {"operar": len(operar), "observar": len(observar), "de_fora": len(fora)},
        "playbook_edges": len(playbook),
        "portfolio_risco": {
            "capital_pct": equity.get("equity_pct"),
            "drawdown_pct": equity.get("drawdown_pct"),
            "kill_switch_ativo": equity.get("kill_switch_active"),
            "trades_resolvidos_total": equity.get("resolved_trades"),
            "resolvidos_neste_ciclo": len(resolved_trades),
        },
        "planos": [p.to_dict() for p in plans],
    }
    DATA.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with HISTORY_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "ts": state["ran_at"], "resumo": state["resumo"],
            "portfolio_risco": state["portfolio_risco"],
            "operar": [{"pair": p.pair, "regime": p.regime, "strat": p.best_strategy,
                        "conf": p.confidence, "stake": p.stake_pct} for p in operar],
        }, ensure_ascii=False) + "\n")

    if verbose:
        print(f"[Torre de Controle] {len(plans)} pares · "
              f"OPERAR {len(operar)} | OBSERVAR {len(observar)} | DE FORA {len(fora)} "
              f"· Playbook: {len(playbook)} edges")
        ks = " · 🛑 KILL-SWITCH ATIVO" if equity.get("kill_switch_active") else ""
        print(f"  💰 Capital paper: {equity.get('equity_pct', 100.0):.2f}% · "
              f"drawdown {equity.get('drawdown_pct', 0.0):.2f}% · "
              f"{len(resolved_trades)} resolvidos neste ciclo (total {equity.get('resolved_trades', 0)}){ks}")
        for p in operar:
            print(f"  🟢 OPERAR {p.pair} [{p.regime}] {p.direction.upper()} · "
                  f"{p.best_strategy} {(p.best_edge or 0)*100:.0f}% · conf {(p.confidence or 0)*100:.0f}% · stake {p.stake_pct}%")
        for p in observar:
            print(f"  🟡 OBSERVAR {p.pair} [{p.regime}] · melhor: {p.best_strategy or '—'}")
        if not operar and not observar:
            print("  Nenhuma operacao/observacao — sem edge comprovado no momento. Abstencao e disciplina.")
    return state


def load_state() -> dict[str, Any] | None:
    if not STATE_PATH.exists():
        return None
    try:
        return json.loads(STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
