"""Mission 343 — System Health Monitor: monitora saúde de todos os componentes em tempo real."""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import threading
import time


STATUS_HEALTHY   = "healthy"
STATUS_DEGRADED  = "degraded"
STATUS_CRITICAL  = "critical"
STATUS_OFFLINE   = "offline"


@dataclass
class ComponentHealth:
    component_id: str = ""
    component_type: str = "agent"       # agent | module | pipeline | infra
    status: str = STATUS_HEALTHY
    latency_ms: float = 0.0
    error_rate: float = 0.0
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    consecutive_failures: int = 0
    alerts: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "component_id": self.component_id,
            "component_type": self.component_type,
            "status": self.status,
            "latency_ms": round(self.latency_ms, 2),
            "error_rate": round(self.error_rate, 4),
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "consecutive_failures": self.consecutive_failures,
            "alerts": self.alerts,
        }


@dataclass
class HealthReport:
    id: str = field(default_factory=lambda: f"hr_{uuid.uuid4().hex[:12]}")
    overall_status: str = STATUS_HEALTHY
    healthy_count: int = 0
    degraded_count: int = 0
    critical_count: int = 0
    offline_count: int = 0
    components: List[ComponentHealth] = field(default_factory=list)
    degraded_mode_active: bool = False
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "overall_status": self.overall_status,
            "healthy_count": self.healthy_count,
            "degraded_count": self.degraded_count,
            "critical_count": self.critical_count,
            "offline_count": self.offline_count,
            "degraded_mode_active": self.degraded_mode_active,
            "generated_at": self.generated_at.isoformat(),
            "components": [c.to_dict() for c in self.components],
        }


