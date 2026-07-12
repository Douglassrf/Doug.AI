from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np
from enum import Enum


class Timeframe(Enum):
    TICK = "tick"; M1 = "1m"; M5 = "5m"; M15 = "15m"; M30 = "30m"
    H1 = "1h"; H4 = "4h"; D1 = "1d"; W1 = "1w"; MN = "1M"


class SignalType(Enum):
    BUY = "buy"; SELL = "sell"; NEUTRAL = "neutral"
    STRONG_BUY = "strong_buy"; STRONG_SELL = "strong_sell"


@dataclass
class TimeframeSignal:
    timeframe: Timeframe
    signal: SignalType
    strength: float = 0.0
    confidence: float = 0.0
    price: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    indicators: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timeframe": self.timeframe.value,
            "signal": self.signal.value,
            "strength": self.strength,
            "confidence": self.confidence,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
            "indicators": self.indicators,
        }


@dataclass
class ConsensusResult:
    id: str = field(default_factory=lambda: f"cons_{uuid.uuid4().hex[:12]}")
    final_signal: SignalType = SignalType.NEUTRAL
    final_strength: float = 0.0
    final_confidence: float = 0.0
    votes: Dict[str, str] = field(default_factory=dict)
    weights: Dict[str, float] = field(default_factory=dict)
    divergences: List[Dict[str, Any]] = field(default_factory=list)
    consensus_score: float = 0.0
    regime: str = ""
    regime_weight: float = 1.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "final_signal": self.final_signal.value,
            "final_strength": self.final_strength,
            "final_confidence": self.final_confidence,
            "votes": self.votes,
            "weights": self.weights,
            "divergences": self.divergences,
            "consensus_score": self.consensus_score,
            "regime": self.regime,
            "regime_weight": self.regime_weight,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class MultiTimeframeConsensusEngine:
    _REGIME_WEIGHTS = {
        "trending_bull":   {"short": 0.3, "medium": 0.4, "long": 0.3},
        "trending_bear":   {"short": 0.3, "medium": 0.4, "long": 0.3},
        "ranging":         {"short": 0.5, "medium": 0.3, "long": 0.2},
        "high_volatility": {"short": 0.6, "medium": 0.3, "long": 0.1},
        "crisis":          {"short": 0.7, "medium": 0.2, "long": 0.1},
    }
    _SHORT_TF = {Timeframe.TICK, Timeframe.M1, Timeframe.M5, Timeframe.M15, Timeframe.M30}
    _MEDIUM_TF = {Timeframe.H1, Timeframe.H4}
    _OPPOSITES = {
        SignalType.BUY: {SignalType.SELL, SignalType.STRONG_SELL},
        SignalType.STRONG_BUY: {SignalType.SELL, SignalType.STRONG_SELL},
        SignalType.SELL: {SignalType.BUY, SignalType.STRONG_BUY},
        SignalType.STRONG_SELL: {SignalType.BUY, SignalType.STRONG_BUY},
    }

    def __init__(self):
        self._signals: Dict[Timeframe, List[TimeframeSignal]] = {tf: [] for tf in Timeframe}
        self._consensus_history: List[ConsensusResult] = []

    def add_signal(self, signal: TimeframeSignal) -> None:
        self._signals[signal.timeframe].append(signal)
        if len(self._signals[signal.timeframe]) > 100:
            self._signals[signal.timeframe] = self._signals[signal.timeframe][-100:]

    def get_consensus(
        self,
        regime: str = "neutral",
        timeframe_weights: Optional[Dict[str, float]] = None,
    ) -> ConsensusResult:
        result = ConsensusResult(regime=regime)
        latest = {tf: sigs[-1] for tf, sigs in self._signals.items() if sigs}
        if not latest:
            return result
        weights = self._calculate_weights(regime, timeframe_weights)
        result.weights = {tf.value: weights.get(tf, 0.0) for tf in latest}
        vote_counts: Dict[str, float] = {}
        total_w = 0.0
        for tf, sig in latest.items():
            w = weights.get(tf, 0.1)
            total_w += w
            vote_counts[sig.signal.value] = vote_counts.get(sig.signal.value, 0.0) + w
            result.votes[tf.value] = sig.signal.value
        if vote_counts:
            winner = max(vote_counts, key=vote_counts.get)
            result.final_signal = SignalType(winner)
            result.final_strength = vote_counts[winner] / total_w if total_w else 0.0
        result.final_confidence = self._calculate_confidence(vote_counts, total_w)
        result.divergences = self._detect_divergences(latest)
        result.consensus_score = 1.0 - (len(result.divergences) / len(latest)) if latest else 0.0
        result.recommendation = self._generate_recommendation(result)
        self._consensus_history.append(result)
        return result

    def _calculate_weights(
        self, regime: str, custom: Optional[Dict[str, float]]
    ) -> Dict[Timeframe, float]:
        rw = self._REGIME_WEIGHTS.get(regime, self._REGIME_WEIGHTS["ranging"])
        weights: Dict[Timeframe, float] = {}
        for tf in Timeframe:
            cat = "short" if tf in self._SHORT_TF else ("medium" if tf in self._MEDIUM_TF else "long")
            weights[tf] = rw.get(cat, 0.3)
        if custom:
            for tf_str, w in custom.items():
                try:
                    weights[Timeframe(tf_str)] = w
                except ValueError:
                    pass
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()} if total else weights

    def _calculate_confidence(self, vote_counts: Dict[str, float], total: float) -> float:
        if not vote_counts or total == 0:
            return 0.0
        max_v = max(vote_counts.values())
        conf = max_v / total
        sorted_v = sorted(vote_counts.values(), reverse=True)
        if len(sorted_v) > 1:
            conf *= 1.0 - sorted_v[1] / max_v * 0.3
        return min(conf, 1.0)

    def _detect_divergences(
        self, signals: Dict[Timeframe, TimeframeSignal]
    ) -> List[Dict[str, Any]]:
        divs: List[Dict[str, Any]] = []
        items = list(signals.items())
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                tf1, s1 = items[i]
                tf2, s2 = items[j]
                if s2.signal in self._OPPOSITES.get(s1.signal, set()):
                    divs.append({
                        "timeframe_1": tf1.value, "signal_1": s1.signal.value,
                        "timeframe_2": tf2.value, "signal_2": s2.signal.value,
                        "severity": "high" if abs(s1.strength - s2.strength) > 0.5 else "medium",
                    })
        return divs

    def _generate_recommendation(self, r: ConsensusResult) -> str:
        if r.consensus_score < 0.3:
            return "HIGH DIVERGENCE: Wait for convergence"
        if r.final_signal == SignalType.NEUTRAL:
            return "NEUTRAL: No clear signal"
        if r.final_confidence < 0.5:
            return f"WEAK {r.final_signal.value.upper()} signal. Consider waiting."
        if r.final_strength > 0.7:
            return f"STRONG {r.final_signal.value.upper()} signal. High conviction."
        return f"{r.final_signal.value.upper()} signal. Confidence: {r.final_confidence:.2f}"

    def get_consensus_history(self, limit: int = 10) -> List[ConsensusResult]:
        return self._consensus_history[-limit:]

    def get_temporal_summary(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        for tf in Timeframe:
            sigs = self._signals[tf]
            if sigs:
                last = sigs[-1]
                summary[tf.value] = {
                    "signal": last.signal.value,
                    "strength": last.strength,
                    "confidence": last.confidence,
                    "count": len(sigs),
                }
            else:
                summary[tf.value] = {"signal": "no_data"}
        return summary
