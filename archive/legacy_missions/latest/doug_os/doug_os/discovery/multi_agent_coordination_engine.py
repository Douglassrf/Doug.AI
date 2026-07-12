from typing import Dict, Any, List, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import threading
import queue


@dataclass
class Agent:
    id: str = field(default_factory=lambda: f"agent_{uuid.uuid4().hex[:12]}")
    name: str = ""
    role: str = ""
    capabilities: Set[str] = field(default_factory=set)
    status: str = "idle"
    reputation: float = 0.5
    health: float = 1.0
    task_count: int = 0
    success_count: int = 0
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "role": self.role,
            "capabilities": list(self.capabilities),
            "status": self.status,
            "reputation": self.reputation,
            "health": self.health,
            "task_count": self.task_count,
            "success_count": self.success_count,
            "last_active": self.last_active.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AgentTask:
    id: str = field(default_factory=lambda: f"at_{uuid.uuid4().hex[:12]}")
    name: str = ""
    priority: int = 5
    capability_required: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
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
            "priority": self.priority,
            "capability_required": self.capability_required,
            "assigned_to": self.assigned_to,
            "status": self.status,
            "result": self.result,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class MultiAgentCoordinationEngine:
    """Motor de coordenação multi-agente (threading, sem asyncio)."""

    def __init__(self) -> None:
        self._agents: Dict[str, Agent] = {}
        self._tasks: Dict[str, AgentTask] = {}
        self._lock = threading.Lock()

    def register_agent(self, name: str, role: str, capabilities: Set[str]) -> Agent:
        agent = Agent(name=name, role=role, capabilities=capabilities)
        with self._lock:
            self._agents[agent.id] = agent
        return agent

    def submit_task(
        self,
        name: str,
        capability_required: str,
        data: Dict[str, Any],
        fn: Optional[Callable] = None,
        priority: int = 5,
    ) -> AgentTask:
        task = AgentTask(
            name=name,
            priority=priority,
            capability_required=capability_required,
            data=data,
            fn=fn,
        )

        with self._lock:
            self._tasks[task.id] = task

        agent = self._select_agent(capability_required)
        if not agent:
            task.status = "failed"
            task.error = "No available agent with required capability"
            return task

        task.assigned_to = agent.id
        task.started_at = datetime.now(timezone.utc)
        task.status = "running"
        agent.status = "busy"
        agent.task_count += 1

        try:
            if fn is not None:
                result = fn()
            else:
                result = {"status": "success", "processed_by": agent.id, "data": data}
            task.result = result
            task.status = "completed"
            agent.success_count += 1
            agent.reputation = min(1.0, agent.reputation + 0.05)
        except Exception as exc:
            task.status = "failed"
            task.error = str(exc)
            agent.reputation = max(0.1, agent.reputation - 0.05)
        finally:
            task.completed_at = datetime.now(timezone.utc)
            agent.status = "idle"
            agent.last_active = datetime.now(timezone.utc)

        return task

    def _select_agent(self, capability: str) -> Optional[Agent]:
        with self._lock:
            available = [
                a for a in self._agents.values()
                if a.status == "idle" and capability in a.capabilities
            ]
        if not available:
            return None
        return max(available, key=lambda x: (x.reputation, x.health))

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        agent = self._agents.get(agent_id)
        return agent.to_dict() if agent else None

    def get_task_result(self, task_id: str) -> Optional[AgentTask]:
        return self._tasks.get(task_id)

    def get_agent_metrics(self) -> Dict[str, Any]:
        with self._lock:
            agents = list(self._agents.values())
            tasks = list(self._tasks.values())

        total_agents = len(agents)
        active_agents = sum(1 for a in agents if a.status == "busy")
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == "completed")
        avg_rep = sum(a.reputation for a in agents) / total_agents if total_agents else 0

        return {
            "total_agents": total_agents,
            "active_agents": active_agents,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": completed_tasks / total_tasks if total_tasks else 0,
            "avg_reputation": avg_rep,
        }
