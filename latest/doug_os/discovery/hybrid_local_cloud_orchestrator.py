from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class ExecutionDecision:
    id: str = field(default_factory=lambda: f"ed_{uuid.uuid4().hex[:12]}")
    task_id: str = ""
    task_type: str = ""
    target: str = "local"
    reason: str = ""
    estimated_cost: float = 0.0
    estimated_latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "task_type": self.task_type,
            "target": self.target,
            "reason": self.reason,
            "estimated_cost": self.estimated_cost,
            "estimated_latency_ms": self.estimated_latency_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ResourceUsage:
    cpu_percent: float = 0.0
    memory_percent: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class HybridLocalCloudOrchestrator:
    """Orquestrador híbrido local/cloud — decide onde executar tarefas com base em recursos e custo."""

    def __init__(
        self,
        local_cpu_threshold: float = 80.0,
        local_memory_threshold: float = 85.0,
        cloud_cost_per_unit: float = 0.01,
    ) -> None:
        self._decisions: List[ExecutionDecision] = []
        self._local_cpu_threshold = local_cpu_threshold
        self._local_memory_threshold = local_memory_threshold
        self._cloud_cost_per_unit = cloud_cost_per_unit
        self._local_usage = ResourceUsage()
        self._cloud_tasks: List[str] = []
        self._local_tasks: List[str] = []

    def update_local_resources(self, cpu_percent: float, memory_percent: float) -> None:
        self._local_usage = ResourceUsage(cpu_percent=cpu_percent, memory_percent=memory_percent)

    def route_task(
        self,
        task_type: str,
        cpu_required: float = 10.0,
        memory_required: float = 10.0,
        latency_sensitive: bool = False,
    ) -> ExecutionDecision:
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        local_ok = (
            self._local_usage.cpu_percent + cpu_required <= self._local_cpu_threshold
            and self._local_usage.memory_percent + memory_required <= self._local_memory_threshold
        )

        if latency_sensitive and local_ok:
            target = "local"
            reason = "Latency-sensitive task, local resources available"
            cost = 0.0
            latency_ms = 5.0
        elif local_ok:
            target = "local"
            reason = "Local resources available"
            cost = 0.0
            latency_ms = 10.0
        else:
            target = "cloud"
            reason = "Local resources saturated, offloading to cloud"
            cost = cpu_required * self._cloud_cost_per_unit
            latency_ms = 100.0

        decision = ExecutionDecision(
            task_id=task_id,
            task_type=task_type,
            target=target,
            reason=reason,
            estimated_cost=cost,
            estimated_latency_ms=latency_ms,
        )
        self._decisions.append(decision)
        if target == "cloud":
            self._cloud_tasks.append(task_id)
        else:
            self._local_tasks.append(task_id)
        return decision

    def get_routing_metrics(self) -> Dict[str, Any]:
        total = len(self._decisions)
        cloud_count = len(self._cloud_tasks)
        local_count = len(self._local_tasks)
        return {
            "total_tasks": total,
            "local_tasks": local_count,
            "cloud_tasks": cloud_count,
            "cloud_ratio": cloud_count / total if total else 0.0,
            "total_cost": sum(d.estimated_cost for d in self._decisions),
            "avg_latency_ms": sum(d.estimated_latency_ms for d in self._decisions) / total if total else 0.0,
        }

    def get_orchestration_dashboard(self) -> Dict[str, Any]:
        return {
            "local_resources": {
                "cpu_percent": self._local_usage.cpu_percent,
                "memory_percent": self._local_usage.memory_percent,
            },
            "routing_metrics": self.get_routing_metrics(),
            "recent_decisions": [d.to_dict() for d in self._decisions[-10:]],
        }
