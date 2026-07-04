# ============================================================
# MISSÃO 261 — ADAPTIVE MARKET TIMING
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import uuid
import numpy as np


@dataclass
class TimingSignal:
    """Sinal de timing."""
    id: str = field(default_factory=lambda: f"ts_{uuid.uuid4().hex[:12]}")
    asset: str = ""
    action: str = ""
    timing_type: str = ""
    optimal_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.0
    score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "asset": self.asset,
            "action": self.action,
            "timing_type": self.timing_type,
            "optimal_time": self.optimal_time.isoformat(),
            "confidence": self.confidence,
            "score": self.score,
            "created_at": self.created_at.isoformat(),
        }


class AdaptiveMarketTiming:
    """Timing adaptativo de mercado."""

    def __init__(self):
        self._signals: List[TimingSignal] = []
        self._timing_history: Dict[str, List[Dict[str, Any]]] = {}
        self._timing_weights = {
            "regime": 0.3,
            "volatility": 0.25,
            "liquidity": 0.25,
            "session": 0.2,
        }

    def calculate_entry_timing(self, asset: str, market_data: Dict[str, Any]) -> TimingSignal:
        regime_score = self._calculate_regime_timing(market_data)
        volatility_score = self._calculate_volatility_timing(market_data)
        liquidity_score = self._calculate_liquidity_timing(market_data)
        session_score = self._calculate_session_timing()

        final_score = (
            regime_score * self._timing_weights["regime"]
            + volatility_score * self._timing_weights["volatility"]
            + liquidity_score * self._timing_weights["liquidity"]
            + session_score * self._timing_weights["session"]
        )
        confidence = 0.5 + final_score * 0.4

        signal = TimingSignal(
            asset=asset,
            action="entry",
            timing_type="combined",
            optimal_time=datetime.now(timezone.utc) + timedelta(minutes=30),
            confidence=confidence,
            score=final_score,
        )
        self._signals.append(signal)
        return signal

    def calculate_exit_timing(self, asset: str, position_data: Dict[str, Any]) -> TimingSignal:
        base_score = 0.6
        if position_data.get("profit", 0) > 0.02:
            base_score += 0.2
        if position_data.get("duration_minutes", 0) > 60:
            base_score += 0.1

        final_score = min(base_score, 1.0)
        confidence = 0.5 + final_score * 0.3

        signal = TimingSignal(
            asset=asset,
            action="exit",
            timing_type="combined",
            optimal_time=datetime.now(timezone.utc) + timedelta(minutes=15),
            confidence=confidence,
            score=final_score,
        )
        self._signals.append(signal)
        return signal

    def _calculate_regime_timing(self, data: Dict) -> float:
        regime_scores = {
            "trending_bull": 0.8,
            "trending_bear": 0.2,
            "ranging": 0.5,
            "high_volatility": 0.4,
            "crisis": 0.1,
            "neutral": 0.5,
        }
        return regime_scores.get(data.get("regime", "neutral"), 0.5)

    def _calculate_volatility_timing(self, data: Dict) -> float:
        volatility = data.get("volatility", 0.3)
        return 1 - abs(volatility - 0.3) * 2

    def _calculate_liquidity_timing(self, data: Dict) -> float:
        return data.get("liquidity", 0.5)

    def _calculate_session_timing(self) -> float:
        hour = datetime.now(timezone.utc).hour
        if 13 <= hour <= 17:
            return 0.8
        if 8 <= hour <= 12:
            return 0.6
        return 0.4

    def get_timing_dashboard(self) -> Dict[str, Any]:
        recent = self._signals[-20:]
        return {
            "total_signals": len(self._signals),
            "recent_signals": len(recent),
            "avg_confidence": np.mean([s.confidence for s in recent]) if recent else 0,
            "entry_signals": sum(1 for s in recent if s.action == "entry"),
            "exit_signals": sum(1 for s in recent if s.action == "exit"),
            "best_timing": max(recent, key=lambda x: x.score).to_dict() if recent else None,
        }
