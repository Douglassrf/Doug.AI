from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import threading


@dataclass
class MeshServiceInstance:
    id: str = field(default_factory=lambda: f"svc_{uuid.uuid4().hex[:12]}")
    name: str = ""
    version: str = "1.0.0"
    host: str = ""
    port: int = 0
    status: str = "healthy"
    load: float = 0.0
    health_score: float = 1.0
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "load": self.load,
            "health_score": self.health_score,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class ServiceRequest:
    id: str = field(default_factory=lambda: f"req_{uuid.uuid4().hex[:12]}")
    service: str = ""
    method: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timeout_seconds: float = 30.0
    retry_count: int = 0
    max_retries: int = 3
    status: str = "pending"
    response: Any = None
    error: Optional[str] = None
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "service": self.service,
            "method": self.method,
            "timeout_seconds": self.timeout_seconds,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "status": self.status,
            "response": self.response,
            "error": self.error,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
        }


class CognitiveServiceMesh:
    """Malha de serviços cognitiva — sem asyncio, routing por carga, circuit breaker."""

    def __init__(self) -> None:
        self._services: Dict[str, List[MeshServiceInstance]] = {}
        self._circuit_breakers: Dict[str, bool] = {}
        self._requests: Dict[str, ServiceRequest] = {}
        self._handlers: Dict[str, Callable] = {}
        self._lock = threading.Lock()

    def register_service(
        self,
        name: str,
        host: str,
        port: int,
        version: str = "1.0.0",
    ) -> MeshServiceInstance:
        instance = MeshServiceInstance(name=name, version=version, host=host, port=port)
        with self._lock:
            self._services.setdefault(name, []).append(instance)
        return instance

    def heartbeat(self, instance_id: str) -> bool:
        with self._lock:
            for instances in self._services.values():
                for inst in instances:
                    if inst.id == instance_id:
                        inst.last_heartbeat = datetime.now(timezone.utc)
                        return True
        return False

    def register_handler(self, service: str, method: str, handler: Callable) -> None:
        self._handlers[f"{service}:{method}"] = handler

    def call(
        self,
        service: str,
        method: str,
        payload: Dict[str, Any],
        timeout_seconds: float = 30.0,
        max_retries: int = 3,
    ) -> ServiceRequest:
        request = ServiceRequest(
            service=service,
            method=method,
            payload=payload,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )
        self._requests[request.id] = request

        if self._circuit_breakers.get(service, False):
            request.status = "failed"
            request.error = "Circuit breaker open"
            return request

        handler = self._handlers.get(f"{service}:{method}")
        if not handler:
            request.status = "failed"
            request.error = "Handler not found"
            return request

        instance = self._get_healthy_instance(service)
        if not instance:
            request.status = "failed"
            request.error = "No healthy instance available"
            return request

        for attempt in range(max_retries + 1):
            request.retry_count = attempt
            t0 = time.perf_counter()
            try:
                response = handler(payload)
                request.response = response
                request.status = "success"
                request.end_time = datetime.now(timezone.utc)
                request.duration_ms = (time.perf_counter() - t0) * 1000
                break
            except Exception as exc:
                request.error = str(exc)
                request.status = "failed"

        return request

    def _get_healthy_instance(self, service: str) -> Optional[MeshServiceInstance]:
        instances = self._services.get(service, [])
        now = datetime.now(timezone.utc)
        healthy = [
            i for i in instances
            if i.status == "healthy"
            and (now - i.last_heartbeat).total_seconds() < 30
        ]
        return min(healthy, key=lambda x: x.load) if healthy else None

    def open_circuit_breaker(self, service: str) -> None:
        self._circuit_breakers[service] = True

    def close_circuit_breaker(self, service: str) -> None:
        self._circuit_breakers[service] = False

    def get_service_status(self) -> Dict[str, Any]:
        return {
            svc: {
                "instances": len(insts),
                "healthy": sum(1 for i in insts if i.status == "healthy"),
                "circuit_breaker": self._circuit_breakers.get(svc, False),
            }
            for svc, insts in self._services.items()
        }
