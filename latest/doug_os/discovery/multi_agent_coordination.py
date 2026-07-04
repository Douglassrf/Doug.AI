from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import queue as queue_module


@dataclass
class Agent:
    id: str = field(default_factory=lambda: f"agent_{uuid.uuid4().hex[:12]}")
    name: str = ""
    role: str = ""
    capabilities: List[str] = field(default_factory=list)
    status: str = "idle"
    current_task: Optional[str] = None
    last_active: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "name": self.name, "role": self.role,
            "capabilities": self.capabilities, "status": self.status,
            "current_task": self.current_task,
            "last_active": self.last_active.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CoordinationMessage:
    id: str = field(default_factory=lambda: f"msg_{uuid.uuid4().hex[:12]}")
    from_agent: str = ""
    to_agent: str = ""
    type: str = ""
    content: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "from_agent": self.from_agent, "to_agent": self.to_agent,
            "type": self.type, "content": self.content, "priority": self.priority,
            "created_at": self.created_at.isoformat(),
        }


class MultiAgentCoordinationEngine:
    def __init__(self):
        self._agents: Dict[str, Agent] = {}
        self._messages: List[CoordinationMessage] = []
        self._message_queue: queue_module.Queue = queue_module.Queue()
        self._agent_registry: Dict[str, List[str]] = {}

    def register_agent(self, name: str, role: str, capabilities: List[str]) -> Agent:
        agent = Agent(name=name, role=role, capabilities=capabilities)
        self._agents[agent.id] = agent
        self._agent_registry.setdefault(role, []).append(agent.id)
        return agent

    def send_message(self, from_agent: str, to_agent: str, type: str,
                     content: Dict[str, Any], priority: int = 5) -> CoordinationMessage:
        msg = CoordinationMessage(from_agent=from_agent, to_agent=to_agent,
                                  type=type, content=content, priority=priority)
        self._messages.append(msg)
        self._message_queue.put(msg)
        return msg

    def broadcast(self, from_agent: str, type: str, content: Dict[str, Any]) -> List[CoordinationMessage]:
        return [self.send_message(from_agent, aid, type, content)
                for aid in self._agents if aid != from_agent]

    def get_agents_by_role(self, role: str) -> List[Agent]:
        return [self._agents[aid] for aid in self._agent_registry.get(role, []) if aid in self._agents]

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        a = self._agents.get(agent_id)
        return a.to_dict() if a else None

    def update_agent_status(self, agent_id: str, status: str) -> bool:
        a = self._agents.get(agent_id)
        if not a:
            return False
        a.status = status
        a.last_active = datetime.now(timezone.utc)
        return True

    def get_coordination_summary(self) -> Dict[str, Any]:
        return {
            "total_agents": len(self._agents),
            "agents_by_role": {r: len(ids) for r, ids in self._agent_registry.items()},
            "total_messages": len(self._messages),
            "messages_by_type": self._count_messages_by_type(),
            "active_agents": sum(1 for a in self._agents.values() if a.status == "busy"),
        }

    def _count_messages_by_type(self) -> Dict[str, int]:
        counts: Dict[str, int] = {}
        for msg in self._messages:
            counts[msg.type] = counts.get(msg.type, 0) + 1
        return counts
