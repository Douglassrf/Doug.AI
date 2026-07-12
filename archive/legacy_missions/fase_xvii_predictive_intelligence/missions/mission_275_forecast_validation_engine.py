# ============================================================
# MISSÃO 275 — FORECAST VALIDATION ENGINE (stub mínimo)
# Fase XVII — Predictive Intelligence Architecture
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class ValidationReport:
    """Relatório de validação de previsão."""
    id: str = field(default_factory=lambda: f"vr_{uuid.uuid4().hex[:12]}")
    forecast_id: str = ""
    predicted_value: float = 0.0
    actual_value: float = 0.0
    error: float = 0.0
    accuracy_score: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "forecast_id": self.forecast_id,
            "predicted_value": self.predicted_value,
            "actual_value": self.actual_value,
            "error": self.error,
            "accuracy_score": self.accuracy_score,
            "created_at": self.created_at.isoformat(),
        }


class ForecastValidationEngine:
    """Valida previsões contra resultados reais."""

    def __init__(self):
        self._reports: List[ValidationReport] = []

    def validate(self, forecast_id: str, predicted: float, actual: float) -> ValidationReport:
        error = abs(predicted - actual)
        accuracy = max(0.0, 1.0 - error / max(abs(actual), 1e-9))

        report = ValidationReport(
            forecast_id=forecast_id,
            predicted_value=predicted,
            actual_value=actual,
            error=error,
            accuracy_score=accuracy,
        )
        self._reports.append(report)
        return report

    def get_validation_dashboard(self) -> Dict[str, Any]:
        scores = [r.accuracy_score for r in self._reports]
        return {
            "validations": len(self._reports),
            "avg_accuracy": float(np.mean(scores)) if scores else 0,
            "avg_error": float(np.mean([r.error for r in self._reports])) if self._reports else 0,
        }
