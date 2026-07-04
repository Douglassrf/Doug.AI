from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import queue
import threading


@dataclass
class BusMessage:
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    sender: str = ""
    recipient: str = ""
    type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "sent"
    retry_count: int = 0
    max_retries: int = 3

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "type": self.type,
            "payload": self.payload,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
        }


class AgentCommunicationBus:
    """Barramento de comunicação entre agentes — pub/sub, retry, dead-letter, métricas."""

    def __init__(self) -> None:
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._messages: List[BusMessage] = []
        self._dead_letters: List[BusMessage] = []
        self._lock = threading.Lock()

    def subscribe(self, event_type: str, handler: Callable) -> None:
        with self._lock:
            self._subscriptions.setdefault(event_type, []).append(handler)

    def publish(
        self,
        sender: str,
        event_type: str,
        payload: Dict[str, Any],
        recipient: str = "",
        priority: int = 5,
    ) -> BusMessage:
        message = BusMessage(
            sender=sender,
            recipient=recipient,
            type=event_type,
            payload=payload,
            priority=priority,
        )
        with self._lock:
            self._messages.append(message)
        self._deliver(message)
        return message

    def _deliver(self, message: BusMessage) -> None:
        handlers = self._subscriptions.get(message.type, [])
        if not handlers:
            message.status = "delivered" if not message.recipient else "failed"
            return

        delivered = False
        for handler in handlers:
            try:
                handler(message)
                delivered = True
            except Exception:
                continue

        if delivered:
            message.status = "delivered"
        else:
            message.retry_count += 1
            if message.retry_count < message.max_retries:
                self._deliver(message)
            else:
                message.status = "failed"
                self._dead_letters.append(message)

    def get_messages(self, limit: int = 100) -> List[BusMessage]:
        return self._messages[-limit:]

    def get_dead_letters(self, limit: int = 50) -> List[BusMessage]:
        return self._dead_letters[-limit:]

    def get_bus_metrics(self) -> Dict[str, Any]:
        total = len(self._messages)
        delivered = sum(1 for m in self._messages if m.status == "delivered")
        failed = sum(1 for m in self._messages if m.status == "failed")
        return {
            "total_messages": total,
            "delivered_messages": delivered,
            "failed_messages": failed,
            "dead_letters": len(self._dead_letters),
            "subscriptions": len(self._subscriptions),
            "event_types": list(self._subscriptions.keys()),
        }
