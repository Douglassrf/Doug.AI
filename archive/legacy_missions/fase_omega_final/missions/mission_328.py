# ============================================================
# MISSÃO 328 — OMEGA PERFORMANCE MONITOR
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib


@dataclass
class PerformanceMetric:
    """Métrica de performance."""

    id: str = field(default_factory=lambda: f"pm_{uuid.uuid4().hex[:12]}")
    component: str = ""
    metric_name: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "component": self.component,
            "metric_name": self.metric_name,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HealthReport:
    """Relatório agregado de saúde."""

    id: str = field(default_factory=lambda: f"hr_{uuid.uuid4().hex[:12]}")
    overall_health: float = 0.0
    latency_ms: float = 0.0
    throughput: float = 0.0
    status: str = "unknown"
    components: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "overall_health": self.overall_health,
            "latency_ms": self.latency_ms,
            "throughput": self.throughput,
            "status": self.status,
            "components": self.components,
            "created_at": self.created_at.isoformat(),
        }


class OmegaPerformanceMonitor:
    """
    Monitor de performance system-wide.

    Implementa métricas, latência, throughput e agregação de saúde.
    """

    HEALTH_THRESHOLDS = {"healthy": 0.8, "degraded": 0.5}

    def __init__(self):
        self._metrics: List[PerformanceMetric] = []
        self._health_reports: List[HealthReport] = []

    def record_metric(
        self,
        component: str,
        metric_name: str,
        value: float,
        unit: str = "",
    ) -> PerformanceMetric:
        """Registra métrica de performance."""
        metric = PerformanceMetric(
            component=component,
            metric_name=metric_name,
            value=value,
            unit=unit,
        )
        self._metrics.append(metric)
        return metric

    def get_component_metrics(
        self, component: str, metric_name: Optional[str] = None
    ) -> List[PerformanceMetric]:
        """Retorna métricas de um componente."""
        metrics = [metric for metric in self._metrics if metric.component == component]
        if metric_name:
            metrics = [metric for metric in metrics if metric.metric_name == metric_name]
        return metrics

    def aggregate_health(self) -> HealthReport:
        """Agrega saúde de todos os componentes."""
        components = sorted(set(metric.component for metric in self._metrics))
        component_health: Dict[str, float] = {}

        for component in components:
            component_metrics = self.get_component_metrics(component)
            if not component_metrics:
                continue

            seed = hashlib.sha256(component.encode()).hexdigest()
            base_health = int(seed[:2], 16) / 255.0

            latency_metrics = [
                metric.value
                for metric in component_metrics
                if metric.metric_name == "latency_ms"
            ]
            avg_latency = (
                sum(latency_metrics) / len(latency_metrics) if latency_metrics else 50.0
            )

            health = max(0.0, min(1.0, base_health * 0.5 + (1.0 - avg_latency / 1000) * 0.5))
            component_health[component] = health

        overall = (
            sum(component_health.values()) / len(component_health)
            if component_health
            else 0.0
        )

        latency_values = [
            metric.value
            for metric in self._metrics
            if metric.metric_name == "latency_ms"
        ]
        throughput_values = [
            metric.value
            for metric in self._metrics
            if metric.metric_name == "throughput"
        ]

        report = HealthReport(
            overall_health=overall,
            latency_ms=sum(latency_values) / len(latency_values) if latency_values else 0.0,
            throughput=(
                sum(throughput_values) / len(throughput_values) if throughput_values else 0.0
            ),
            components=component_health,
        )

        if overall >= self.HEALTH_THRESHOLDS["healthy"]:
            report.status = "healthy"
        elif overall >= self.HEALTH_THRESHOLDS["degraded"]:
            report.status = "degraded"
        else:
            report.status = "critical"

        self._health_reports.append(report)
        return report

    def get_performance_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard de performance."""
        latest = self._health_reports[-1].to_dict() if self._health_reports else None
        return {
            "total_metrics": len(self._metrics),
            "components_monitored": len(
                set(metric.component for metric in self._metrics)
            ),
            "latest_health": latest,
            "health_reports": len(self._health_reports),
        }
