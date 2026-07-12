from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class MarketSnapshot:
    id: str = field(default_factory=lambda: f"ms_{uuid.uuid4().hex[:12]}")
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    forex: Dict[str, float] = field(default_factory=dict)
    crypto: Dict[str, float] = field(default_factory=dict)
    commodities: Dict[str, float] = field(default_factory=dict)
    bonds: Dict[str, float] = field(default_factory=dict)
    indices: Dict[str, float] = field(default_factory=dict)
    futures: Dict[str, float] = field(default_factory=dict)
    etfs: Dict[str, float] = field(default_factory=dict)
    macro: Dict[str, float] = field(default_factory=dict)
    correlations: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "forex": self.forex,
            "crypto": self.crypto,
            "commodities": self.commodities,
            "bonds": self.bonds,
            "indices": self.indices,
            "futures": self.futures,
            "etfs": self.etfs,
            "macro": self.macro,
            "correlations": self.correlations,
        }


@dataclass
class GlobalMarketState:
    snapshot_id: str = ""
    global_regime: str = "neutral"
    liquidity_score: float = 0.0
    risk_score: float = 0.0
    momentum_score: float = 0.0
    correlation_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    anomaly_detected: bool = False
    anomaly_description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "snapshot_id": self.snapshot_id,
            "global_regime": self.global_regime,
            "liquidity_score": self.liquidity_score,
            "risk_score": self.risk_score,
            "momentum_score": self.momentum_score,
            "correlation_matrix": self.correlation_matrix,
            "anomaly_detected": self.anomaly_detected,
            "anomaly_description": self.anomaly_description,
            "created_at": self.created_at.isoformat(),
        }


class GlobalMarketSynchronization:
    """Sincronização global de mercados em 8 classes de ativos."""

    _MARKETS = ("forex", "crypto", "commodities", "bonds", "indices", "futures", "etfs", "macro")

    def __init__(self, seed: int = 42) -> None:
        self._rng = np.random.default_rng(seed)
        self._snapshots: List[MarketSnapshot] = []
        self._states: List[GlobalMarketState] = []

    def add_snapshot(self, data: Dict[str, Any]) -> MarketSnapshot:
        snapshot = MarketSnapshot(
            forex=data.get("forex", {}),
            crypto=data.get("crypto", {}),
            commodities=data.get("commodities", {}),
            bonds=data.get("bonds", {}),
            indices=data.get("indices", {}),
            futures=data.get("futures", {}),
            etfs=data.get("etfs", {}),
            macro=data.get("macro", {}),
        )
        snapshot.correlations = self._calculate_correlations(snapshot)
        self._snapshots.append(snapshot)
        return snapshot

    def _calculate_correlations(self, snapshot: MarketSnapshot) -> Dict[str, Dict[str, float]]:
        market_vals: Dict[str, List[float]] = {}
        for m in self._MARKETS:
            d = getattr(snapshot, m, {})
            if d:
                market_vals[m] = list(d.values())

        markets = list(market_vals.keys())
        correlations: Dict[str, Dict[str, float]] = {}

        for i, m1 in enumerate(markets):
            correlations[m1] = {}
            for j, m2 in enumerate(markets):
                if i == j:
                    correlations[m1][m2] = 1.0
                else:
                    v1 = np.array(market_vals[m1])
                    v2 = np.array(market_vals[m2])
                    min_len = min(len(v1), len(v2))
                    if min_len >= 2:
                        corr = float(np.corrcoef(v1[:min_len], v2[:min_len])[0, 1])
                        if np.isnan(corr):
                            corr = 0.0
                    else:
                        corr = float(self._rng.uniform(-0.5, 0.8))
                    correlations[m1][m2] = corr
        return correlations

    def analyze_global_state(self, snapshot_id: str) -> GlobalMarketState:
        snapshot = next((s for s in self._snapshots if s.id == snapshot_id), None)
        if not snapshot:
            raise ValueError(f"Snapshot {snapshot_id} not found")

        state = GlobalMarketState(snapshot_id=snapshot_id)
        state.liquidity_score = self._liquidity_score(snapshot)
        state.risk_score = self._risk_score(snapshot)
        state.momentum_score = self._momentum_score(snapshot)
        state.global_regime = self._detect_regime(state)
        state.correlation_matrix = snapshot.correlations
        state.anomaly_detected, state.anomaly_description = self._detect_anomalies(snapshot)

        self._states.append(state)
        return state

    def _liquidity_score(self, snapshot: MarketSnapshot) -> float:
        values = list(snapshot.forex.values()) + list(snapshot.crypto.values())
        return float(np.mean(values)) if values else 0.5

    def _risk_score(self, snapshot: MarketSnapshot) -> float:
        values = list(snapshot.bonds.values()) + list(snapshot.macro.values())
        base = float(np.mean(values)) if values else 0.5
        # Invert: higher bond activity → lower risk
        return max(0.0, min(1.0, 1.0 - base))

    def _momentum_score(self, snapshot: MarketSnapshot) -> float:
        values = list(snapshot.indices.values()) + list(snapshot.futures.values())
        return float(np.mean(values)) if values else 0.5

    def _detect_regime(self, state: GlobalMarketState) -> str:
        if state.risk_score > 0.7:
            return "crisis"
        if state.risk_score > 0.5:
            return "high_risk"
        if state.momentum_score > 0.6 and state.liquidity_score > 0.6:
            return "bull"
        if state.momentum_score < 0.4 and state.liquidity_score > 0.5:
            return "bear"
        return "neutral"

    def _detect_anomalies(self, snapshot: MarketSnapshot) -> Tuple[bool, str]:
        all_vals: List[float] = []
        for m in self._MARKETS:
            all_vals.extend(getattr(snapshot, m, {}).values())
        if not all_vals:
            return False, ""
        arr = np.array(all_vals)
        z_scores = np.abs((arr - arr.mean()) / (arr.std() + 1e-9))
        if np.any(z_scores > 3):
            return True, "Extreme z-score detected in market data"
        return False, ""

    def get_global_state(self) -> Optional[GlobalMarketState]:
        return self._states[-1] if self._states else None

    def get_correlation_matrix(self) -> Dict[str, Dict[str, float]]:
        return self._states[-1].correlation_matrix if self._states else {}
