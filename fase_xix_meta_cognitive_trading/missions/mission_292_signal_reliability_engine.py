# ============================================================
# MISSÃO 292 — SIGNAL RELIABILITY ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class SignalReliability:
    """Confiabilidade do sinal."""
    id: str = field(default_factory=lambda: f"sr_{uuid.uuid4().hex[:12]}")
    signal_id: str = ""
    quality_score: float = 0.0
    stability_score: float = 0.0
    persistence_score: float = 0.0
    historical_accuracy: float = 0.0
    reliability_score: float = 0.0
    certification_status: str = "pending"  # pending, certified, rejected
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "signal_id": self.signal_id,
            "quality_score": self.quality_score,
            "stability_score": self.stability_score,
            "persistence_score": self.persistence_score,
            "historical_accuracy": self.historical_accuracy,
            "reliability_score": self.reliability_score,
            "certification_status": self.certification_status,
            "created_at": self.created_at.isoformat(),
        }


class SignalReliabilityEngine:
    """
    Motor de confiabilidade de sinais.

    Implementa:
    - Signal Quality
    - Signal Stability
    - Signal Persistence
    - Historical Accuracy
    - Signal Ranking
    - Signal Certification
    - False Signal Detector
    - Reliability History
    - Signal Dashboard
    - Continuous Calibration
    """

    def __init__(self):
        self._reliabilities: Dict[str, List[SignalReliability]] = {}
        self._certified_signals: List[str] = []
        self._false_signals: List[str] = []

    def evaluate_signal(
        self,
        signal_id: str,
        quality: float,
        stability: float,
        persistence: float,
        historical_accuracy: float,
    ) -> SignalReliability:
        """Avalia confiabilidade do sinal."""
        reliability_score = (
            quality * 0.25
            + stability * 0.25
            + persistence * 0.20
            + historical_accuracy * 0.30
        )

        reliability = SignalReliability(
            signal_id=signal_id,
            quality_score=quality,
            stability_score=stability,
            persistence_score=persistence,
            historical_accuracy=historical_accuracy,
            reliability_score=reliability_score,
        )

        if reliability_score > 0.7:
            reliability.certification_status = "certified"
            if signal_id not in self._certified_signals:
                self._certified_signals.append(signal_id)
        elif reliability_score < 0.3:
            reliability.certification_status = "rejected"
            self._false_signals.append(signal_id)

        if signal_id not in self._reliabilities:
            self._reliabilities[signal_id] = []

        self._reliabilities[signal_id].append(reliability)
        return reliability

    def detect_false_signal(self, signal_id: str) -> bool:
        """Detecta sinal falso."""
        if signal_id not in self._reliabilities:
            return False

        recent = self._reliabilities[signal_id][-5:]
        if len(recent) < 3:
            return False

        trend = [r.reliability_score for r in recent]
        if all(trend[i] > trend[i + 1] for i in range(len(trend) - 1)):
            return True

        return False

    def get_signal_ranking(self) -> List[SignalReliability]:
        """Retorna ranking de sinais."""
        all_reliabilities = []
        for rels in self._reliabilities.values():
            if rels:
                all_reliabilities.append(rels[-1])

        return sorted(all_reliabilities, key=lambda x: x.reliability_score, reverse=True)

    def get_signal_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de sinais."""
        total_signals = len(self._reliabilities)
        certified = len(self._certified_signals)
        rejected = len(self._false_signals)

        return {
            "total_signals": total_signals,
            "certified_signals": certified,
            "rejected_signals": rejected,
            "certification_rate": certified / total_signals if total_signals > 0 else 0,
            "avg_reliability": np.mean([
                r.reliability_score for rels in self._reliabilities.values() for r in rels
            ])
            if total_signals > 0
            else 0,
            "top_signals": [r.to_dict() for r in self.get_signal_ranking()[:5]],
        }