class SystemHealthMonitor:
    """
    Monitora saúde de todos os componentes do DOUG.AI.

    - Recebe heartbeats e métricas de latência / error_rate
    - Classifica cada componente: healthy → degraded → critical → offline
    - Ativa modo degradado automaticamente se componente crítico falha
    - Gera alertas para SLA violations

    SLA defaults:
        latency_sla_ms  = 500ms
        error_rate_sla  = 0.05 (5%)
        heartbeat_timeout_s = 60s
    """

    def __init__(
        self,
        latency_sla_ms: float = 500.0,
        error_rate_sla: float = 0.05,
        heartbeat_timeout_s: float = 60.0,
        critical_components: Optional[List[str]] = None,
    ) -> None:
        self._latency_sla_ms = latency_sla_ms
        self._error_rate_sla = error_rate_sla
        self._heartbeat_timeout_s = heartbeat_timeout_s
        self._critical_components = set(critical_components or [])
        self._components: Dict[str, ComponentHealth] = {}
        self._reports: List[HealthReport] = []
        self._degraded_mode = False
        self._lock = threading.Lock()

    # ------------------------------------------------------------------ #
    #  Registration                                                        #
    # ------------------------------------------------------------------ #

    def register(
        self,
        component_id: str,
        component_type: str = "agent",
        is_critical: bool = False,
    ) -> ComponentHealth:
        with self._lock:
            health = ComponentHealth(
                component_id=component_id,
                component_type=component_type,
            )
            self._components[component_id] = health
            if is_critical:
                self._critical_components.add(component_id)
            return health

    # ------------------------------------------------------------------ #
    #  Heartbeat & metrics                                                 #
    # ------------------------------------------------------------------ #

    def heartbeat(
        self,
        component_id: str,
        latency_ms: float = 0.0,
        error_rate: float = 0.0,
    ) -> ComponentHealth:
        with self._lock:
            if component_id not in self._components:
                self.register(component_id)

            h = self._components[component_id]
            h.last_heartbeat = datetime.now(timezone.utc)
            h.latency_ms = latency_ms
            h.error_rate = error_rate
            h.alerts = []

            # Classifica status
            if latency_ms > self._latency_sla_ms * 3 or error_rate > 0.30:
                h.status = STATUS_CRITICAL
                h.consecutive_failures += 1
                h.alerts.append(f"CRITICAL: latency={latency_ms:.0f}ms error_rate={error_rate:.2%}")
            elif latency_ms > self._latency_sla_ms or error_rate > self._error_rate_sla:
                h.status = STATUS_DEGRADED
                h.consecutive_failures += 1
                h.alerts.append(f"SLA violation: latency={latency_ms:.0f}ms error_rate={error_rate:.2%}")
            else:
                h.status = STATUS_HEALTHY
                h.consecutive_failures = 0

            return h

    def record_failure(self, component_id: str, reason: str = "") -> ComponentHealth:
        with self._lock:
            if component_id not in self._components:
                self.register(component_id)
            h = self._components[component_id]
            h.consecutive_failures += 1
            h.status = STATUS_CRITICAL if h.consecutive_failures >= 3 else STATUS_DEGRADED
            if reason:
                h.alerts.append(reason)
            return h

    # ------------------------------------------------------------------ #
    #  Health check                                                        #
    # ------------------------------------------------------------------ #

    def check_heartbeat_timeouts(self) -> List[str]:
        """Marca como offline componentes que não enviaram heartbeat recentemente."""
        timed_out = []
        now = datetime.now(timezone.utc)
        with self._lock:
            for cid, h in self._components.items():
                elapsed = (now - h.last_heartbeat).total_seconds()
                if elapsed > self._heartbeat_timeout_s and h.status != STATUS_OFFLINE:
                    h.status = STATUS_OFFLINE
                    h.alerts.append(f"Heartbeat timeout: {elapsed:.0f}s sem sinal")
                    timed_out.append(cid)
        return timed_out

    def generate_report(self) -> HealthReport:
        with self._lock:
            components = list(self._components.values())

        counts = {STATUS_HEALTHY: 0, STATUS_DEGRADED: 0, STATUS_CRITICAL: 0, STATUS_OFFLINE: 0}
        for c in components:
            counts[c.status] = counts.get(c.status, 0) + 1

        # Modo degradado: qualquer componente crítico offline ou critical
        critical_down = any(
            c.component_id in self._critical_components and c.status in (STATUS_CRITICAL, STATUS_OFFLINE)
            for c in components
        )

        with self._lock:
            self._degraded_mode = critical_down

        # Status global
        if counts[STATUS_OFFLINE] > 0 or counts[STATUS_CRITICAL] > 0:
            overall = STATUS_CRITICAL
        elif counts[STATUS_DEGRADED] > 0:
            overall = STATUS_DEGRADED
        else:
            overall = STATUS_HEALTHY

        report = HealthReport(
            overall_status=overall,
            healthy_count=counts[STATUS_HEALTHY],
            degraded_count=counts[STATUS_DEGRADED],
            critical_count=counts[STATUS_CRITICAL],
            offline_count=counts[STATUS_OFFLINE],
            components=list(components),
            degraded_mode_active=critical_down,
        )
        self._reports.append(report)
        return report

    # ------------------------------------------------------------------ #
    #  Degraded mode                                                       #
    # ------------------------------------------------------------------ #

    @property
    def is_degraded_mode(self) -> bool:
        return self._degraded_mode

    def get_active_alerts(self) -> List[Dict[str, Any]]:
        alerts = []
        with self._lock:
            for h in self._components.values():
                for alert in h.alerts:
                    alerts.append({"component": h.component_id, "status": h.status, "alert": alert})
        return alerts

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            components = list(self._components.values())
        if not components:
            return {"total_components": 0}
        by_status = {STATUS_HEALTHY: 0, STATUS_DEGRADED: 0, STATUS_CRITICAL: 0, STATUS_OFFLINE: 0}
        for c in components:
            by_status[c.status] = by_status.get(c.status, 0) + 1
        return {
            "total_components": len(components),
            "by_status": by_status,
            "degraded_mode": self._degraded_mode,
            "critical_components": list(self._critical_components),
            "total_reports": len(self._reports),
        }
