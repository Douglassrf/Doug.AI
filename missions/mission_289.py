# ============================================================
# MISSÃO 289 — ADAPTIVE BIAS DETECTOR
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class BiasReport:
    """Relatório de viés."""
    id: str = field(default_factory=lambda: f"br_{uuid.uuid4().hex[:12]}")
    bias_type: str = ""
    score: float = 0.0
    severity: str = "low"  # low, medium, high, critical
    impact: float = 0.0
    recommendation: str = ""
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "bias_type": self.bias_type,
            "score": self.score,
            "severity": self.severity,
            "impact": self.impact,
            "recommendation": self.recommendation,
            "detected_at": self.detected_at.isoformat(),
            "details": self.details,
        }


class AdaptiveBiasDetector:
    """
    Detector adaptativo de vieses.

    Implementa:
    - Recency Bias
    - Confirmation Bias
    - Overfitting Bias
    - Regime Bias
    - Survivorship Bias
    - Confidence Bias
    - Statistical Bias
    - Bias History
    - Bias Alerts
    - Bias Dashboard
    """

    def __init__(self):
        self._reports: List[BiasReport] = []
        self._bias_thresholds = {
            "recency": 0.6,
            "confirmation": 0.6,
            "overfitting": 0.7,
            "regime": 0.5,
            "survivorship": 0.4,
            "confidence": 0.6,
            "statistical": 0.5,
        }

    def detect_biases(self, data: Dict[str, Any]) -> List[BiasReport]:
        """Detecta vieses nos dados."""
        reports = []

        recency = self._detect_recency_bias(data)
        if recency:
            reports.append(recency)

        confirmation = self._detect_confirmation_bias(data)
        if confirmation:
            reports.append(confirmation)

        overfitting = self._detect_overfitting_bias(data)
        if overfitting:
            reports.append(overfitting)

        regime = self._detect_regime_bias(data)
        if regime:
            reports.append(regime)

        confidence = self._detect_confidence_bias(data)
        if confidence:
            reports.append(confidence)

        self._reports.extend(reports)
        return reports

    def _detect_recency_bias(self, data: Dict) -> Optional[BiasReport]:
        """Detecta viés de recência."""
        recent_weight = data.get("recent_weight", 0.5)
        if recent_weight > self._bias_thresholds["recency"]:
            return BiasReport(
                bias_type="recency",
                score=recent_weight,
                severity="high" if recent_weight > 0.8 else "medium",
                impact=recent_weight * 0.5,
                recommendation="Reduce weight on recent data. Use longer lookback periods.",
                details={"recent_weight": recent_weight},
            )
        return None

    def _detect_confirmation_bias(self, data: Dict) -> Optional[BiasReport]:
        """Detecta viés de confirmação."""
        confirmation_ratio = data.get("confirmation_ratio", 0.5)
        if confirmation_ratio > self._bias_thresholds["confirmation"]:
            return BiasReport(
                bias_type="confirmation",
                score=confirmation_ratio,
                severity="high" if confirmation_ratio > 0.8 else "medium",
                impact=confirmation_ratio * 0.4,
                recommendation="Seek disconfirming evidence. Challenge assumptions.",
                details={"confirmation_ratio": confirmation_ratio},
            )
        return None

    def _detect_overfitting_bias(self, data: Dict) -> Optional[BiasReport]:
        """Detecta viés de overfitting."""
        overfit_score = data.get("overfit_score", 0.0)
        if overfit_score > self._bias_thresholds["overfitting"]:
            return BiasReport(
                bias_type="overfitting",
                score=overfit_score,
                severity="critical" if overfit_score > 0.9 else "high",
                impact=overfit_score * 0.6,
                recommendation="Reduce model complexity. Increase validation data.",
                details={"overfit_score": overfit_score},
            )
        return None

    def _detect_regime_bias(self, data: Dict) -> Optional[BiasReport]:
        """Detecta viés de regime."""
        regime_coverage = data.get("regime_coverage", 1.0)
        if regime_coverage < self._bias_thresholds["regime"]:
            return BiasReport(
                bias_type="regime",
                score=1 - regime_coverage,
                severity="high" if regime_coverage < 0.3 else "medium",
                impact=(1 - regime_coverage) * 0.5,
                recommendation="Expand training across multiple market regimes.",
                details={"regime_coverage": regime_coverage},
            )
        return None

    def _detect_confidence_bias(self, data: Dict) -> Optional[BiasReport]:
        """Detecta viés de confiança."""
        confidence_gap = data.get("confidence_gap", 0.0)
        if confidence_gap > self._bias_thresholds["confidence"]:
            return BiasReport(
                bias_type="confidence",
                score=confidence_gap,
                severity="high" if confidence_gap > 0.8 else "medium",
                impact=confidence_gap * 0.3,
                recommendation="Calibrate confidence with historical accuracy.",
                details={"confidence_gap": confidence_gap},
            )
        return None

    def get_bias_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de vieses."""
        if not self._reports:
            return {"status": "no_biases_detected"}

        recent = self._reports[-20:]

        return {
            "total_biases": len(self._reports),
            "recent_biases": len(recent),
            "bias_distribution": {
                bias_type: sum(1 for r in recent if r.bias_type == bias_type)
                for bias_type in set(r.bias_type for r in recent)
            },
            "severity_distribution": {
                "critical": sum(1 for r in recent if r.severity == "critical"),
                "high": sum(1 for r in recent if r.severity == "high"),
                "medium": sum(1 for r in recent if r.severity == "medium"),
                "low": sum(1 for r in recent if r.severity == "low"),
            },
            "avg_impact": np.mean([r.impact for r in recent]) if recent else 0,
            "recommendations": [
                r.recommendation for r in recent if r.severity in ["high", "critical"]
            ],
        }
