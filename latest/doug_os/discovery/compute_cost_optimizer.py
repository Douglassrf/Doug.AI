from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid

try:
    import psutil
    _HAS_PSUTIL = True
except ImportError:
    _HAS_PSUTIL = False


@dataclass
class ComputeCost:
    id: str = field(default_factory=lambda: f"cc_{uuid.uuid4().hex[:12]}")
    operation: str = ""
    cpu_cost: float = 0.0
    memory_cost: float = 0.0
    time_cost_ms: float = 0.0
    priority: int = 5
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "cpu_cost": self.cpu_cost,
            "memory_cost": self.memory_cost,
            "time_cost_ms": self.time_cost_ms,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class CostBudget:
    cpu_budget: float = 100.0
    memory_budget: float = 100.0
    time_budget_ms: float = 10_000.0
    used_cpu: float = 0.0
    used_memory: float = 0.0
    used_time_ms: float = 0.0

    @property
    def remaining_cpu(self) -> float:
        return max(0.0, self.cpu_budget - self.used_cpu)

    @property
    def remaining_memory(self) -> float:
        return max(0.0, self.memory_budget - self.used_memory)

    @property
    def remaining_time_ms(self) -> float:
        return max(0.0, self.time_budget_ms - self.used_time_ms)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cpu_budget": self.cpu_budget,
            "memory_budget": self.memory_budget,
            "time_budget_ms": self.time_budget_ms,
            "used_cpu": self.used_cpu,
            "used_memory": self.used_memory,
            "used_time_ms": self.used_time_ms,
            "remaining_cpu": self.remaining_cpu,
            "remaining_memory": self.remaining_memory,
            "remaining_time_ms": self.remaining_time_ms,
        }


class ComputeCostOptimizer:
    """Otimizador de custo computacional com orçamento por operação e modo low-cost."""

    def __init__(self) -> None:
        self._costs: List[ComputeCost] = []
        self._budgets: Dict[str, CostBudget] = {}
        self._low_cost_mode = False

    def set_budget(self, operation: str, cpu: float, memory: float, time_ms: float) -> None:
        self._budgets[operation] = CostBudget(
            cpu_budget=cpu,
            memory_budget=memory,
            time_budget_ms=time_ms,
        )

    def record_cost(
        self,
        operation: str,
        cpu_cost: float = 0.0,
        memory_cost: float = 0.0,
        time_cost_ms: float = 0.0,
        priority: int = 5,
    ) -> ComputeCost:
        cost = ComputeCost(
            operation=operation,
            cpu_cost=cpu_cost,
            memory_cost=memory_cost,
            time_cost_ms=time_cost_ms,
            priority=priority,
        )
        self._costs.append(cost)

        if operation in self._budgets:
            b = self._budgets[operation]
            b.used_cpu += cpu_cost
            b.used_memory += memory_cost
            b.used_time_ms += time_cost_ms

        return cost

    def check_budget(self, operation: str) -> bool:
        if operation not in self._budgets:
            return True
        b = self._budgets[operation]
        return b.used_cpu <= b.cpu_budget and b.used_memory <= b.memory_budget and b.used_time_ms <= b.time_budget_ms

    def snapshot_system(self) -> Dict[str, float]:
        if not _HAS_PSUTIL:
            return {}
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory_percent": psutil.virtual_memory().percent,
            }
        except Exception:
            return {}

    def get_cost_metrics(self, operation: Optional[str] = None) -> Dict[str, Any]:
        costs = [c for c in self._costs if operation is None or c.operation == operation]
        if not costs:
            return {"status": "no_data"}
        return {
            "total_cpu": sum(c.cpu_cost for c in costs),
            "total_memory": sum(c.memory_cost for c in costs),
            "total_time_ms": sum(c.time_cost_ms for c in costs),
            "avg_cpu": sum(c.cpu_cost for c in costs) / len(costs),
            "avg_time_ms": sum(c.time_cost_ms for c in costs) / len(costs),
            "count": len(costs),
        }

    def enable_low_cost_mode(self) -> None:
        self._low_cost_mode = True

    def disable_low_cost_mode(self) -> None:
        self._low_cost_mode = False

    def get_cost_dashboard(self) -> Dict[str, Any]:
        return {
            "low_cost_mode": self._low_cost_mode,
            "total_operations": len(self._costs),
            "budgets": {k: v.to_dict() for k, v in self._budgets.items()},
            "metrics": self.get_cost_metrics(),
        }
