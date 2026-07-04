from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class RegimeTransition:
    current_regime: str = ""
    previous_regime: str = ""
    transition_score: float = 0.0
    early_confidence: float = 0.0
    transition_type: str = "none"
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    indicators: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "current_regime": self.current_regime,
            "previous_regime": self.previous_regime,
            "transition_score": self.transition_score,
            "early_confidence": self.early_confidence,
            "transition_type": self.transition_type,
            "detected_at": self.detected_at.isoformat(),
            "indicators": self.indicators,
        }


class RegimeTransitionIntelligence:
    def __init__(self):
        self._regime_history: List[Dict[str, Any]] = []
        self._regime_transitions: List[RegimeTransition] = []

    def analyze(self, current_regime: str, indicators: Dict[str, float]) -> RegimeTransition:
        previous = self._regime_history[-1]["regime"] if self._regime_history else current_regime
        transition_score = self._calculate_transition_score(indicators)
        early_confidence = self._calculate_early_confidence(indicators)
        transition_type = self._determine_transition_type(transition_score, early_confidence)
        t = RegimeTransition(
            current_regime=current_regime, previous_regime=previous,
            transition_score=transition_score, early_confidence=early_confidence,
            transition_type=transition_type, indicators=indicators,
        )
        self._regime_transitions.append(t)
        self._regime_history.append({"regime": current_regime,
                                     "timestamp": datetime.now(timezone.utc).isoformat()})
        return t

    def _calculate_transition_score(self, indicators: Dict[str, float]) -> float:
        score = 0.0
        if indicators.get("volatility", 0) > 0.5: score += 0.2
        if abs(indicators.get("momentum", 0)) > 0.3: score += 0.2
        v = indicators.get("volume_ratio", 1.0)
        if v > 2.0 or v < 0.5: score += 0.2
        if indicators.get("trend_change", 0) > 0.3: score += 0.2
        if indicators.get("anomaly", 0) > 0.5: score += 0.2
        return float(min(score, 1.0))

    def _calculate_early_confidence(self, indicators: Dict[str, float]) -> float:
        if not indicators: return 0.0
        conf = sum(1 for v in indicators.values() if v > 0.5) / len(indicators) * 0.5
        conf += float(np.mean(list(indicators.values()))) * 0.2
        return float(min(conf, 1.0))

    def _determine_transition_type(self, score: float, confidence: float) -> str:
        if score > 0.7 and confidence > 0.7: return "hard"
        if score > 0.4: return "soft"
        return "none"

    def get_transition_alerts(self, threshold: float = 0.5) -> List[RegimeTransition]:
        return [t for t in self._regime_transitions if t.transition_score > threshold]
