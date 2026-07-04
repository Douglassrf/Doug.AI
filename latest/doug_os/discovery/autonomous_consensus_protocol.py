from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class ConsensusVote:
    id: str = field(default_factory=lambda: f"cv_{uuid.uuid4().hex[:12]}")
    voter_id: str = ""
    proposal_id: str = ""
    option: str = ""
    confidence: float = 0.0
    risk_score: float = 0.0
    weight: float = 1.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "voter_id": self.voter_id, "proposal_id": self.proposal_id,
            "option": self.option, "confidence": self.confidence,
            "risk_score": self.risk_score, "weight": self.weight,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ConsensusResult:
    id: str = field(default_factory=lambda: f"cr_{uuid.uuid4().hex[:12]}")
    proposal_id: str = ""
    winner: str = ""
    confidence: float = 0.0
    total_votes: int = 0
    votes_distribution: Dict[str, int] = field(default_factory=dict)
    consensus_score: float = 0.0
    tie_break_applied: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "proposal_id": self.proposal_id, "winner": self.winner,
            "confidence": self.confidence, "total_votes": self.total_votes,
            "votes_distribution": self.votes_distribution,
            "consensus_score": self.consensus_score,
            "tie_break_applied": self.tie_break_applied,
            "created_at": self.created_at.isoformat(),
        }


class AutonomousConsensusProtocol:
    def __init__(self):
        self._voters: Dict[str, float] = {}
        self._votes: List[ConsensusVote] = []
        self._results: List[ConsensusResult] = []
        self._proposals: Dict[str, Dict[str, Any]] = {}

    def register_voter(self, voter_id: str, weight: float = 1.0) -> None:
        self._voters[voter_id] = weight

    def propose(self, proposal_id: str, options: List[str], context: Dict[str, Any]) -> None:
        self._proposals[proposal_id] = {
            "options": options, "context": context,
            "created_at": datetime.now(timezone.utc),
        }

    def vote(
        self, proposal_id: str, voter_id: str, option: str,
        confidence: float = 0.8, risk_score: float = 0.2,
    ) -> ConsensusVote:
        if voter_id not in self._voters:
            raise ValueError(f"Voter {voter_id} not registered")
        if proposal_id not in self._proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        v = ConsensusVote(
            voter_id=voter_id, proposal_id=proposal_id, option=option,
            confidence=confidence, risk_score=risk_score, weight=self._voters[voter_id],
        )
        self._votes.append(v)
        return v

    def finalize(self, proposal_id: str) -> ConsensusResult:
        if proposal_id not in self._proposals:
            raise ValueError(f"Proposal {proposal_id} not found")
        proposal_votes = [v for v in self._votes if v.proposal_id == proposal_id]
        if not proposal_votes:
            return ConsensusResult(proposal_id=proposal_id, winner="no_consensus")
        weighted: Dict[str, float] = {}
        total_w = 0.0
        for v in proposal_votes:
            score = v.weight * v.confidence * (1.0 - v.risk_score)
            weighted[v.option] = weighted.get(v.option, 0.0) + score
            total_w += score
        winner = max(weighted, key=weighted.get)
        confidence = weighted[winner] / (total_w + 1e-9)
        n_opts = len(weighted)
        consensus_score = 1.0 - (n_opts - 1) / (n_opts + 1e-9) if n_opts > 1 else 1.0
        tie_break = False
        if n_opts > 1:
            sorted_v = sorted(weighted.values(), reverse=True)
            if abs(sorted_v[0] - sorted_v[1]) < 0.01:
                tie_break = True
                winner = min(
                    [v for v in proposal_votes if v.option in weighted],
                    key=lambda x: x.risk_score,
                ).option
        dist = {}
        for v in proposal_votes:
            dist[v.option] = dist.get(v.option, 0) + 1
        result = ConsensusResult(
            proposal_id=proposal_id, winner=winner, confidence=confidence,
            total_votes=len(proposal_votes), votes_distribution=dist,
            consensus_score=consensus_score, tie_break_applied=tie_break,
        )
        self._results.append(result)
        return result

    def get_consensus_history(self, limit: int = 10) -> List[ConsensusResult]:
        return self._results[-limit:]

    def get_consensus_metrics(self) -> Dict[str, Any]:
        if not self._results:
            return {"status": "no_data"}
        successful = [r for r in self._results if r.winner != "no_consensus"]
        return {
            "total_consensos": len(self._results),
            "successful_consensos": len(successful),
            "success_rate": len(successful) / len(self._results),
            "avg_confidence": float(np.mean([r.confidence for r in self._results])),
            "avg_consensus_score": float(np.mean([r.consensus_score for r in self._results])),
        }
