from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class AgentVote:
    id: str = field(default_factory=lambda: f"av_{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    option: str = ""
    confidence: float = 0.0
    expertise_weight: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "option": self.option,
            "confidence": self.confidence,
            "expertise_weight": self.expertise_weight,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CouncilDecision:
    id: str = field(default_factory=lambda: f"cd_{uuid.uuid4().hex[:12]}")
    topic: str = ""
    votes: List[AgentVote] = field(default_factory=list)
    decision: str = ""
    confidence: float = 0.0
    consensus_level: float = 0.0
    minority_report: Optional[Dict[str, Any]] = None
    tie_broken: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "votes": [v.to_dict() for v in self.votes],
            "decision": self.decision,
            "confidence": self.confidence,
            "consensus_level": self.consensus_level,
            "minority_report": self.minority_report,
            "tie_broken": self.tie_broken,
            "created_at": self.created_at.isoformat(),
        }


class AgentConsensusCouncil:
    """Conselho de consenso entre agentes — votação ponderada, tie-break, minority report."""

    def __init__(self, consensus_threshold: float = 0.6) -> None:
        self._votes: Dict[str, List[AgentVote]] = {}
        self._decisions: List[CouncilDecision] = []
        self._agent_expertise: Dict[str, float] = {}
        self._consensus_threshold = consensus_threshold

    def register_agent_expertise(self, agent_id: str, expertise: float) -> None:
        self._agent_expertise[agent_id] = min(max(expertise, 0.0), 1.0)

    def vote(
        self,
        topic: str,
        agent_id: str,
        option: str,
        confidence: float = 0.8,
    ) -> AgentVote:
        expertise = self._agent_expertise.get(agent_id, 0.5)
        vote = AgentVote(agent_id=agent_id, option=option, confidence=confidence, expertise_weight=expertise)
        self._votes.setdefault(topic, []).append(vote)
        return vote

    def finalize_decision(self, topic: str) -> CouncilDecision:
        votes = self._votes.get(topic, [])
        if not votes:
            return CouncilDecision(topic=topic, decision="no_consensus", confidence=0.0, consensus_level=0.0)

        weighted_votes: Dict[str, float] = {}
        total_weight = 0.0
        for vote in votes:
            weight = vote.expertise_weight * vote.confidence
            weighted_votes[vote.option] = weighted_votes.get(vote.option, 0.0) + weight
            total_weight += weight

        if not weighted_votes:
            return CouncilDecision(topic=topic, decision="no_consensus", confidence=0.0, consensus_level=0.0)

        decision = max(weighted_votes, key=lambda k: weighted_votes[k])
        confidence = weighted_votes[decision] / total_weight if total_weight > 0 else 0.0

        n_options = len(weighted_votes)
        consensus_level = 1.0 - (n_options - 1) / max(n_options, 1)

        minority_report: Optional[Dict[str, Any]] = None
        if n_options > 1:
            minority_opts = {o: w for o, w in weighted_votes.items() if o != decision}
            minority_total = sum(minority_opts.values())
            minority_report = {
                "options": minority_opts,
                "total_minority": minority_total,
                "ratio": minority_total / total_weight if total_weight > 0 else 0.0,
            }

        tie_broken = False
        if n_options > 1:
            sorted_scores = sorted(weighted_votes.values(), reverse=True)
            if len(sorted_scores) > 1 and abs(sorted_scores[0] - sorted_scores[1]) < 0.01:
                tie_broken = True
                # Tie-break: highest mean confidence
                decision = max(
                    set(v.option for v in votes),
                    key=lambda x: float(np.mean([v.confidence for v in votes if v.option == x])),
                )

        result = CouncilDecision(
            topic=topic,
            votes=votes,
            decision=decision,
            confidence=confidence,
            consensus_level=max(0.0, min(1.0, consensus_level)),
            minority_report=minority_report,
            tie_broken=tie_broken,
        )
        self._decisions.append(result)
        return result

    def get_council_dashboard(self) -> Dict[str, Any]:
        return {
            "total_decisions": len(self._decisions),
            "avg_confidence": float(np.mean([d.confidence for d in self._decisions])) if self._decisions else 0.0,
            "avg_consensus": float(np.mean([d.consensus_level for d in self._decisions])) if self._decisions else 0.0,
            "tie_breaks": sum(1 for d in self._decisions if d.tie_broken),
            "agent_expertise": self._agent_expertise,
            "recent_decisions": [d.to_dict() for d in self._decisions[-5:]],
        }
