"""Mission 342 — Overnight Learning Loop: agrega aprendizado do dia e atualiza pesos para amanhã."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class DaySession:
    """Resumo do dia de trading para o loop de aprendizado."""
    date: str = ""
    total_trades: int = 0
    won_trades: int = 0
    lost_trades: int = 0
    total_pnl: float = 0.0
    agent_outcomes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    patterns_tested: List[str] = field(default_factory=list)
    hypotheses_failed: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def win_rate(self) -> float:
        total = self.won_trades + self.lost_trades
        return self.won_trades / total if total > 0 else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "total_trades": self.total_trades,
            "won_trades": self.won_trades,
            "lost_trades": self.lost_trades,
            "total_pnl": round(self.total_pnl, 4),
            "win_rate": round(self.win_rate, 4),
            "agent_outcomes": self.agent_outcomes,
            "patterns_tested": self.patterns_tested,
            "hypotheses_failed": self.hypotheses_failed,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class LearningReport:
    id: str = field(default_factory=lambda: f"lr_{uuid.uuid4().hex[:12]}")
    session_date: str = ""
    agents_promoted: List[str] = field(default_factory=list)
    agents_penalized: List[str] = field(default_factory=list)
    updated_weights: Dict[str, float] = field(default_factory=dict)
    top_patterns: List[str] = field(default_factory=list)
    experiments_scheduled: int = 0
    strategies_ranked: List[Dict[str, Any]] = field(default_factory=list)
    ready_for_tomorrow: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "session_date": self.session_date,
            "agents_promoted": self.agents_promoted,
            "agents_penalized": self.agents_penalized,
            "updated_weights": {k: round(v, 4) for k, v in self.updated_weights.items()},
            "top_patterns": self.top_patterns,
            "experiments_scheduled": self.experiments_scheduled,
            "strategies_ranked": self.strategies_ranked,
            "ready_for_tomorrow": self.ready_for_tomorrow,
            "created_at": self.created_at.isoformat(),
        }


class OvernightLearningLoop:
    """
    Rodado às 22h após o fechamento do mercado:

    1. Agrega resultados dos agentes do dia (FederatedLearning simulado)
    2. Ranqueia estratégias por evidência científica
    3. Penaliza agentes que erraram, promove os que acertaram (reputação)
    4. Agenda experimentos A/B para hipóteses que falharam
    5. Retorna pesos atualizados prontos para amanhã

    promote_threshold: win_rate mínimo para promoção
    penalize_threshold: win_rate máximo para penalização
    weight_decay: taxa de decaimento dos pesos de agentes sem dados
    """

    def __init__(
        self,
        promote_threshold: float = 0.65,
        penalize_threshold: float = 0.45,
        weight_decay: float = 0.05,
        max_weight: float = 1.0,
        min_weight: float = 0.10,
    ) -> None:
        self._promote_threshold = promote_threshold
        self._penalize_threshold = penalize_threshold
        self._weight_decay = weight_decay
        self._max_weight = max_weight
        self._min_weight = min_weight
        self._agent_weights: Dict[str, float] = {}
        self._strategy_scores: Dict[str, List[float]] = {}
        self._sessions: List[DaySession] = []
        self._reports: List[LearningReport] = []
        self._scheduled_experiments: List[str] = []

    # ------------------------------------------------------------------ #
    #  Session data                                                        #
    # ------------------------------------------------------------------ #

    def record_session(self, session: DaySession) -> None:
        self._sessions.append(session)

    def record_strategy_result(self, strategy_name: str, score: float) -> None:
        self._strategy_scores.setdefault(strategy_name, []).append(score)

    # ------------------------------------------------------------------ #
    #  Overnight run                                                       #
    # ------------------------------------------------------------------ #

    def run_overnight(self, session: DaySession) -> LearningReport:
        """Executa o loop de aprendizado com os dados do dia."""
        self.record_session(session)

        promoted: List[str] = []
        penalized: List[str] = []
        updated_weights: Dict[str, float] = {}

        # ── 1. Atualiza pesos dos agentes ──────────────────────────────
        for agent_id, outcomes in session.agent_outcomes.items():
            current_weight = self._agent_weights.get(agent_id, 0.70)
            agent_wr = float(outcomes.get("win_rate", 0.5))

            if agent_wr >= self._promote_threshold:
                new_weight = min(self._max_weight, current_weight + 0.05)
                promoted.append(agent_id)
            elif agent_wr <= self._penalize_threshold:
                new_weight = max(self._min_weight, current_weight - 0.08)
                penalized.append(agent_id)
            else:
                # neutro: decaimento suave se não tem dados suficientes
                trades = int(outcomes.get("trades", 0))
                new_weight = max(self._min_weight, current_weight - (self._weight_decay if trades < 3 else 0.0))

            self._agent_weights[agent_id] = new_weight
            updated_weights[agent_id] = round(new_weight, 4)

        # ── 2. Ranqueia estratégias ────────────────────────────────────
        ranked = []
        for strat, scores in self._strategy_scores.items():
            avg = float(np.mean(scores))
            ranked.append({"strategy": strat, "avg_score": round(avg, 4), "samples": len(scores)})
        ranked.sort(key=lambda x: x["avg_score"], reverse=True)

        top_patterns = [session.patterns_tested[i] for i in range(min(3, len(session.patterns_tested)))]

        # ── 3. Agenda experimentos para hipóteses que falharam ─────────
        new_experiments = len(session.hypotheses_failed)
        for h in session.hypotheses_failed:
            if h not in self._scheduled_experiments:
                self._scheduled_experiments.append(h)

        # ── 4. Monta relatório ─────────────────────────────────────────
        report = LearningReport(
            session_date=session.date,
            agents_promoted=promoted,
            agents_penalized=penalized,
            updated_weights=updated_weights,
            top_patterns=top_patterns,
            experiments_scheduled=new_experiments,
            strategies_ranked=ranked[:5],
            ready_for_tomorrow=len(self._agent_weights) > 0,
        )
        self._reports.append(report)
        return report

    # ------------------------------------------------------------------ #
    #  Weights access                                                      #
    # ------------------------------------------------------------------ #

    def get_weights_for_tomorrow(self) -> Dict[str, float]:
        return dict(self._agent_weights)

    def get_weight(self, agent_id: str) -> float:
        return self._agent_weights.get(agent_id, 0.70)

    def get_scheduled_experiments(self) -> List[str]:
        return list(self._scheduled_experiments)

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_sessions": len(self._sessions),
            "total_reports": len(self._reports),
            "tracked_agents": len(self._agent_weights),
            "tracked_strategies": len(self._strategy_scores),
            "scheduled_experiments": len(self._scheduled_experiments),
        }

    def get_reports(self, limit: int = 30) -> List[Dict[str, Any]]:
        return [r.to_dict() for r in self._reports[-limit:]]
