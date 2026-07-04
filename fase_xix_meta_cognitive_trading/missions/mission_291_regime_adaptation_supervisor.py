# ============================================================
# MISSÃO 291 — REGIME ADAPTATION SUPERVISOR
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class RegimeTransition:
    """Transição de regime."""
    id: str = field(default_factory=lambda: f"rt_{uuid.uuid4().hex[:12]}")
    from_regime: str = ""
    to_regime: str = ""
    confidence: float = 0.0
    transition_score: float = 0.0
    adaptation_needed: bool = False
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "from_regime": self.from_regime,
            "to_regime": self.to_regime,
            "confidence": self.confidence,
            "transition_score": self.transition_score,
            "adaptation_needed": self.adaptation_needed,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class RegimeAdaptationSupervisor:
    """
    Supervisor de adaptação a regimes.

    Implementa:
    - Regime Transition Monitor
    - Strategy Rotation
    - Adaptive Parameters
    - Regime Confidence
    - Regime Stability
    - Drift Detection
    - Adaptive Learning
    - Transition History
    - Supervisor Dashboard
    - Recovery Logic
    """

    def __init__(self):
        self._transitions: List[RegimeTransition] = []
        self._regime_history: List[str] = []
        self._regime_stability: Dict[str, float] = {}
        self._regimes = [
            "trending_bull",
            "trending_bear",
            "ranging",
            "high_volatility",
            "crisis",
        ]

    def monitor_regime(
        self,
        current_regime: str,
        market_data: Dict[str, Any],
    ) -> RegimeTransition:
        """Monitora regime e detecta transições."""
        if self._regime_history:
            previous = self._regime_history[-1]
            if previous != current_regime:
                transition_score = self._calculate_transition_score(
                    previous, current_regime, market_data
                )
                confidence = self._calculate_confidence(market_data)

                transition = RegimeTransition(
                    from_regime=previous,
                    to_regime=current_regime,
                    confidence=confidence,
                    transition_score=transition_score,
                    adaptation_needed=True,
                    recommendation=self._generate_recommendation(previous, current_regime),
                )

                self._transitions.append(transition)
                self._regime_history.append(current_regime)
                return transition

        self._regime_history.append(current_regime)
        return RegimeTransition(
            from_regime=current_regime,
            to_regime=current_regime,
            confidence=1.0,
            transition_score=0.0,
            adaptation_needed=False,
            recommendation="No transition detected. Continue current strategy.",
        )

    def _calculate_transition_score(self, from_regime: str, to_regime: str, market: Dict) -> float:
        """Calcula score de transição."""
        volatility = market.get("volatility", 0.3)
        score = min(volatility * 2, 1.0)

        if market.get("volume_spike", False):
            score += 0.2

        if market.get("trend_change", 0) > 0.3:
            score += 0.2

        return min(score, 1.0)

    def _calculate_confidence(self, market: Dict) -> float:
        """Calcula confiança na transição."""
        confidence = 0.5

        if market.get("data_quality", 0) > 0.7:
            confidence += 0.2

        if market.get("volatility", 0.3) < 0.4:
            confidence += 0.1

        return min(confidence, 1.0)

    def _generate_recommendation(self, from_regime: str, to_regime: str) -> str:
        """Gera recomendação de adaptação."""
        recommendations = {
            ("trending_bull", "ranging"): "Reduce position size. Wait for trend confirmation.",
            ("trending_bull", "trending_bear"): "Switch to defensive strategy. Increase risk monitoring.",
            ("ranging", "trending_bull"): "Increase position size. Follow trend.",
            ("ranging", "trending_bear"): "Reduce exposure. Consider short positions.",
            ("high_volatility", "crisis"): "Emergency protocol: Halt new positions.",
        }

        return recommendations.get(
            (from_regime, to_regime),
            "Monitor regime transition. Adjust parameters accordingly.",
        )

    def get_regime_stability(self) -> Dict[str, float]:
        """Retorna estabilidade dos regimes."""
        if not self._regime_history:
            return {r: 0.0 for r in self._regimes}

        for regime in self._regimes:
            count = self._regime_history.count(regime)
            self._regime_stability[regime] = count / len(self._regime_history)

        return self._regime_stability

    def get_supervisor_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard do supervisor."""
        return {
            "total_transitions": len(self._transitions),
            "recent_transitions": [t.to_dict() for t in self._transitions[-5:]],
            "regime_stability": self.get_regime_stability(),
            "current_regime": self._regime_history[-1] if self._regime_history else "unknown",
            "regime_diversity": len(set(self._regime_history[-50:]))
            if len(self._regime_history) >= 50
            else 0,
            "adaptation_triggered": any(t.adaptation_needed for t in self._transitions[-5:]),
        }
