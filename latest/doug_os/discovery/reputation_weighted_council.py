"""Mission 337 — Reputation-Weighted Council: pondera votos pela reputação em tempo real."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class WeightedVote:
    agent_id: str = ""
    option: str = ""
    raw_confidence: float = 0.0
    reputation_score: float = 1.0
    trend: str = "stable"
    effective_weight: float = 0.0      # reputação × confiança (0 se declining grave)
    zeroed: bool = False               # True se agente foi zerado por declining

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "option": self.option,
            "raw_confidence": round(self.raw_confidence, 3),
            "reputation_score": round(self.reputation_score, 3),
            "trend": self.trend,
            "effective_weight": round(self.effective_weight, 4),
            "zeroed": self.zeroed,
        }


@dataclass
class ReputationCouncilDecision:
    id: str = field(default_factory=lambda: f"rcd_{uuid.uuid4().hex[:12]}")
    topic: str = ""
    votes: List[WeightedVote] = field(default_factory=list)
    decision: str = ""
    confidence: float = 0.0
    active_agents: int = 0
    zeroed_agents: int = 0
    tally: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "votes": [v.to_dict() for v in self.votes],
            "decision": self.decision,
            "confidence": round(self.confidence, 3),
            "active_agents": self.active_agents,
            "zeroed_agents": self.zeroed_agents,
            "tally": {k: round(v, 4) for k, v in self.tally.items()},
            "created_at": self.created_at.isoformat(),
        }


class ReputationWeightedCouncil:
    """
    Conselho onde o peso de cada agente é proporcional à sua reputação atual.

    Regras:
    - Agentes com trend == 'declining' E reputation < declining_zero_threshold
      têm peso zerado até reabilitar
    - effective_weight = reputation_score × raw_confidence
    - Decisão = opção com maior soma de effective_weight
    - Empate: opção mais conservadora (HOLD > SELL > BUY)
    """

    CONSERVATIVE_ORDER = {"HOLD": 0, "SELL": 1, "BUY": 2}

    def __init__(
        self,
        declining_zero_threshold: float = 0.50,
        min_active_agents: int = 2,
    ) -> None:
        self._declining_zero_threshold = declining_zero_threshold
        self._min_active_agents = min_active_agents
        self._agent_reputation: Dict[str, Dict[str, Any]] = {}
        self._decisions: List[ReputationCouncilDecision] = []

    # ------------------------------------------------------------------ #
    #  Reputação                                                           #
    # ------------------------------------------------------------------ #

    def update_reputation(
        self, agent_id: str, score: float, trend: str = "stable"
    ) -> None:
        """Atualiza reputação de um agente. trend: improving | stable | declining"""
        self._agent_reputation[agent_id] = {
            "score": float(np.clip(score, 0.0, 1.0)),
            "trend": trend,
        }

    def get_reputation(self, agent_id: str) -> Dict[str, Any]:
        return self._agent_reputation.get(agent_id, {"score": 1.0, "trend": "stable"})

    # ------------------------------------------------------------------ #
    #  Vote                                                                #
    # ------------------------------------------------------------------ #

    def deliberate(
        self,
        topic: str,
        votes: List[Dict[str, Any]],
    ) -> ReputationCouncilDecision:
        """
        votes: lista de dicts com { agent_id, option, confidence }
        """
        weighted_votes: List[WeightedVote] = []
        tally: Dict[str, float] = {}
        zeroed = 0

        for v in votes:
            agent_id = v.get("agent_id", "unknown")
            option = v.get("option", "HOLD")
            raw_conf = float(v.get("confidence", 0.5))

            rep = self.get_reputation(agent_id)
            rep_score = rep["score"]
            trend = rep["trend"]

            # Zera agentes declining com score muito baixo
            is_zeroed = trend == "declining" and rep_score < self._declining_zero_threshold
            effective = 0.0 if is_zeroed else (rep_score * raw_conf)

            if is_zeroed:
                zeroed += 1

            wv = WeightedVote(
                agent_id=agent_id,
                option=option,
                raw_confidence=raw_conf,
                reputation_score=rep_score,
                trend=trend,
                effective_weight=effective,
                zeroed=is_zeroed,
            )
            weighted_votes.append(wv)

            if not is_zeroed:
                tally[option] = tally.get(option, 0.0) + effective

        active = len(weighted_votes) - zeroed

        # Fallback: se agentes ativos insuficientes → HOLD conservador
        if active < self._min_active_agents or not tally:
            decision_str = "HOLD"
            confidence = 0.0
        else:
            # Decisão: maior peso; empate → mais conservador
            max_weight = max(tally.values())
            winners = [opt for opt, w in tally.items() if abs(w - max_weight) < 1e-9]
            if len(winners) == 1:
                decision_str = winners[0]
            else:
                decision_str = min(winners, key=lambda o: self.CONSERVATIVE_ORDER.get(o, 99))

            total_weight = sum(tally.values())
            confidence = max_weight / total_weight if total_weight > 0 else 0.0

        decision = ReputationCouncilDecision(
            topic=topic,
            votes=weighted_votes,
            decision=decision_str,
            confidence=float(confidence),
            active_agents=active,
            zeroed_agents=zeroed,
            tally=tally,
        )
        self._decisions.append(decision)
        return decision

    # ------------------------------------------------------------------ #
    #  Introspection                                                       #
    # ------------------------------------------------------------------ #

    def get_agent_weights(self) -> Dict[str, float]:
        return {
            aid: rep["score"] if rep["trend"] != "declining" or rep["score"] >= self._declining_zero_threshold
            else 0.0
            for aid, rep in self._agent_reputation.items()
        }

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._decisions)
        if total == 0:
            return {"total": 0, "agents_tracked": len(self._agent_reputation)}
        by_decision = {}
        for d in self._decisions:
            by_decision[d.decision] = by_decision.get(d.decision, 0) + 1
        avg_zeroed = np.mean([d.zeroed_agents for d in self._decisions])
        return {
            "total": total,
            "by_decision": by_decision,
            "avg_zeroed_per_round": round(float(avg_zeroed), 2),
            "agents_tracked": len(self._agent_reputation),
        }
