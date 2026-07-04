# ============================================================
# MISSÃO 295 — META LEARNING FEEDBACK ENGINE (stub mínimo)
# Fase XIX — Meta-Cognitive Trading Intelligence
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class MetaLearningFeedback:
    """Feedback de meta-aprendizado a partir de resultados."""
    id: str = field(default_factory=lambda: f"mlf_{uuid.uuid4().hex[:12]}")
    decision_id: str = ""
    predicted_outcome: float = 0.0
    actual_outcome: float = 0.0
    calibration_error: float = 0.0
    learning_signal: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "predicted_outcome": self.predicted_outcome,
            "actual_outcome": self.actual_outcome,
            "calibration_error": self.calibration_error,
            "learning_signal": self.learning_signal,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class MetaLearningFeedbackEngine:
    """Captura feedback de decisões para calibrar meta-cognição."""

    def __init__(self):
        self._feedback: List[MetaLearningFeedback] = []

    def record_feedback(
        self,
        decision_id: str,
        predicted_outcome: float,
        actual_outcome: float,
    ) -> MetaLearningFeedback:
        calibration_error = abs(predicted_outcome - actual_outcome)
        learning_signal = max(0.0, 1.0 - calibration_error)
        recommendation = (
            "Recalibrate confidence model"
            if calibration_error > 0.3
            else "Maintain current calibration"
        )

        entry = MetaLearningFeedback(
            decision_id=decision_id,
            predicted_outcome=predicted_outcome,
            actual_outcome=actual_outcome,
            calibration_error=calibration_error,
            learning_signal=learning_signal,
            recommendation=recommendation,
        )
        self._feedback.append(entry)
        return entry

    def get_learning_dashboard(self) -> Dict[str, Any]:
        if not self._feedback:
            return {"status": "no_feedback"}

        return {
            "feedback_count": len(self._feedback),
            "avg_calibration_error": np.mean([f.calibration_error for f in self._feedback]),
            "avg_learning_signal": np.mean([f.learning_signal for f in self._feedback]),
            "recent_feedback": [f.to_dict() for f in self._feedback[-5:]],
        }
