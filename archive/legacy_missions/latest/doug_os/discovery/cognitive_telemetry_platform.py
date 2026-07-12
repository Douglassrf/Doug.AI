from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class TelemetryPoint:
    id: str = field(default_factory=lambda: f"tp_{uuid.uuid4().hex[:12]}")
    source: str = ""
    metric_type: str = ""
    name: str = ""
    value: Any = None
    tags: Dict[str, str] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    severity: str = "info"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source": self.source,
            "metric_type": self.metric_type,
            "name": self.name,
            "value": self.value,
            "tags": self.tags,
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
        }


class CognitiveTelemetryPlatform:
    """Plataforma de telemetria cognitiva — métricas, logs, traces, performance."""

    def __init__(self, max_points: int = 10_000) -> None:
        self._points: List[TelemetryPoint] = []
        self._max_points = max_points
        self._metrics: Dict[str, List[float]] = {}
        self._logs: List[Dict[str, Any]] = []

    def collect(self, point: TelemetryPoint) -> None:
        self._points.append(point)
        if len(self._points) > self._max_points:
            self._points = self._points[-self._max_points:]

        if point.metric_type == "metric" and isinstance(point.value, (int, float)):
            bucket = self._metrics.setdefault(point.name, [])
            bucket.append(float(point.value))
            if len(bucket) > 1000:
                self._metrics[point.name] = bucket[-1000:]

        if point.metric_type == "log":
            self._logs.append(point.to_dict())
            if len(self._logs) > 1000:
                self._logs = self._logs[-1000:]

    def record_metric(self, name: str, value: float, source: str = "system", tags: Optional[Dict[str, str]] = None) -> TelemetryPoint:
        point = TelemetryPoint(source=source, metric_type="metric", name=name, value=value, tags=tags or {})
        self.collect(point)
        return point

    def record_log(self, message: str, source: str = "system", severity: str = "info") -> TelemetryPoint:
        point = TelemetryPoint(source=source, metric_type="log", name="log", value=message, severity=severity)
        self.collect(point)
        return point

    def get_metric(self, name: str, last_n: int = 100) -> List[float]:
        return self._metrics.get(name, [])[-last_n:]

    def get_metrics_summary(self) -> Dict[str, Any]:
        summary: Dict[str, Any] = {}
        for name, values in self._metrics.items():
            if values:
                summary[name] = {
                    "count": len(values),
                    "min": min(values),
                    "max": max(values),
                    "avg": sum(values) / len(values),
                    "last": values[-1],
                }
        return summary

    def get_logs(self, severity: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        filtered = self._logs
        if severity:
            filtered = [l for l in filtered if l.get("severity") == severity]
        return filtered[-limit:]

    def get_dashboard(self) -> Dict[str, Any]:
        total = len(self._points)
        return {
            "total_points": total,
            "metric_points": sum(1 for p in self._points if p.metric_type == "metric"),
            "log_points": sum(1 for p in self._points if p.metric_type == "log"),
            "trace_points": sum(1 for p in self._points if p.metric_type == "trace"),
            "unique_metrics": len(self._metrics),
            "metrics_summary": self.get_metrics_summary(),
            "recent_logs": self.get_logs(limit=10),
        }
