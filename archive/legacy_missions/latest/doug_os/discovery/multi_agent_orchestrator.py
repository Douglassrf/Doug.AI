from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import threading
import queue


@dataclass
class AgentInfo:
    id: str = field(default_factory=lambda: f"agent_{uuid.uuid4().hex[:12]}")
    name: str = ""
    capabilities: Set[str] = field(default_factory=set)
    status: str = "idle"
    load: float = 0.0
    priority: int = 5
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    active_tasks: int = 0
    max_tasks: int = 10
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "capabilities": list(self.capabilities),
            "status": self.status,
            "load": self.load,
            "priority": self.priority,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "active_tasks": self.active_tasks,
            "max_tasks": self.max_tasks,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AgentTask:
    id: str = field(default_factory=lambda: f"at_{uuid.uuid4().hex[:12]}")
    name: str = ""
    capability: str = ""
    priority: int = 5
    payload: Dict[str, Any] = field(default_factory=dict)
    fn: Optional[Callable] = field(default=None, repr=False)
    assigned_to: Optional[str] = None
    status: str = "pending"
    result: Any = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "capability": self.capability,
            "priority": self.priority,
            "assigned_to": self.assigned_to,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class MultiAgentOrchestrator:
    """Orquestrador multi-agente — registry, dispatch, heartbeat, load distribution."""

    def __init__(self, heartbeat_timeout: int = 30) -> None:
        self._agents: Dict[str, AgentInfo] = {}
        self._tasks: Dict[str, AgentTask] = {}
        self._task_queue: queue.Queue = queue.Queue()
        self._capability_index: Dict[str, Set[str]] = {}
        self._heartbeat_timeout = heartbeat_timeout
        self._lock = threading.Lock()
        self._is_running = False
        self._workers: List[threading.Thread] = []

    def register_agent(
        self,
        name: str,
        capabilities: Set[str],
        max_tasks: int = 10,
        priority: int = 5,
    ) -> AgentInfo:
        agent = AgentInfo(name=name, capabilities=capabilities, max_tasks=max_tasks, priority=priority)
        with self._lock:
            self._agents[agent.id] = agent
            for cap in capabilities:
                self._capability_index.setdefault(cap, set()).add(agent.id)
        return agent

    def heartbeat(self, agent_id: str) -> bool:
        agent = self._agents.get(agent_id)
        if not agent:
            return False
        agent.last_heartbeat = datetime.now(timezone.utc)
        agent.status = "idle" if agent.active_tasks == 0 else "busy"
        return True

    def submit_task(
        self,
        name: str,
        capability: str,
        payload: Dict[str, Any],
        priority: int = 5,
        fn: Optional[Callable] = None,
    ) -> AgentTask:
        task = AgentTask(name=name, capability=capability, priority=priority, payload=payload, fn=fn)
        with self._lock:
            self._tasks[task.id] = task
        self._task_queue.put(task)
        return task

    def dispatch_pending(self) -> int:
        """Dispatch all tasks currently in queue synchronously. Returns count dispatched."""
        dispatched = 0
        while not self._task_queue.empty():
            try:
                task = self._task_queue.get_nowait()
            except queue.Empty:
                break
            agent_id = self._select_agent(task.capability, task.priority)
            if not agent_id:
                task.status = "failed"
                task.error = "No available agent with required capability"
            else:
                agent = self._agents.get(agent_id)
                if not agent:
                    task.status = "failed"
                    task.error = "Agent not found"
                else:
                    task.assigned_to = agent_id
                    task.started_at = datetime.now(timezone.utc)
                    task.status = "running"
                    agent.active_tasks += 1
                    agent.load = agent.active_tasks / agent.max_tasks
                    try:
                        result = task.fn(task.payload) if task.fn else {"status": "success", "processed_by": agent_id}
                        task.result = result
                        task.status = "completed"
                    except Exception as exc:
                        task.status = "failed"
                        task.error = str(exc)
                    finally:
                        task.completed_at = datetime.now(timezone.utc)
                        agent.active_tasks -= 1
                        agent.load = agent.active_tasks / agent.max_tasks
                        agent.status = "idle" if agent.active_tasks == 0 else "busy"
            dispatched += 1
        return dispatched

    def _select_agent(self, capability: str, priority: int) -> Optional[str]:
        candidate_ids = self._capability_index.get(capability, set())
        if not candidate_ids:
            return None
        now = datetime.now(timezone.utc)
        available = []
        for agent_id in candidate_ids:
            agent = self._agents.get(agent_id)
            if not agent:
                continue
            if (now - agent.last_heartbeat).total_seconds() > self._heartbeat_timeout:
                agent.status = "offline"
                continue
            if agent.status in ("offline", "error"):
                continue
            if agent.active_tasks >= agent.max_tasks:
                continue
            available.append(agent)
        if not available:
            return None
        available.sort(key=lambda x: (x.priority, -x.load), reverse=True)
        return available[0].id

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        agent = self._agents.get(agent_id)
        return agent.to_dict() if agent else None

    def get_orchestrator_dashboard(self) -> Dict[str, Any]:
        total = len(self._agents)
        active = sum(1 for a in self._agents.values() if a.status in ("idle", "busy"))
        offline = sum(1 for a in self._agents.values() if a.status == "offline")
        return {
            "total_agents": total,
            "active_agents": active,
            "offline_agents": offline,
            "pending_tasks": sum(1 for t in self._tasks.values() if t.status == "pending"),
            "running_tasks": sum(1 for t in self._tasks.values() if t.status == "running"),
            "completed_tasks": sum(1 for t in self._tasks.values() if t.status == "completed"),
            "failed_tasks": sum(1 for t in self._tasks.values() if t.status == "failed"),
            "avg_load": sum(a.load for a in self._agents.values()) / total if total > 0 else 0.0,
        }
