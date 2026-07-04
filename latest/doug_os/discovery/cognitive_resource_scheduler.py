from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import threading
import queue as queue_module


class TaskPriority:
    REAL_TIME = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4

    NAMES = {0: "real_time", 1: "high", 2: "normal", 3: "low", 4: "background"}


@dataclass
class ScheduledTask:
    id: str = field(default_factory=lambda: f"task_{uuid.uuid4().hex[:12]}")
    name: str = ""
    priority: int = TaskPriority.NORMAL
    function: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    scheduled_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None

    def __lt__(self, other):
        return self.priority < other.priority

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "priority": self.priority,
            "scheduled_at": self.scheduled_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "status": self.status, "result": self.result, "error": self.error,
        }


class CognitiveResourceScheduler:
    def __init__(self, max_concurrent: int = 4):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._max_concurrent = max_concurrent
        self._queue: queue_module.PriorityQueue = queue_module.PriorityQueue()
        self._lock = threading.Lock()

    def schedule(self, name: str, func: Callable, priority: int = TaskPriority.NORMAL,
                 *args, **kwargs) -> ScheduledTask:
        task = ScheduledTask(name=name, priority=priority, function=func, args=args, kwargs=kwargs)
        with self._lock:
            self._tasks[task.id] = task
        self._queue.put((priority, task))
        return task

    def run_next(self) -> Optional[ScheduledTask]:
        """Executa a proxima task de maior prioridade (sincrono)."""
        try:
            _, task = self._queue.get_nowait()
        except queue_module.Empty:
            return None
        task.started_at = datetime.now(timezone.utc)
        task.status = "running"
        try:
            task.result = task.function(*task.args, **task.kwargs)
            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
        finally:
            task.completed_at = datetime.now(timezone.utc)
        return task

    def run_all(self) -> List[ScheduledTask]:
        """Executa todas as tasks pendentes em ordem de prioridade."""
        results = []
        while not self._queue.empty():
            t = self.run_next()
            if t: results.append(t)
        return results

    def get_task(self, task_id: str) -> Optional[ScheduledTask]:
        return self._tasks.get(task_id)

    def get_queue_status(self) -> Dict[str, int]:
        return {"pending": self._queue.qsize(),
                "total": len(self._tasks)}
