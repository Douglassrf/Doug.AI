from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import threading


@dataclass
class CognitiveNode:
    id: str = field(default_factory=lambda: f"node_{uuid.uuid4().hex[:12]}")
    name: str = ""
    capabilities: List[str] = field(default_factory=list)
    status: str = "active"
    load: float = 0.0
    memory_usage: float = 0.0
    cpu_usage: float = 0.0
    active_tasks: int = 0
    max_tasks: int = 10
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "capabilities": self.capabilities,
            "status": self.status, "load": self.load, "memory_usage": self.memory_usage,
            "cpu_usage": self.cpu_usage, "active_tasks": self.active_tasks,
            "max_tasks": self.max_tasks,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class DistributedTask:
    id: str = field(default_factory=lambda: f"dtask_{uuid.uuid4().hex[:12]}")
    name: str = ""
    node_id: str = ""
    function: Optional[Callable] = None
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    priority: int = 5
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "node_id": self.node_id,
            "priority": self.priority, "status": self.status, "result": self.result,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "created_at": self.created_at.isoformat(),
        }


class DistributedCognitiveProcessing:
    def __init__(self):
        self._nodes: Dict[str, CognitiveNode] = {}
        self._tasks: Dict[str, DistributedTask] = {}
        self._lock = threading.Lock()

    def register_node(self, name: str, capabilities: List[str], max_tasks: int = 10) -> CognitiveNode:
        node = CognitiveNode(name=name, capabilities=capabilities, max_tasks=max_tasks)
        with self._lock:
            self._nodes[node.id] = node
        return node

    def update_node_health(self, node_id: str) -> bool:
        node = self._nodes.get(node_id)
        if not node:
            return False
        node.last_heartbeat = datetime.now(timezone.utc)
        return True

    def submit_task(self, name: str, func: Callable, priority: int = 5,
                    node_capability: Optional[str] = None, *args, **kwargs) -> DistributedTask:
        node_id = self._select_node(node_capability)
        if not node_id:
            raise ValueError("No available node found")
        task = DistributedTask(name=name, node_id=node_id, function=func,
                               args=args, kwargs=kwargs, priority=priority)
        with self._lock:
            self._tasks[task.id] = task
        self._run_task(task)
        return task

    def _select_node(self, capability: Optional[str] = None) -> Optional[str]:
        available = [n for n in self._nodes.values()
                     if n.status == "active" and n.active_tasks < n.max_tasks
                     and (capability is None or capability in n.capabilities)]
        if not available:
            return None
        return min(available, key=lambda x: x.load).id

    def _run_task(self, task: DistributedTask) -> None:
        node = self._nodes.get(task.node_id)
        if not node:
            task.status = "failed"
            task.error = "Node not found"
            return
        task.started_at = datetime.now(timezone.utc)
        task.status = "running"
        node.active_tasks += 1
        node.load = node.active_tasks / node.max_tasks
        try:
            task.result = task.function(*task.args, **task.kwargs)
            task.status = "completed"
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
        finally:
            task.completed_at = datetime.now(timezone.utc)
            node.active_tasks = max(node.active_tasks - 1, 0)
            node.load = node.active_tasks / node.max_tasks

    def get_node_status(self) -> Dict[str, Any]:
        return {nid: n.to_dict() for nid, n in self._nodes.items()}

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        task = self._tasks.get(task_id)
        return task.to_dict() if task else None
