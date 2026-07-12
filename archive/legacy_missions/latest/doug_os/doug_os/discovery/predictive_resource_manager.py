from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import numpy as np

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


@dataclass
class ResourcePrediction:
    id: str = field(default_factory=lambda: f"rp_{uuid.uuid4().hex[:12]}")
    resource_type: str = ""
    predicted_value: float = 0.0
    current_value: float = 0.0
    peak_value: float = 0.0
    confidence: float = 0.0
    horizon_minutes: int = 60
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "resource_type": self.resource_type,
            "predicted_value": self.predicted_value,
            "current_value": self.current_value,
            "peak_value": self.peak_value,
            "confidence": self.confidence,
            "horizon_minutes": self.horizon_minutes,
            "created_at": self.created_at.isoformat(),
        }


class PredictiveResourceManager:
    """Gerenciador preditivo de recursos com regressão linear via numpy."""

    _RESOURCE_TYPES = ("cpu", "memory", "queue", "thread", "io", "cache")

    def __init__(self) -> None:
        self._history: Dict[str, List[float]] = {rt: [] for rt in self._RESOURCE_TYPES}
        self._predictions: List[ResourcePrediction] = []

    def record_usage(self, resource_type: str, value: float) -> None:
        if resource_type not in self._history:
            self._history[resource_type] = []
        self._history[resource_type].append(value)
        if len(self._history[resource_type]) > 1000:
            self._history[resource_type] = self._history[resource_type][-1000:]

    def snapshot_system(self) -> Dict[str, float]:
        """Captura métricas reais se psutil disponível."""
        if not _HAS_PSUTIL:
            return {}
        snapshot: Dict[str, float] = {}
        try:
            snapshot["cpu"] = psutil.cpu_percent(interval=None) / 100.0
            vm = psutil.virtual_memory()
            snapshot["memory"] = vm.percent / 100.0
        except Exception:
            pass
        return snapshot

    def predict_resource(
        self,
        resource_type: str,
        horizon_minutes: int = 60,
    ) -> ResourcePrediction:
        history = self._history.get(resource_type, [])

        if len(history) < 2:
            pred = ResourcePrediction(
                resource_type=resource_type,
                predicted_value=float(np.mean(history)) if history else 0.0,
                current_value=history[-1] if history else 0.0,
                confidence=0.3,
                horizon_minutes=horizon_minutes,
            )
            self._predictions.append(pred)
            return pred

        x = np.arange(len(history), dtype=float)
        slope, intercept = np.polyfit(x, history, 1)
        future_idx = float(len(history) + horizon_minutes)
        predicted = float(slope * future_idx + intercept)

        variance = float(np.var(history))
        confidence = min(0.9, 1.0 / (1.0 + variance))

        pred = ResourcePrediction(
            resource_type=resource_type,
            predicted_value=max(0.0, predicted),
            current_value=float(history[-1]),
            peak_value=float(max(history)),
            confidence=confidence,
            horizon_minutes=horizon_minutes,
        )
        self._predictions.append(pred)
        return pred

    def get_auto_scaling_recommendation(self) -> Dict[str, Any]:
        recommendations: Dict[str, Any] = {}
        for rt in self._RESOURCE_TYPES:
            pred = self.predict_resource(rt, horizon_minutes=30)
            if pred.confidence > 0.5 and pred.current_value > 0:
                growth = (pred.predicted_value - pred.current_value) / (pred.current_value + 1e-9)
                if growth > 0.3:
                    recommendations[rt] = {
                        "action": "scale_up",
                        "reason": f"Predicted growth of {growth*100:.1f}%",
                        "priority": min(10, int(growth * 20)),
                    }
                elif growth < -0.3:
                    recommendations[rt] = {
                        "action": "scale_down",
                        "reason": f"Predicted decrease of {-growth*100:.1f}%",
                        "priority": int(-growth * 10),
                    }
        return recommendations

    def get_resource_dashboard(self) -> Dict[str, Any]:
        resource_summary: Dict[str, Any] = {}
        for rt in self._RESOURCE_TYPES:
            h = self._history[rt]
            resource_summary[rt] = {
                "current": float(h[-1]) if h else 0.0,
                "peak": float(max(h)) if h else 0.0,
                "trend": self._trend(h),
            }
        return {
            "resource_types": resource_summary,
            "predictions": [p.to_dict() for p in self._predictions[-10:]],
        }

    @staticmethod
    def _trend(history: List[float]) -> str:
        if len(history) < 10:
            return "stable"
        slope = (history[-1] - history[-10]) / 10
        if slope > 0.1:
            return "increasing"
        if slope < -0.1:
            return "decreasing"
        return "stable"
