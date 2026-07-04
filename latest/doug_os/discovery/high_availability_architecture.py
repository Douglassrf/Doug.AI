from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import threading


@dataclass
class ServiceInstance:
    id: str = field(default_factory=lambda: f"si_{uuid.uuid4().hex[:12]}")
    service_name: str = ""
    host: str = ""
    port: int = 0
    status: str = "healthy"
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    uptime_seconds: float = 0.0
    health_score: float = 1.0
    replicas: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "service_name": self.service_name,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": self.uptime_seconds,
            "health_score": self.health_score,
            "replicas": self.replicas,
        }


@dataclass
class AvailabilityReport:
    service_name: str = ""
    total_instances: int = 0
    healthy_instances: int = 0
    availability_score: float = 0.0
    uptime_percentage: float = 0.0
    degraded_services: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "service_name": self.service_name,
            "total_instances": self.total_instances,
            "healthy_instances": self.healthy_instances,
            "availability_score": self.availability_score,
            "uptime_percentage": self.uptime_percentage,
            "degraded_services": self.degraded_services,
            "created_at": self.created_at.isoformat(),
        }


class HighAvailabilityArchitecture:
    """Arquitetura de alta disponibilidade com redundância, failover e degradação graciosa."""

    def __init__(self) -> None:
        self._services: Dict[str, List[ServiceInstance]] = {}
        self._reports: List[AvailabilityReport] = []
        self._lock = threading.Lock()

    def register_service(self, service_name: str, host: str, port: int) -> ServiceInstance:
        instance = ServiceInstance(service_name=service_name, host=host, port=port)
        with self._lock:
            self._services.setdefault(service_name, []).append(instance)
        return instance

    def heartbeat(self, instance_id: str) -> bool:
        with self._lock:
            for instances in self._services.values():
                for inst in instances:
                    if inst.id == instance_id:
                        now = datetime.now(timezone.utc)
                        inst.last_heartbeat = now
                        inst.uptime_seconds = (now - inst.start_time).total_seconds()
                        return True
        return False

    def check_health(self, service_name: str) -> AvailabilityReport:
        instances = self._services.get(service_name, [])
        if not instances:
            return AvailabilityReport(service_name=service_name)

        now = datetime.now(timezone.utc)
        healthy = 0
        degraded: List[str] = []

        for inst in instances:
            age = (now - inst.last_heartbeat).total_seconds()
            if age > 30:
                inst.status = "unhealthy"
                inst.health_score = max(0.0, inst.health_score - 0.1)
            elif inst.health_score < 0.5:
                inst.status = "degraded"
            else:
                inst.status = "healthy"
                healthy += 1

            if inst.status in ("degraded", "unhealthy"):
                degraded.append(inst.id)

        availability = healthy / len(instances)
        report = AvailabilityReport(
            service_name=service_name,
            total_instances=len(instances),
            healthy_instances=healthy,
            availability_score=availability,
            uptime_percentage=availability * 100,
            degraded_services=degraded,
        )
        self._reports.append(report)
        return report

    def failover(self, service_name: str, instance_id: str) -> Optional[ServiceInstance]:
        instances = self._services.get(service_name, [])
        for inst in instances:
            if inst.id == instance_id:
                inst.status = "offline"
                break

        return next(
            (i for i in instances if i.id != instance_id and i.status == "healthy"),
            None,
        )

    def graceful_degradation(self, service_name: str) -> List[str]:
        degraded: List[str] = []
        for inst in self._services.get(service_name, []):
            if inst.health_score < 0.3:
                inst.status = "offline"
                degraded.append(inst.id)
            elif inst.health_score < 0.6:
                inst.status = "degraded"
                degraded.append(inst.id)
        return degraded

    def get_availability_score(self) -> Dict[str, float]:
        return {svc: self.check_health(svc).availability_score for svc in self._services}

    def get_reports(self, limit: int = 10) -> List[AvailabilityReport]:
        return self._reports[-limit:]
