from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np


@dataclass
class LatencyReport:
    module_name: str = ""
    avg_latency_ms: float = 0.0
    max_latency_ms: float = 0.0
    min_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    sample_count: int = 0
    threshold_breached: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "module_name": self.module_name,
            "avg_latency_ms": self.avg_latency_ms,
            "max_latency_ms": self.max_latency_ms,
            "min_latency_ms": self.min_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "sample_count": self.sample_count,
            "threshold_breached": self.threshold_breached,
            "created_at": self.created_at.isoformat(),
        }


class AdaptiveLatencyController:
    def __init__(self, max_latency_ms: float = 100.0):
        self._max_latency = max_latency_ms
        self._latency_history: Dict[str, List[float]] = {}
        self._reports: List[LatencyReport] = []
        self._slow_modules: Dict[str, int] = {}
        self._throttling_active: Dict[str, bool] = {}

    def record_latency(self, module_name: str, latency_ms: float) -> None:
        self._latency_history.setdefault(module_name, []).append(latency_ms)
        if len(self._latency_history[module_name]) > 1000:
            self._latency_history[module_name] = self._latency_history[module_name][-1000:]
        if latency_ms > self._max_latency:
            self._slow_modules[module_name] = self._slow_modules.get(module_name, 0) + 1
            if self._slow_modules[module_name] > 5:
                self._throttling_active[module_name] = True
        else:
            self._slow_modules[module_name] = 0
            self._throttling_active[module_name] = False

    def analyze(self) -> List[LatencyReport]:
        reports = []
        for module_name, latencies in self._latency_history.items():
            if not latencies: continue
            r = LatencyReport(
                module_name=module_name,
                avg_latency_ms=float(np.mean(latencies)),
                max_latency_ms=float(np.max(latencies)),
                min_latency_ms=float(np.min(latencies)),
                p95_latency_ms=float(np.percentile(latencies, 95)),
                sample_count=len(latencies),
                threshold_breached=latencies[-1] > self._max_latency,
            )
            reports.append(r)
            self._reports.append(r)
        return reports

    def predict_latency(self, module_name: str) -> float:
        latencies = self._latency_history.get(module_name, [])
        if not latencies: return 0.0
        if len(latencies) < 5: return float(np.mean(latencies))
        x = np.arange(len(latencies))
        slope, intercept = np.polyfit(x, latencies, 1)
        return float(max(slope * len(latencies) + intercept, 0.0))

    def get_slow_modules(self, threshold_ms: Optional[float] = None) -> List[str]:
        t = threshold_ms or self._max_latency
        return [m for m, lats in self._latency_history.items() if lats and float(np.mean(lats)) > t]

    def should_throttle(self, module_name: str) -> bool:
        return self._throttling_active.get(module_name, False)

    def get_recommendation(self, module_name: str) -> str:
        lats = self._latency_history.get(module_name, [])
        if not lats: return "No data available"
        avg = float(np.mean(lats))
        p95 = float(np.percentile(lats, 95))
        if avg > self._max_latency * 2: return "CRITICAL: Module severely underperforming. Immediate optimization required."
        if avg > self._max_latency * 1.5: return "HIGH: Module performing poorly. Consider reducing load or optimizing."
        if avg > self._max_latency: return "MEDIUM: Module exceeding latency threshold. Monitor closely."
        if p95 > self._max_latency * 1.5: return "LOW: Intermittent latency spikes detected. Investigate periodically."
        return "GOOD: Module performing within acceptable limits."
