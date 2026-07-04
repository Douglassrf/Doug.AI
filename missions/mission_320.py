# ============================================================
# MISSÃO 320 — UNIVERSAL TIME MACHINE
# Fase Ômega Final — Doug.AI v1.0
# ============================================================

from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import json
import hashlib
import time
import asyncio


@dataclass
class TimeSnapshot:
    """Snapshot temporal."""

    id: str = field(default_factory=lambda: f"ts_{uuid.uuid4().hex[:12]}")
    name: str = ""
    state: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0.0"
    hash: str = ""

    def __post_init__(self):
        if not self.hash:
            self.hash = self._calculate_hash()

    def _calculate_hash(self) -> str:
        """Calcula hash do snapshot."""
        content = json.dumps(self.state, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "timestamp": self.timestamp.isoformat(),
            "version": self.version,
            "hash": self.hash,
        }


@dataclass
class ReplayExecution:
    """Execução de replay."""

    id: str = field(default_factory=lambda: f"re_{uuid.uuid4().hex[:12]}")
    snapshot_id: str = ""
    duration_ms: float = 0.0
    success: bool = False
    changes: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "snapshot_id": self.snapshot_id,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "changes": self.changes,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
        }


class UniversalTimeMachine:
    """
    Máquina do tempo universal.

    Implementa replay, rollback, timeline e dashboard.
    """

    def __init__(self):
        self._snapshots: Dict[str, TimeSnapshot] = {}
        self._replays: List[ReplayExecution] = []
        self._timeline: List[Dict[str, Any]] = []
        self._max_snapshots = 1000

    def create_snapshot(self, name: str, state: Dict[str, Any]) -> TimeSnapshot:
        """Cria snapshot do estado."""
        snapshot = TimeSnapshot(name=name, state=state)
        self._snapshots[snapshot.id] = snapshot

        if len(self._snapshots) > self._max_snapshots:
            oldest = min(
                self._snapshots.keys(),
                key=lambda key: self._snapshots[key].timestamp,
            )
            del self._snapshots[oldest]

        self._timeline.append(
            {
                "event": "snapshot_created",
                "snapshot_id": snapshot.id,
                "name": name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return snapshot

    async def replay(
        self,
        snapshot_id: str,
        target_function: Callable,
        context: Optional[Dict[str, Any]] = None,
    ) -> ReplayExecution:
        """Reexecuta estado a partir de snapshot."""
        snapshot = self._snapshots.get(snapshot_id)
        if not snapshot:
            return ReplayExecution(
                snapshot_id=snapshot_id,
                success=False,
                error="Snapshot not found",
            )

        start = time.perf_counter()
        execution = ReplayExecution(snapshot_id=snapshot_id)

        try:
            restored_state = snapshot.state.copy()

            if context:
                restored_state["context"] = context

            if asyncio.iscoroutinefunction(target_function):
                output = await target_function(restored_state)
            else:
                output = target_function(restored_state)

            if isinstance(output, dict):
                execution.changes = output
            else:
                execution.changes = {"result": output}
            execution.success = True

        except Exception as exc:
            execution.error = str(exc)
            execution.success = False

        execution.duration_ms = (time.perf_counter() - start) * 1000
        self._replays.append(execution)

        self._timeline.append(
            {
                "event": "replay_executed",
                "snapshot_id": snapshot_id,
                "success": execution.success,
                "duration_ms": execution.duration_ms,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return execution

    def rollback(self, snapshot_id: str) -> bool:
        """Rollback para snapshot."""
        snapshot = self._snapshots.get(snapshot_id)
        if not snapshot:
            return False

        self._timeline.append(
            {
                "event": "rollback",
                "snapshot_id": snapshot_id,
                "name": snapshot.name,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        )
        return True

    def get_timeline(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Retorna timeline."""
        return self._timeline[-limit:]

    def search_snapshots(self, query: str) -> List[TimeSnapshot]:
        """Busca snapshots."""
        query_lower = query.lower()
        return [
            snapshot
            for snapshot in self._snapshots.values()
            if query_lower in snapshot.name.lower()
        ]

    def get_time_machine_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard da máquina do tempo."""
        total_snapshots = len(self._snapshots)
        total_replays = len(self._replays)
        successful_replays = sum(1 for replay in self._replays if replay.success)

        return {
            "total_snapshots": total_snapshots,
            "total_replays": total_replays,
            "successful_replays": successful_replays,
            "success_rate": successful_replays / total_replays if total_replays > 0 else 0,
            "avg_replay_ms": (
                sum(replay.duration_ms for replay in self._replays) / total_replays
                if total_replays > 0
                else 0
            ),
            "timeline_events": len(self._timeline),
            "recent_snapshots": [
                snapshot.to_dict()
                for snapshot in list(self._snapshots.values())[-5:]
            ],
        }
