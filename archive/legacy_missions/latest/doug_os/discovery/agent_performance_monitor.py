from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class PerformanceSnapshot:
    id: str = field(default_factory=lambda: f"snap_{uuid.uuid4().hex[:12]}")
    agent_id: str = ""
    tasks_completed: int = 0
    tasks_failed: int = 0
    avg_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0
    throughput_per_min: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage_mb: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_id": self.agent_id,
            "tasks_completed": self.tasks_completed,
            "tasks_failed": self.tasks_failed,
            "avg_latency_ms": self.avg_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "throughput_per_min": self.throughput_per_min,
            "error_rate": self.error_rate,
            "cpu_usage": self.cpu_usage,
            "memory_usage_mb": self.memory_usage_mb,
            "timestamp": self.timestamp.isoformat(),
        }


class AgentPerformanceMonitor:
    """Monitor de performance de agentes — latências, throughput, alertas, SLAs."""

    def __init__(self, latency_sla_ms: float = 500.0, error_rate_sla: float = 0.05) -> None:
        self._snapshots: Dict[str, List[PerformanceSnapshot]] = {}
        self._latencies: Dict[str, List[float]] = {}
        self._latency_sla_ms = latency_sla_ms
        self._error_rate_sla = error_rate_sla
        self._alerts: List[Dict[str, Any]] = []

    def record_task(
        self,
        agent_id: str,
        latency_ms: float,
        success: bool = True,
        cpu_usage: float = 0.0,
        memory_mb: float = 0.0,
    ) -> None:
        self._latencies.setdefault(agent_id, []).append(latency_ms)
        if len(self._latencies[agent_id]) > 1000:
            self._latencies[agent_id] = self._latencies[agent_id][-1000:]

        if latency_ms > self._latency_sla_ms:
            self._alerts.append({
                "agent_id": agent_id,
                "type": "latency_sla_breach",
                "value": latency_ms,
                "threshold": self._latency_sla_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    def snapshot(self, agent_id: str, tasks_completed: int, tasks_failed: int) -> PerformanceSnapshot:
        latencies = self._latencies.get(agent_id, [])
        avg_lat = float(np.mean(latencies)) if latencies else 0.0
        p99_lat = float(np.percentile(latencies, 99)) if len(latencies) >= 2 else avg_lat
        total = tasks_completed + tasks_failed
        error_rate = tasks_failed / total if total > 0 else 0.0

        if error_rate > self._error_rate_sla:
            self._alerts.append({
                "agent_id": agent_id,
                "type": "error_rate_sla_breach",
                "value": error_rate,
                "threshold": self._error_rate_sla,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

        snap = PerformanceSnapshot(
            agent_id=agent_id,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            avg_latency_ms=avg_lat,
            p99_latency_ms=p99_lat,
            error_rate=error_rate,
        )
        self._snapshots.setdefault(agent_id, []).append(snap)
        return snap

    def get_snapshots(self, agent_id: str, limit: int = 10) -> List[PerformanceSnapshot]:
        return self._snapshots.get(agent_id, [])[-limit:]

    def get_alerts(self, agent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if agent_id:
            return [a for a in self._alerts if a["agent_id"] == agent_id]
        return self._alerts

    def is_sla_met(self, agent_id: str) -> bool:
        latencies = self._latencies.get(agent_id, [])
        if not latencies:
            return True
        return float(np.mean(latencies)) <= self._latency_sla_ms

    def get_monitor_dashboard(self) -> Dict[str, Any]:
        return {
            "monitored_agents": len(self._snapshots),
            "total_alerts": len(self._alerts),
            "latency_breaches": sum(1 for a in self._alerts if a["type"] == "latency_sla_breach"),
            "error_rate_breaches": sum(1 for a in self._alerts if a["type"] == "error_rate_sla_breach"),
            "agents": list(self._snapshots.keys()),
        }
