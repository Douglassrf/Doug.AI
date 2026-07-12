"""Mission 340 — Validated Pattern Registry: knowledge graph de padrões com evidência científica."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class TradingPattern:
    id: str = field(default_factory=lambda: f"tp_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    conditions: Dict[str, Any] = field(default_factory=dict)
    asset_types: List[str] = field(default_factory=list)   # crypto, fx, commodities …
    evidence_score: float = 0.0
    replications: int = 0
    last_pnl: float = 0.0
    avg_pnl: float = 0.0
    confidence: float = 0.0
    status: str = "active"          # active | archived | probation
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_updated: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    pnl_history: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "conditions": self.conditions,
            "asset_types": self.asset_types,
            "evidence_score": round(self.evidence_score, 4),
            "replications": self.replications,
            "last_pnl": round(self.last_pnl, 4),
            "avg_pnl": round(self.avg_pnl, 4),
            "confidence": round(self.confidence, 4),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat(),
        }


class ValidatedPatternRegistry:
    """
    Registra e mantém padrões de trading validados cientificamente.

    confidence = evidence_score × 0.50 + win_rate × 0.30 + replication_score × 0.20
    replication_score = min(1.0, replications / 50)

    Status:
    - active:     confidence ≥ archive_threshold (default 0.60)
    - probation:  recém-criado, aguarda replications ≥ min_replications
    - archived:   confidence < archive_threshold
    """

    def __init__(
        self,
        archive_threshold: float = 0.60,
        min_replications: int = 5,
    ) -> None:
        self._archive_threshold = archive_threshold
        self._min_replications = min_replications
        self._patterns: Dict[str, TradingPattern] = {}

    # ------------------------------------------------------------------ #
    #  CRUD                                                                #
    # ------------------------------------------------------------------ #

    def register(
        self,
        name: str,
        description: str = "",
        conditions: Optional[Dict[str, Any]] = None,
        asset_types: Optional[List[str]] = None,
        initial_evidence: float = 0.0,
    ) -> TradingPattern:
        pattern = TradingPattern(
            name=name,
            description=description,
            conditions=conditions or {},
            asset_types=asset_types or [],
            evidence_score=initial_evidence,
            status="probation",
        )
        self._patterns[pattern.id] = pattern
        return pattern

    def get(self, pattern_id: str) -> Optional[TradingPattern]:
        return self._patterns.get(pattern_id)

    def get_by_name(self, name: str) -> Optional[TradingPattern]:
        for p in self._patterns.values():
            if p.name == name:
                return p
        return None

    # ------------------------------------------------------------------ #
    #  Atualização de evidência                                            #
    # ------------------------------------------------------------------ #

    def record_result(
        self,
        pattern_id: str,
        pnl: float,
        evidence_score: Optional[float] = None,
    ) -> Optional[TradingPattern]:
        p = self._patterns.get(pattern_id)
        if p is None:
            return None

        p.pnl_history.append(pnl)
        p.last_pnl = pnl
        p.replications += 1
        p.avg_pnl = float(np.mean(p.pnl_history))
        p.last_updated = datetime.now(timezone.utc)

        if evidence_score is not None:
            p.evidence_score = float(np.clip(evidence_score, 0.0, 1.0))

        self._recompute_confidence(p)
        self._update_status(p)
        return p

    def _recompute_confidence(self, p: TradingPattern) -> None:
        win_rate = sum(1 for x in p.pnl_history if x > 0) / len(p.pnl_history) if p.pnl_history else 0.0
        rep_score = min(1.0, p.replications / 50.0)
        p.confidence = (
            p.evidence_score * 0.50
            + win_rate * 0.30
            + rep_score * 0.20
        )

    def _update_status(self, p: TradingPattern) -> None:
        if p.replications < self._min_replications:
            p.status = "probation"
        elif p.confidence >= self._archive_threshold:
            p.status = "active"
        else:
            p.status = "archived"

    # ------------------------------------------------------------------ #
    #  Queries                                                             #
    # ------------------------------------------------------------------ #

    def get_active(
        self,
        asset_type: Optional[str] = None,
        min_confidence: float = 0.0,
    ) -> List[TradingPattern]:
        patterns = [p for p in self._patterns.values() if p.status == "active"]
        if asset_type:
            patterns = [p for p in patterns if asset_type in p.asset_types or not p.asset_types]
        patterns = [p for p in patterns if p.confidence >= min_confidence]
        return sorted(patterns, key=lambda p: p.confidence, reverse=True)

    def get_top(self, n: int = 5, asset_type: Optional[str] = None) -> List[TradingPattern]:
        return self.get_active(asset_type=asset_type)[:n]

    def archive_low_confidence(self) -> int:
        archived = 0
        for p in self._patterns.values():
            if p.status == "active" and p.confidence < self._archive_threshold:
                p.status = "archived"
                archived += 1
        return archived

    # ------------------------------------------------------------------ #
    #  Introspection                                                       #
    # ------------------------------------------------------------------ #

    def get_stats(self) -> Dict[str, Any]:
        total = len(self._patterns)
        by_status = {"active": 0, "archived": 0, "probation": 0}
        for p in self._patterns.values():
            by_status[p.status] = by_status.get(p.status, 0) + 1
        active_patterns = [p for p in self._patterns.values() if p.status == "active"]
        avg_confidence = float(np.mean([p.confidence for p in active_patterns])) if active_patterns else 0.0
        return {
            "total": total,
            "by_status": by_status,
            "avg_active_confidence": round(avg_confidence, 4),
        }

    def list_all(self) -> List[Dict[str, Any]]:
        return [p.to_dict() for p in sorted(
            self._patterns.values(), key=lambda p: p.confidence, reverse=True
        )]
