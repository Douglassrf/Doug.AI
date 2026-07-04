from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import threading
import numpy as np

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


@dataclass
class PerformanceMetric:
    id: str = field(default_factory=lambda: f"pm_{uuid.uuid4().hex[:12]}")
    module: str = ""
    metric_type: str = ""
    value: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    threshold: float = 0.0
    alert_level: str = "green"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "module": self.module, "metric_type": self.metric_type,
            "value": self.value, "timestamp": self.timestamp.isoformat(),
            "threshold": self.threshold, "alert_level": self.alert_level,
        }


@dataclass
class OptimizationRecommendation:
    id: str = field(default_factory=lambda: f"opt_{uuid.uuid4().hex[:12]}")
    module: str = ""
    issue: str = ""
    recommendation: str = ""
    estimated_improvement: float = 0.0
    priority: int = 5
    implemented: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "module": self.module, "issue": self.issue,
            "recommendation": self.recommendation,
            "estimated_improvement": self.estimated_improvement,
            "priority": self.priority, "implemented": self.implemented,
            "created_at": self.created_at.isoformat(),
        }


class CognitivePerformanceOptimizer:
    def __init__(self):
        self._metrics: List[PerformanceMetric] = []
        self._recommendations: List[OptimizationRecommendation] = []
        self._monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self) -> None:
        if self._monitoring:
            return
        self._monitoring = True
        self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        self._monitoring = False
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)

    def _monitor_loop(self) -> None:
        while self._monitoring:
            try:
                self._collect_sample()
                self._analyze_bottlenecks()
                self._generate_recommendations()
                time.sleep(1)
            except Exception:
                time.sleep(1)

    def _collect_sample(self) -> None:
        if _HAS_PSUTIL:
            cpu_val = psutil.cpu_percent(interval=None)
            mem_val = psutil.virtual_memory().percent
        else:
            cpu_val = 50.0
            mem_val = 60.0
        cpu_level = "red" if cpu_val > 80 else ("yellow" if cpu_val > 60 else "green")
        mem_level = "red" if mem_val > 85 else ("yellow" if mem_val > 70 else "green")
        self._record_metric("system", "cpu", cpu_val, 80.0, cpu_level)
        self._record_metric("system", "memory", mem_val, 85.0, mem_level)

    def _record_metric(self, module: str, metric_type: str, value: float,
                       threshold: float, alert_level: str) -> None:
        self._metrics.append(PerformanceMetric(
            module=module, metric_type=metric_type, value=value,
            threshold=threshold, alert_level=alert_level,
        ))

    def record_metric(self, module: str, metric_type: str, value: float,
                      threshold: float = 80.0) -> PerformanceMetric:
        alert = "red" if value > threshold else ("yellow" if value > threshold * 0.75 else "green")
        m = PerformanceMetric(module=module, metric_type=metric_type,
                              value=value, threshold=threshold, alert_level=alert)
        self._metrics.append(m)
        return m

    def _analyze_bottlenecks(self) -> None:
        cpu_red = [m for m in self._metrics if m.metric_type == "cpu" and m.alert_level == "red"]
        if len(cpu_red) > 5:
            self._recommendations.append(OptimizationRecommendation(
                module="system", issue="High CPU usage",
                recommendation="Scale horizontally or optimize CPU-intensive operations",
                estimated_improvement=0.3, priority=8,
            ))
        mem_red = [m for m in self._metrics if m.metric_type == "memory" and m.alert_level == "red"]
        if len(mem_red) > 5:
            self._recommendations.append(OptimizationRecommendation(
                module="system", issue="High memory usage",
                recommendation="Optimize memory usage or increase available memory",
                estimated_improvement=0.2, priority=7,
            ))

    def _generate_recommendations(self) -> None:
        recent = self._metrics[-10:]
        reds = [m for m in recent if m.alert_level == "red"]
        if len(reds) > 3:
            self._recommendations.append(OptimizationRecommendation(
                module="system", issue="Multiple red alerts",
                recommendation="Performance crisis — immediate optimization required",
                estimated_improvement=0.5, priority=10,
            ))

    def get_metrics(self, module: Optional[str] = None, metric_type: Optional[str] = None,
                    limit: int = 100) -> List[PerformanceMetric]:
        filtered = self._metrics
        if module: filtered = [m for m in filtered if m.module == module]
        if metric_type: filtered = [m for m in filtered if m.metric_type == metric_type]
        return filtered[-limit:]

    def get_recommendations(self, priority_threshold: int = 5) -> List[OptimizationRecommendation]:
        return [r for r in self._recommendations if r.priority >= priority_threshold and not r.implemented]

    def implement_recommendation(self, recommendation_id: str) -> bool:
        for r in self._recommendations:
            if r.id == recommendation_id:
                r.implemented = True
                return True
        return False

    def get_performance_summary(self) -> Dict[str, Any]:
        if not self._metrics:
            return {"status": "no_data"}
        recent = self._metrics[-60:]
        cpu_vals = [m.value for m in recent if m.metric_type == "cpu"]
        mem_vals = [m.value for m in recent if m.metric_type == "memory"]
        return {
            "avg_cpu": float(np.mean(cpu_vals)) if cpu_vals else 0.0,
            "avg_memory": float(np.mean(mem_vals)) if mem_vals else 0.0,
            "red_alerts": sum(1 for m in recent if m.alert_level == "red"),
            "yellow_alerts": sum(1 for m in recent if m.alert_level == "yellow"),
            "pending_recommendations": len([r for r in self._recommendations if not r.implemented]),
        }
