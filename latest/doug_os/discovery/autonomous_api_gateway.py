from typing import Dict, Any, Optional, Callable, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import hashlib


@dataclass
class APIRequest:
    id: str = field(default_factory=lambda: f"api_{uuid.uuid4().hex[:12]}")
    endpoint: str = ""
    method: str = ""
    headers: Dict[str, str] = field(default_factory=dict)
    body: Any = None
    client_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "pending"
    response: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "method": self.method,
            "client_id": self.client_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "response": self.response,
            "error": self.error,
            "duration_ms": self.duration_ms,
        }


class AutonomousAPIGateway:
    """Gateway API autônomo — auth, rate-limiting, routing, métricas. Sync, sem asyncio."""

    def __init__(self, rate_limit_max: int = 100) -> None:
        self._requests: Dict[str, APIRequest] = {}
        self._handlers: Dict[str, Callable] = {}
        self._rate_limits: Dict[str, Dict[str, int]] = {}
        self._rate_limit_max = rate_limit_max
        self._authenticated_clients: Set[str] = set()
        self._api_keys: Dict[str, str] = {}

    def register_handler(self, endpoint: str, method: str, handler: Callable) -> None:
        self._handlers[f"{method}:{endpoint}"] = handler

    def register_client(self, client_id: str) -> str:
        api_key = hashlib.sha256(f"{client_id}:{time.time()}".encode()).hexdigest()[:32]
        self._api_keys[api_key] = client_id
        self._authenticated_clients.add(client_id)
        return api_key

    def authenticate(self, api_key: str) -> bool:
        return api_key in self._api_keys

    def authorize(self, client_id: str, endpoint: str) -> bool:
        return client_id in self._authenticated_clients

    def rate_limit_check(self, client_id: str, endpoint: str) -> bool:
        counts = self._rate_limits.setdefault(client_id, {})
        cnt = counts.get(endpoint, 0)
        if cnt >= self._rate_limit_max:
            return False
        counts[endpoint] = cnt + 1
        return True

    def handle_request(
        self,
        endpoint: str,
        method: str,
        headers: Dict[str, str],
        body: Any,
        api_key: str,
    ) -> APIRequest:
        request = APIRequest(endpoint=endpoint, method=method, headers=headers, body=body)

        if not self.authenticate(api_key):
            request.status = "failed"
            request.error = "Authentication failed"
            self._requests[request.id] = request
            return request

        client_id = self._api_keys[api_key]
        request.client_id = client_id

        if not self.authorize(client_id, endpoint):
            request.status = "failed"
            request.error = "Authorization failed"
            self._requests[request.id] = request
            return request

        if not self.rate_limit_check(client_id, endpoint):
            request.status = "failed"
            request.error = "Rate limit exceeded"
            self._requests[request.id] = request
            return request

        handler = self._handlers.get(f"{method}:{endpoint}")
        if not handler:
            request.status = "failed"
            request.error = "Endpoint not found"
            self._requests[request.id] = request
            return request

        t0 = time.perf_counter()
        try:
            request.response = handler(body)
            request.status = "success"
        except Exception as exc:
            request.status = "failed"
            request.error = str(exc)
        finally:
            request.duration_ms = (time.perf_counter() - t0) * 1000

        self._requests[request.id] = request
        return request

    def get_metrics(self) -> Dict[str, Any]:
        total = len(self._requests)
        success = sum(1 for r in self._requests.values() if r.status == "success")
        return {
            "total_requests": total,
            "success_requests": success,
            "failed_requests": total - success,
            "success_rate": success / total if total else 0.0,
            "avg_duration_ms": (
                sum(r.duration_ms for r in self._requests.values()) / total if total else 0.0
            ),
            "clients": len(self._authenticated_clients),
        }
