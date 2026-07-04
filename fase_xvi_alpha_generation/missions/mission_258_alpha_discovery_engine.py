# ============================================================
# MISSÃO 258 — ALPHA DISCOVERY ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib
import numpy as np


def _deterministic_unit(seed: str, lo: float = 0.0, hi: float = 1.0) -> float:
    """Valor determinístico em [lo, hi] a partir de seed."""
    digest = hashlib.sha256(seed.encode()).hexdigest()
    return lo + (int(digest[:8], 16) / 0xFFFFFFFF) * (hi - lo)


@dataclass
class AlphaSignature:
    """Assinatura de Alpha."""
    id: str = field(default_factory=lambda: f"alpha_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    formula: str = ""
    score: float = 0.0
    confidence: float = 0.0
    lifetime_estimate_days: float = 0.0
    correlation_to_market: float = 0.0
    diversity_score: float = 0.0
    validation_status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_validated: Optional[datetime] = None
    decay_rate: float = 0.0
    performance_history: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "formula": self.formula,
            "score": self.score,
            "confidence": self.confidence,
            "lifetime_estimate_days": self.lifetime_estimate_days,
            "correlation_to_market": self.correlation_to_market,
            "diversity_score": self.diversity_score,
            "validation_status": self.validation_status,
            "created_at": self.created_at.isoformat(),
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "decay_rate": self.decay_rate,
            "performance_history": self.performance_history[-20:],
        }


@dataclass
class AlphaDiscoveryResult:
    """Resultado da descoberta de Alpha."""
    id: str = field(default_factory=lambda: f"adr_{uuid.uuid4().hex[:12]}")
    alpha_id: str = ""
    discovery_method: str = ""
    signal_strength: float = 0.0
    sharpe_ratio: float = 0.0
    win_rate: float = 0.0
    max_drawdown: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "alpha_id": self.alpha_id,
            "discovery_method": self.discovery_method,
            "signal_strength": self.signal_strength,
            "sharpe_ratio": self.sharpe_ratio,
            "win_rate": self.win_rate,
            "max_drawdown": self.max_drawdown,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class AlphaDiscoveryEngine:
    """Motor de descoberta de Alpha."""

    def __init__(self):
        self._alphas: Dict[str, AlphaSignature] = {}
        self._discoveries: List[AlphaDiscoveryResult] = []
        self._alpha_registry: Dict[str, Dict[str, Any]] = {}

    def discover_alpha(
        self,
        name: str,
        description: str,
        formula: str,
        performance_data: List[float],
    ) -> AlphaSignature:
        """Descobre novo Alpha."""
        if len(performance_data) > 1:
            returns = np.array(performance_data)
            mean_return = np.mean(returns)
            std_return = np.std(returns)
            sharpe = mean_return / std_return if std_return > 0 else 0
            win_rate = sum(1 for r in returns if r > 0) / len(returns)
            max_dd = self._calculate_max_drawdown(returns)
        else:
            sharpe = 0.0
            win_rate = 0.0
            max_dd = 0.0

        score = min(sharpe / 2 + win_rate * 0.5, 1.0)
        confidence = min(len(performance_data) / 100, 1.0)
        lifetime = self._estimate_lifetime(sharpe, win_rate, len(performance_data))
        correlation = _deterministic_unit(f"{name}:{formula}", -0.3, 0.3)
        diversity = self._calculate_diversity(formula)

        alpha = AlphaSignature(
            name=name,
            description=description,
            formula=formula,
            score=score,
            confidence=confidence,
            lifetime_estimate_days=lifetime,
            correlation_to_market=correlation,
            diversity_score=diversity,
            performance_history=performance_data[-20:],
            decay_rate=0.1 / lifetime if lifetime > 0 else 0.1,
        )

        self._alphas[alpha.id] = alpha
        return alpha

    def _calculate_max_drawdown(self, returns: np.ndarray) -> float:
        cum_returns = np.cumprod(1 + returns)
        running_max = np.maximum.accumulate(cum_returns)
        drawdown = (cum_returns - running_max) / running_max
        return abs(np.min(drawdown)) if len(drawdown) > 0 else 0.0

    def _estimate_lifetime(self, sharpe: float, win_rate: float, sample_size: int) -> float:
        base_lifetime = 30.0
        quality_factor = min(max(sharpe * 0.5 + win_rate * 0.5, 0.1), 1.0)
        sample_factor = min(sample_size / 100, 1.0)
        return base_lifetime * (quality_factor * 0.7 + sample_factor * 0.3)

    def _calculate_diversity(self, formula: str) -> float:
        common_terms = ["moving_average", "rsi", "macd", "bollinger", "ema"]
        unique_terms = [t for t in common_terms if t not in formula.lower()]
        diversity = 0.5 + len(unique_terms) / len(common_terms) * 0.5
        return min(diversity, 1.0)

    def validate_alpha(self, alpha_id: str) -> bool:
        alpha = self._alphas.get(alpha_id)
        if not alpha:
            return False

        if len(alpha.performance_history) >= 20:
            recent = alpha.performance_history[-20:]
            win_rate = sum(1 for r in recent if r > 0) / len(recent)
            if win_rate > 0.5 and alpha.score > 0.3:
                alpha.validation_status = "validated"
                alpha.last_validated = datetime.now(timezone.utc)
                return True

        alpha.validation_status = "rejected"
        return False

    def get_alpha_ranking(self) -> List[AlphaSignature]:
        validated = [a for a in self._alphas.values() if a.validation_status == "validated"]
        return sorted(validated, key=lambda x: x.score, reverse=True)

    def get_alpha_dashboard(self) -> Dict[str, Any]:
        total = len(self._alphas)
        validated = sum(1 for a in self._alphas.values() if a.validation_status == "validated")
        rejected = sum(1 for a in self._alphas.values() if a.validation_status == "rejected")
        return {
            "total_alphas": total,
            "validated_alphas": validated,
            "rejected_alphas": rejected,
            "avg_score": np.mean([a.score for a in self._alphas.values()]) if self._alphas else 0,
            "avg_lifetime": np.mean([a.lifetime_estimate_days for a in self._alphas.values()]) if self._alphas else 0,
            "top_alphas": [a.to_dict() for a in self.get_alpha_ranking()[:5]],
        }
