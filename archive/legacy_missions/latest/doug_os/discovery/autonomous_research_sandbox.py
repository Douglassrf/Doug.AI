from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time
import threading


@dataclass
class ResearchTask:
    id: str = field(default_factory=lambda: f"rt_{uuid.uuid4().hex[:12]}")
    name: str = ""
    description: str = ""
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "description": self.description,
            "status": self.status, "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "result": self.result, "error": self.error,
        }


class AutonomousResearchSandbox:
    def __init__(self, timeout_seconds: int = 300):
        self._tasks: Dict[str, ResearchTask] = {}
        self._timeout = timeout_seconds

    def submit_task(self, name: str, description: str, research_func: Callable, *args, **kwargs) -> ResearchTask:
        task = ResearchTask(name=name, description=description)
        self._tasks[task.id] = task
        self._run_task(task, research_func, *args, **kwargs)
        return task

    def _run_task(self, task: ResearchTask, func: Callable, *args, **kwargs) -> None:
        task.started_at = datetime.now(timezone.utc)
        task.status = "running"
        result_container: Dict[str, Any] = {}

        def target():
            try:
                r = func(*args, **kwargs)
                result_container["data"] = r
                result_container["status"] = "success"
            except Exception as e:
                result_container["error"] = str(e)
                result_container["status"] = "error"

        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=self._timeout)

        task.completed_at = datetime.now(timezone.utc)
        if thread.is_alive():
            task.status = "failed"
            task.error = f"Timeout after {self._timeout}s"
        elif result_container.get("status") == "error":
            task.status = "failed"
            task.error = result_container.get("error", "Unknown error")
        else:
            task.status = "completed"
            task.result = {"status": "success", "data": result_container.get("data")}

    def get_task(self, task_id: str) -> Optional[ResearchTask]:
        return self._tasks.get(task_id)

    def get_pending_tasks(self) -> List[ResearchTask]:
        return [t for t in self._tasks.values() if t.status == "pending"]

    def get_completed_tasks(self) -> List[ResearchTask]:
        return [t for t in self._tasks.values() if t.status == "completed"]

    def get_report(self) -> Dict[str, Any]:
        total = len(self._tasks)
        completed = len(self.get_completed_tasks())
        failed = len([t for t in self._tasks.values() if t.status == "failed"])
        return {
            "total_tasks": total,
            "pending": len(self.get_pending_tasks()),
            "completed": completed,
            "failed": failed,
            "success_rate": completed / total if total > 0 else 0.0,
            "tasks": [t.to_dict() for t in list(self._tasks.values())[-10:]],
        }
