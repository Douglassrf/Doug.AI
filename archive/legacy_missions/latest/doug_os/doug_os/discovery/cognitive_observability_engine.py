from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class Trace:
    id: str = field(default_factory=lambda: f"trace_{uuid.uuid4().hex[:12]}")
    operation: str = ""
    module: str = ""
    parent_id: Optional[str] = None
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: Optional[datetime] = None
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: str = "started"
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "operation": self.operation,
            "module": self.module,
            "parent_id": self.parent_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
            "status": self.status,
            "error": self.error,
        }


@dataclass
class ObservableEvent:
    id: str = field(default_factory=lambda: f"event_{uuid.uuid4().hex[:12]}")
    type: str = ""
    source: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    data: Dict[str, Any] = field(default_factory=dict)
    severity: str = "info"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data,
            "severity": self.severity,
        }


class CognitiveObservabilityEngine:
    """Motor de observabilidade cognitiva — rastreamento distribuído sem asyncio."""

    def __init__(self) -> None:
        self._traces: Dict[str, Trace] = {}
        self._events: List[ObservableEvent] = []
        self._active_traces: Dict[str, str] = {}
        self._timeline: List[Dict[str, Any]] = []

    # ------------------------------------------------------------------
    def start_trace(
        self,
        operation: str,
        module: str,
        parent_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Trace:
        trace = Trace(operation=operation, module=module, parent_id=parent_id, metadata=metadata or {})
        self._traces[trace.id] = trace
        self._active_traces[parent_id or "root"] = trace.id
        self._internal_event("trace_started", trace.to_dict())
        return trace

    def end_trace(
        self,
        trace_id: str,
        status: str = "completed",
        error: Optional[str] = None,
    ) -> Optional[Trace]:
        trace = self._traces.get(trace_id)
        if not trace:
            return None
        trace.end_time = datetime.now(timezone.utc)
        trace.duration_ms = (trace.end_time - trace.start_time).total_seconds() * 1000
        trace.status = status
        trace.error = error
        self._active_traces.pop(trace.parent_id or "root", None)
        self._internal_event("trace_completed", trace.to_dict())
        return trace

    def log_event(
        self,
        event_type: str,
        source: str,
        data: Dict[str, Any],
        severity: str = "info",
    ) -> ObservableEvent:
        event = ObservableEvent(type=event_type, source=source, data=data, severity=severity)
        self._events.append(event)
        self._timeline.append({"timestamp": event.timestamp.isoformat(), "event": event.to_dict()})
        return event

    def _internal_event(self, event_type: str, data: Dict[str, Any]) -> None:
        self.log_event(event_type, "observability_engine", data)

    # ------------------------------------------------------------------
    def get_trace(self, trace_id: str) -> Optional[Trace]:
        return self._traces.get(trace_id)

    def get_trace_tree(self, root_trace_id: str) -> List[Trace]:
        return [
            t for t in self._traces.values()
            if t.id == root_trace_id or t.parent_id == root_trace_id
        ]

    def get_events(
        self,
        event_type: Optional[str] = None,
        severity: Optional[str] = None,
        limit: int = 100,
    ) -> List[ObservableEvent]:
        result = self._events
        if event_type:
            result = [e for e in result if e.type == event_type]
        if severity:
            result = [e for e in result if e.severity == severity]
        return result[-limit:]

    def get_timeline(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._timeline[-limit:]

    def get_observability_dashboard(self) -> Dict[str, Any]:
        total = len(self._traces)
        completed = sum(1 for t in self._traces.values() if t.status == "completed")
        failed = sum(1 for t in self._traces.values() if t.status == "failed")
        durations = [t.duration_ms for t in self._traces.values() if t.duration_ms > 0]
        return {
            "total_traces": total,
            "completed_traces": completed,
            "failed_traces": failed,
            "active_traces": len(self._active_traces),
            "total_events": len(self._events),
            "events_by_severity": {
                sev: sum(1 for e in self._events if e.severity == sev)
                for sev in ("info", "warning", "error", "critical")
            },
            "avg_trace_duration_ms": sum(durations) / len(durations) if durations else 0.0,
        }
