from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import queue
import threading
import itertools


@dataclass
class Event:
    id: str = field(default_factory=lambda: f"evt_{uuid.uuid4().hex[:12]}")
    type: str = ""
    source: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    status: str = "pending"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "payload": self.payload,
            "priority": self.priority,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": self.correlation_id,
            "status": self.status,
        }


class GlobalEventBus:
    """Barramento global de eventos — threading, replay, persistência, prioridade."""

    def __init__(self, n_workers: int = 2) -> None:
        self._subscribers: Dict[str, List[Callable]] = {}
        self._events: List[Event] = []
        self._persistence: Dict[str, Event] = {}
        self._queue: queue.PriorityQueue = queue.PriorityQueue()
        self._lock = threading.Lock()
        self._is_running = False
        self._workers: List[threading.Thread] = []
        self._n_workers = n_workers
        self._counter = itertools.count()

    def subscribe(self, event_type: str, handler: Callable) -> None:
        with self._lock:
            self._subscribers.setdefault(event_type, []).append(handler)

    def publish(self, event: Event) -> None:
        with self._lock:
            self._events.append(event)
            self._persistence[event.id] = event
            if len(self._events) > 10_000:
                self._events = self._events[-10_000:]

        # Priority queue: lower number = higher priority; counter breaks ties between equal priorities
        self._queue.put((10 - event.priority, next(self._counter), event))

    def start(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        for _ in range(self._n_workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self._workers.append(t)

    def stop(self) -> None:
        self._is_running = False
        for _ in self._workers:
            self._queue.put((0, -1, None))
        for t in self._workers:
            t.join(timeout=2)
        self._workers.clear()

    def _worker(self) -> None:
        while self._is_running:
            try:
                _, _cnt, event = self._queue.get(timeout=0.1)
            except queue.Empty:
                continue
            if event is None:
                break
            handlers = self._subscribers.get(event.type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as exc:
                    event.payload["error"] = str(exc)
                    event.status = "failed"
            if event.status != "failed":
                event.status = "processed"
            self._queue.task_done()

    def process_pending(self) -> int:
        """Process all pending events synchronously (for testing)."""
        processed = 0
        while not self._queue.empty():
            try:
                _, _cnt, event = self._queue.get_nowait()
            except queue.Empty:
                break
            if event is None:
                break
            handlers = self._subscribers.get(event.type, [])
            for handler in handlers:
                try:
                    handler(event)
                except Exception as exc:
                    event.payload["error"] = str(exc)
                    event.status = "failed"
            if event.status != "failed":
                event.status = "processed"
            processed += 1
        return processed

    def replay_events(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        filtered = [e for e in self._events if e.status == "processed"]
        if event_type:
            filtered = [e for e in filtered if e.type == event_type]
        return filtered[-limit:]

    def get_metrics(self) -> Dict[str, Any]:
        total = len(self._events)
        processed = sum(1 for e in self._events if e.status == "processed")
        return {
            "total_events": total,
            "processed_events": processed,
            "pending_events": total - processed,
            "queue_size": self._queue.qsize(),
            "subscribers": len(self._subscribers),
            "event_types": list(self._subscribers.keys()),
        }
