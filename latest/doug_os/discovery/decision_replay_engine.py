from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import copy


@dataclass
class DecisionSnapshot:
    id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    decision_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    market_state: Dict[str, Any] = field(default_factory=dict)
    internal_state: Dict[str, Any] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    council_state: Dict[str, Any] = field(default_factory=dict)
    risk_state: Dict[str, Any] = field(default_factory=dict)
    dougbrain_state: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "decision_id": self.decision_id,
            "timestamp": self.timestamp.isoformat(),
            "market_state": self.market_state, "internal_state": self.internal_state,
            "weights": self.weights, "council_state": self.council_state,
            "risk_state": self.risk_state, "dougbrain_state": self.dougbrain_state,
        }


@dataclass
class ReplayResult:
    decision_id: str = ""
    original_result: Dict[str, Any] = field(default_factory=dict)
    replayed_result: Dict[str, Any] = field(default_factory=dict)
    differences: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision_id": self.decision_id, "original_result": self.original_result,
            "replayed_result": self.replayed_result, "differences": self.differences,
            "confidence": self.confidence, "created_at": self.created_at.isoformat(),
        }


class DecisionReplayEngine:
    def __init__(self):
        self._snapshots: Dict[str, DecisionSnapshot] = {}
        self._replays: List[ReplayResult] = []

    def create_snapshot(self, decision_id: str, market_state: Dict, internal_state: Dict,
                        weights: Dict, council_state: Dict, risk_state: Dict,
                        dougbrain_state: Dict) -> DecisionSnapshot:
        snap = DecisionSnapshot(
            decision_id=decision_id,
            market_state=copy.deepcopy(market_state),
            internal_state=copy.deepcopy(internal_state),
            weights=copy.deepcopy(weights),
            council_state=copy.deepcopy(council_state),
            risk_state=copy.deepcopy(risk_state),
            dougbrain_state=copy.deepcopy(dougbrain_state),
        )
        self._snapshots[snap.id] = snap
        return snap

    def get_snapshot(self, snapshot_id: str) -> Optional[DecisionSnapshot]:
        return self._snapshots.get(snapshot_id)

    def replay(self, snapshot_id: str, decision_function: Callable,
               original_result: Optional[Dict] = None, **kwargs) -> ReplayResult:
        snap = self._snapshots.get(snapshot_id)
        if not snap:
            raise ValueError(f"Snapshot {snapshot_id} not found")
        replayed_result = decision_function(
            market_state=copy.deepcopy(snap.market_state),
            internal_state=copy.deepcopy(snap.internal_state),
            weights=copy.deepcopy(snap.weights),
            council_state=copy.deepcopy(snap.council_state),
            risk_state=copy.deepcopy(snap.risk_state),
            dougbrain_state=copy.deepcopy(snap.dougbrain_state),
            **kwargs,
        )
        orig = original_result or {}
        differences = self._compare_results(orig, replayed_result)
        confidence = self._calculate_confidence(differences)
        result = ReplayResult(
            decision_id=snap.decision_id, original_result=orig,
            replayed_result=replayed_result, differences=differences, confidence=confidence,
        )
        self._replays.append(result)
        return result

    def _compare_results(self, original: Dict, replayed: Dict) -> Dict[str, Any]:
        diff = {}
        for key in set(original) | set(replayed):
            if key not in original:
                diff[key] = {"status": "new", "value": replayed[key]}
            elif key not in replayed:
                diff[key] = {"status": "removed", "value": original[key]}
            elif original[key] != replayed[key]:
                diff[key] = {
                    "status": "changed", "original": original[key], "replayed": replayed[key],
                    "diff": abs(original[key] - replayed[key]) if isinstance(original[key], (int, float)) else None,
                }
        return diff

    def _calculate_confidence(self, differences: Dict) -> float:
        if not differences: return 1.0
        return float(max(1.0 - len(differences) * 0.1, 0.0))
