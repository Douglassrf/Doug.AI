from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class Evidence:
    id: str = field(default_factory=lambda: f"ev_{uuid.uuid4().hex[:12]}")
    title: str = ""
    source: str = ""
    evidence_type: str = "empirical"
    p_value: float = 1.0
    effect_size: float = 0.0
    sample_size: int = 0
    replication_count: int = 0
    peer_reviewed: bool = False
    tags: List[str] = field(default_factory=list)
    rank_score: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "evidence_type": self.evidence_type,
            "p_value": self.p_value,
            "effect_size": self.effect_size,
            "sample_size": self.sample_size,
            "replication_count": self.replication_count,
            "peer_reviewed": self.peer_reviewed,
            "tags": self.tags,
            "rank_score": self.rank_score,
            "timestamp": self.timestamp.isoformat(),
        }


class ScientificEvidenceRanking:
    """Sistema de ranking de evidências científicas baseado em p-value, efeito, replicação e peer review."""

    def __init__(self) -> None:
        self._evidence_pool: Dict[str, Evidence] = {}

    def add_evidence(
        self,
        title: str,
        source: str,
        p_value: float = 1.0,
        effect_size: float = 0.0,
        sample_size: int = 0,
        replication_count: int = 0,
        peer_reviewed: bool = False,
        evidence_type: str = "empirical",
        tags: Optional[List[str]] = None,
    ) -> Evidence:
        ev = Evidence(
            title=title,
            source=source,
            p_value=p_value,
            effect_size=effect_size,
            sample_size=sample_size,
            replication_count=replication_count,
            peer_reviewed=peer_reviewed,
            evidence_type=evidence_type,
            tags=tags or [],
        )
        ev.rank_score = self._compute_rank(ev)
        self._evidence_pool[ev.id] = ev
        return ev

    def _compute_rank(self, ev: Evidence) -> float:
        # Statistical significance (0-1, lower p = higher score)
        p_score = max(0.0, 1.0 - ev.p_value / 0.05) if ev.p_value <= 0.05 else 0.0

        # Effect size (Cohen's d scale: 0.2 small, 0.5 medium, 0.8 large)
        es_score = min(1.0, abs(ev.effect_size) / 0.8)

        # Sample size (log-scale, 1000 = full score)
        ss_score = min(1.0, np.log1p(ev.sample_size) / np.log1p(1000)) if ev.sample_size > 0 else 0.0

        # Replication
        rep_score = min(1.0, ev.replication_count / 5.0)

        # Peer review bonus
        pr_bonus = 0.2 if ev.peer_reviewed else 0.0

        raw = 0.3 * p_score + 0.25 * es_score + 0.2 * ss_score + 0.2 * rep_score + 0.05 * 1.0
        return min(1.0, raw + pr_bonus)

    def rank_evidence(self, tag_filter: Optional[str] = None) -> List[Evidence]:
        pool = list(self._evidence_pool.values())
        if tag_filter:
            pool = [e for e in pool if tag_filter in e.tags]
        return sorted(pool, key=lambda e: e.rank_score, reverse=True)

    def get_top_evidence(self, n: int = 5, tag_filter: Optional[str] = None) -> List[Evidence]:
        return self.rank_evidence(tag_filter)[:n]

    def compare_evidence(self, ev_id_a: str, ev_id_b: str) -> Dict[str, Any]:
        a = self._evidence_pool.get(ev_id_a)
        b = self._evidence_pool.get(ev_id_b)
        if not a or not b:
            return {"error": "Evidence not found"}
        winner = a if a.rank_score >= b.rank_score else b
        return {
            "evidence_a": a.to_dict(),
            "evidence_b": b.to_dict(),
            "winner_id": winner.id,
            "score_delta": abs(a.rank_score - b.rank_score),
        }

    def get_ranking_summary(self) -> Dict[str, Any]:
        pool = list(self._evidence_pool.values())
        if not pool:
            return {"status": "empty"}
        scores = [e.rank_score for e in pool]
        return {
            "total": len(pool),
            "avg_score": float(np.mean(scores)),
            "top_score": float(np.max(scores)),
            "peer_reviewed_count": sum(1 for e in pool if e.peer_reviewed),
        }
