from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np
from enum import Enum


class DecisionLevel(Enum):
    TACTICAL = "tactical"
    STRATEGIC = "strategic"
    EXECUTIVE = "executive"


@dataclass
class ExecutiveDecision:
    id: str = field(default_factory=lambda: f"exec_{uuid.uuid4().hex[:12]}")
    title: str = ""
    description: str = ""
    level: DecisionLevel = DecisionLevel.TACTICAL
    priority: int = 5
    votes: Dict[str, str] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    result: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    timeline_days: int = 0
    resources_required: Dict[str, float] = field(default_factory=dict)
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    executed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "title": self.title, "description": self.description,
            "level": self.level.value, "priority": self.priority,
            "votes": self.votes, "weights": self.weights, "result": self.result,
            "confidence": self.confidence, "reasoning": self.reasoning,
            "timeline_days": self.timeline_days, "resources_required": self.resources_required,
            "status": self.status, "created_at": self.created_at.isoformat(),
            "executed_at": self.executed_at.isoformat() if self.executed_at else None,
        }


@dataclass
class ExecutiveScore:
    strategic_score: float = 0.0
    tactical_score: float = 0.0
    executive_score: float = 0.0
    overall_score: float = 0.0
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "strategic_score": self.strategic_score, "tactical_score": self.tactical_score,
            "executive_score": self.executive_score, "overall_score": self.overall_score,
            "recommendations": self.recommendations, "created_at": self.created_at.isoformat(),
        }


class ExecutiveCouncilIntelligence:
    _MEMBERS = ["ceo", "cfo", "cmo", "cto", "cso"]

    def __init__(self):
        self._decisions: List[ExecutiveDecision] = []
        self._member_weights: Dict[str, float] = {m: 1.0 for m in self._MEMBERS}

    def propose_decision(self, title: str, description: str,
                         level: DecisionLevel = DecisionLevel.TACTICAL,
                         priority: int = 5, timeline_days: int = 0,
                         resources_required: Optional[Dict[str, float]] = None) -> ExecutiveDecision:
        d = ExecutiveDecision(title=title, description=description, level=level,
                              priority=priority, timeline_days=timeline_days,
                              resources_required=resources_required or {},
                              weights=self._member_weights.copy())
        self._decisions.append(d)
        return d

    def vote(self, decision_id: str, member: str, vote: str, confidence: float = 0.8) -> bool:
        d = self._get_decision(decision_id)
        if not d or member not in self._MEMBERS:
            return False
        d.votes[member] = vote
        d.weights[member] = confidence
        return True

    def finalize_decision(self, decision_id: str) -> Optional[ExecutiveDecision]:
        d = self._get_decision(decision_id)
        if not d:
            return None
        if not d.votes:
            d.status = "rejected"
            d.reasoning = "No votes cast"
            return d
        weighted: Dict[str, float] = {}
        for member, v in d.votes.items():
            weighted[v] = weighted.get(v, 0) + d.weights.get(member, 1.0)
        result = max(weighted, key=weighted.get)
        d.result = result
        total = sum(weighted.values())
        d.confidence = weighted[result] / total if total > 0 else 0.0
        d.status = "approved" if d.confidence >= 0.6 else "rejected"
        d.reasoning = f"Decision {decision_id} {d.status} with {d.confidence:.2f} confidence"
        return d

    def _get_decision(self, decision_id: str) -> Optional[ExecutiveDecision]:
        return next((d for d in self._decisions if d.id == decision_id), None)

    def calculate_score(self) -> ExecutiveScore:
        if not self._decisions:
            return ExecutiveScore(recommendations=["No decisions made. Start proposing decisions."])
        tactical = [d for d in self._decisions if d.level == DecisionLevel.TACTICAL]
        strategic = [d for d in self._decisions if d.level == DecisionLevel.STRATEGIC]
        executive = [d for d in self._decisions if d.level == DecisionLevel.EXECUTIVE]
        ts = self._calculate_level_score(tactical)
        ss = self._calculate_level_score(strategic)
        es = self._calculate_level_score(executive)
        return ExecutiveScore(
            tactical_score=ts, strategic_score=ss, executive_score=es,
            overall_score=ts * 0.3 + ss * 0.3 + es * 0.4,
            recommendations=self._generate_recommendations(ts, ss, es),
        )

    def _calculate_level_score(self, decisions: List[ExecutiveDecision]) -> float:
        if not decisions:
            return 0.0
        success_rate = sum(1 for d in decisions if d.status == "approved") / len(decisions)
        confs = [d.confidence for d in decisions if d.confidence > 0]
        avg_conf = float(np.mean(confs)) if confs else 0.0
        return success_rate * 0.6 + avg_conf * 0.4

    def _generate_recommendations(self, t: float, s: float, e: float) -> List[str]:
        recs = []
        if t < 0.5:
            recs.append("Tactical decisions need improvement. Review execution process.")
        elif t > 0.8:
            recs.append("Tactical decisions performing well.")
        if s < 0.5:
            recs.append("Strategic decisions need more focus. Increase strategic planning.")
        elif s > 0.8:
            recs.append("Strategic decisions are solid.")
        if e < 0.5:
            recs.append("Executive decisions need more oversight and structure.")
        elif e > 0.8:
            recs.append("Executive decisions are well-managed.")
        if not recs:
            recs.append("All decision levels performing adequately.")
        return recs

    def get_priority_queue(self, max_items: int = 10) -> List[ExecutiveDecision]:
        pending = [d for d in self._decisions if d.status == "pending"]
        return sorted(pending, key=lambda x: x.priority, reverse=True)[:max_items]
