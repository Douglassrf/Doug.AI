# ============================================================
# MISSÃO 319 — UNIVERSAL EVENT BUS
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import asyncio


@dataclass
class UniversalEvent:
    """Evento universal."""

    id: str = field(default_factory=lambda: f"uevt_{uuid.uuid4().hex[:12]}")
    type: str = ""
    source: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: Optional[str] = None
    version: str = "1.0.0"
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
            "version": self.version,
            "status": self.status,
        }


class UniversalEventBus:
    """
    Barramento universal de eventos.

    Implementa publish, subscribe, priority queue, retry, dead letter e replay.
    """

    def __init__(self):
        self._subscriptions: Dict[str, List[Callable]] = {}
        self._events: List[UniversalEvent] = []
        self._dead_letters: List[UniversalEvent] = []
        self._queue: asyncio.PriorityQueue = asyncio.PriorityQueue()
        self._workers: List[asyncio.Task] = []
        self._is_running = False
        self._max_retries = 3
        self._retry_delay = 0.01
        self._metrics: Dict[str, int] = {
            "published": 0,
            "processed": 0,
            "failed": 0,
            "retried": 0,
            "queue_size": 0,
        }
        self._event_trace: Dict[str, List[str]] = {}
        self._counter = 0

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """Registra handler para tipo de evento."""
        if event_type not in self._subscriptions:
            self._subscriptions[event_type] = []
        self._subscriptions[event_type].append(handler)

    async def publish(self, event: UniversalEvent) -> bool:
        """Publica evento no barramento."""
        self._metrics["published"] += 1
        self._events.append(event)
        self._event_trace[event.id] = [event.source]

        priority = 10 - event.priority
        self._counter += 1
        await self._queue.put((priority, self._counter, event))
        self._metrics["queue_size"] = self._queue.qsize()
        return True

    async def start(self, workers: int = 4) -> None:
        """Inicia o barramento."""
        if self._is_running:
            return

        self._is_running = True
        self._workers = [asyncio.create_task(self._worker(i)) for i in range(workers)]

    async def stop(self) -> None:
        """Para o barramento."""
        self._is_running = False

        for worker in self._workers:
            worker.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

    async def _worker(self, wid: int) -> None:
        """Worker processa eventos."""
        while self._is_running:
            try:
                _, _, event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
                self._metrics["queue_size"] = self._queue.qsize()
            except asyncio.TimeoutError:
                continue

            handlers = self._subscriptions.get(event.type, [])

            if not handlers:
                event.status = "failed"
                self._dead_letters.append(event)
                self._metrics["failed"] += 1
                self._queue.task_done()
                continue

            retry_count = 0
            processed = False

            while retry_count < self._max_retries and not processed:
                try:
                    for handler in handlers:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)

                    event.status = "processed"
                    self._metrics["processed"] += 1
                    processed = True

                    if event.id in self._event_trace:
                        self._event_trace[event.id].append("processed")

                except Exception as exc:
                    retry_count += 1
                    self._metrics["retried"] += 1

                    if retry_count < self._max_retries:
                        await asyncio.sleep(self._retry_delay * retry_count)
                    else:
                        event.status = "failed"
                        self._dead_letters.append(event)
                        self._metrics["failed"] += 1
                        if event.id in self._event_trace:
                            self._event_trace[event.id].append(f"failed: {exc}")

            self._queue.task_done()

    def replay_events(
        self, event_type: Optional[str] = None, limit: int = 100
    ) -> List[UniversalEvent]:
        """Reexecuta eventos armazenados."""
        filtered = [event for event in self._events if event.status == "processed"]

        if event_type:
            filtered = [event for event in filtered if event.type == event_type]

        return filtered[-limit:]

    def get_event_trace(self, event_id: str) -> Optional[List[str]]:
        """Retorna trace de um evento."""
        return self._event_trace.get(event_id)

    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do barramento."""
        return {
            **self._metrics,
            "total_events": len(self._events),
            "dead_letters": len(self._dead_letters),
            "subscriptions": len(self._subscriptions),
            "event_types": list(self._subscriptions.keys()),
            "trace_count": len(self._event_trace),
        }
