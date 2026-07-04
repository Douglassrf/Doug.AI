from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class FaultRecord:
    id: str = field(default_factory=lambda: f"fr_{uuid.uuid4().hex[:12]}")
    component: str = ""
    fault_type: str = ""
    severity: str = "medium"
    description: str = ""
    recovery_action: str = ""
    recovered: bool = False
    recovery_time_ms: float = 0.0
    occurred_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "component": self.component, "fault_type": self.fault_type,
            "severity": self.severity, "description": self.description,
            "recovery_action": self.recovery_action, "recovered": self.recovered,
            "recovery_time_ms": self.recovery_time_ms,
            "occurred_at": self.occurred_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }


@dataclass
class HealthStatus:
    component: str = ""
    status: str = "healthy"
    stability_score: float = 1.0
    uptime_seconds: float = 0.0
    failure_count: int = 0
    last_check: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component": self.component, "status": self.status,
            "stability_score": self.stability_score, "uptime_seconds": self.uptime_seconds,
            "failure_count": self.failure_count, "last_check": self.last_check.isoformat(),
        }


class CognitiveFaultTolerance:
    _SEVERITIES = {"crash": "critical", "timeout": "high", "memory": "high",
                   "dependency": "medium", "network": "medium"}
    _RECOVERY_ACTIONS = {"crash": "restart_component", "timeout": "increase_timeout",
                         "memory": "clear_cache_and_restart", "dependency": "check_dependency_health",
                         "network": "reconnect_network"}

    def __init__(self):
        self._faults: List[FaultRecord] = []
        self._health: Dict[str, HealthStatus] = {}
        self._isolated_modules: Set[str] = set()

    def register_component(self, component: str) -> None:
        self._health[component] = HealthStatus(component=component)

    def detect_failure(self, component: str, fault_type: str, description: str) -> FaultRecord:
        severity = self._SEVERITIES.get(fault_type, "medium")
        fault = FaultRecord(component=component, fault_type=fault_type,
                            severity=severity, description=description)
        self._faults.append(fault)
        self._update_health(component, "failed")
        if severity in ("critical", "high"):
            self._isolated_modules.add(component)
        fault.recovery_action = self._RECOVERY_ACTIONS.get(fault_type, "manual_recovery_required")
        return fault

    def _update_health(self, component: str, status: str) -> None:
        if component in self._health:
            h = self._health[component]
            h.status = status
            h.last_check = datetime.now(timezone.utc)
            h.failure_count += 1
            h.stability_score = max(0.0, h.stability_score - 0.1)

    def recover_component(self, component: str) -> bool:
        if component not in self._health:
            return False
        h = self._health[component]
        h.status = "recovering"
        h.stability_score = min(1.0, h.stability_score + 0.2)
        self._isolated_modules.discard(component)
        h.status = "healthy"
        return True

    def is_component_isolated(self, component: str) -> bool:
        return component in self._isolated_modules

    def get_health_status(self, component: str) -> Optional[HealthStatus]:
        return self._health.get(component)

    def get_stability_score(self, component: str) -> float:
        return self._health[component].stability_score if component in self._health else 1.0

    def get_failure_analytics(self) -> Dict[str, Any]:
        if not self._faults:
            return {"status": "no_faults"}
        by_type: Dict[str, int] = {}
        for f in self._faults:
            by_type[f.fault_type] = by_type.get(f.fault_type, 0) + 1
        recovered = [f for f in self._faults if f.recovered]
        return {
            "total_faults": len(self._faults),
            "recovered_faults": len(recovered),
            "by_type": by_type,
            "avg_recovery_ms": float(np.mean([f.recovery_time_ms for f in recovered])) if recovered else 0.0,
            "isolated_components": list(self._isolated_modules),
        }
