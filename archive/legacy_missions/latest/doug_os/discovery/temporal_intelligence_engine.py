from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


class TimeHorizon:
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    VERY_LONG = "very_long"


@dataclass
class TemporalData:
    timestamp: datetime
    value: float
    horizon: str = TimeHorizon.SHORT
    confidence: float = 0.5
    persistence: float = 0.0
    cycle: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(), "value": self.value,
            "horizon": self.horizon, "confidence": self.confidence,
            "persistence": self.persistence, "cycle": self.cycle,
        }


@dataclass
class TemporalIntelligence:
    short_term: Dict[str, Any] = field(default_factory=dict)
    medium_term: Dict[str, Any] = field(default_factory=dict)
    long_term: Dict[str, Any] = field(default_factory=dict)
    very_long_term: Dict[str, Any] = field(default_factory=dict)
    persistence_score: float = 0.0
    cycle_detected: Optional[str] = None
    change_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "short_term": self.short_term, "medium_term": self.medium_term,
            "long_term": self.long_term, "very_long_term": self.very_long_term,
            "persistence_score": self.persistence_score,
            "cycle_detected": self.cycle_detected, "change_score": self.change_score,
            "created_at": self.created_at.isoformat(),
        }


class TemporalIntelligenceEngine:
    def __init__(self):
        self._history: List[TemporalData] = []

    def analyze(self, data: TemporalData) -> TemporalIntelligence:
        self._history.append(data)
        return TemporalIntelligence(
            short_term=self._analyze_horizon(TimeHorizon.SHORT),
            medium_term=self._analyze_horizon(TimeHorizon.MEDIUM),
            long_term=self._analyze_horizon(TimeHorizon.LONG),
            very_long_term=self._analyze_horizon(TimeHorizon.VERY_LONG),
            persistence_score=self._calculate_persistence(),
            cycle_detected=self._detect_cycle(),
            change_score=self._calculate_change_score(),
        )

    def _analyze_horizon(self, horizon: str) -> Dict[str, Any]:
        filtered = [d for d in self._history if d.horizon == horizon]
        if not filtered: return {"status": "no_data"}
        values = [d.value for d in filtered]
        return {
            "count": len(values), "mean": float(np.mean(values)),
            "std": float(np.std(values)), "min": float(np.min(values)),
            "max": float(np.max(values)), "trend": self._calculate_trend(values),
            "confidence": float(np.mean([d.confidence for d in filtered])),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        if len(values) < 3: return "stable"
        x = np.arange(len(values))
        slope = float(np.polyfit(x, values, 1)[0])
        if slope > 0.01: return "increasing"
        if slope < -0.01: return "decreasing"
        return "stable"

    def _calculate_persistence(self) -> float:
        if len(self._history) < 10: return 0.0
        values = [d.value for d in self._history[-10:]]
        corr = np.corrcoef(values[:-1], values[1:])
        return float(max(corr[0, 1], 0.0)) if corr.shape == (2, 2) else 0.0

    def _detect_cycle(self) -> Optional[str]:
        if len(self._history) < 20: return None
        values = [d.value for d in self._history[-20:]]
        fft = np.fft.fft(values)
        freqs = np.fft.fftfreq(len(values))
        dominant = float(freqs[int(np.argmax(np.abs(fft[1:]))) + 1])
        if abs(dominant) > 0.1: return "short_cycle"
        if abs(dominant) > 0.05: return "medium_cycle"
        return "long_cycle"

    def _calculate_change_score(self) -> float:
        if len(self._history) < 5: return 0.0
        recent = [d.value for d in self._history[-5:]]
        older = [d.value for d in self._history[-10:-5]]
        if not older: return 0.0
        return float(min(abs(np.mean(recent) - np.mean(older)), 1.0))
