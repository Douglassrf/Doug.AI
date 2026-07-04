from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class ResearchTask:
    id: str = field(default_factory=lambda: f"rt_{uuid.uuid4().hex[:12]}")
    topic: str = ""
    priority: int = 5
    status: str = "pending"
    assigned_agent: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "topic": self.topic,
            "priority": self.priority,
            "status": self.status,
            "assigned_agent": self.assigned_agent,
            "result": self.result,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


@dataclass
class ResearchAgent:
    id: str = field(default_factory=lambda: f"ra_{uuid.uuid4().hex[:12]}")
    name: str = ""
    specialization: str = "general"
    active_tasks: int = 0
    completed_tasks: int = 0
    reputation: float = 0.7

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "specialization": self.specialization,
            "active_tasks": self.active_tasks,
            "completed_tasks": self.completed_tasks,
            "reputation": self.reputation,
        }


class AutonomousResearchCoordinator:
    """Coordenador de pesquisa autônomo — atribui tarefas, agrega resultados, pondera evidências."""

    def __init__(self, max_parallel_tasks: int = 5) -> None:
        self._agents: Dict[str, ResearchAgent] = {}
        self._tasks: Dict[str, ResearchTask] = {}
        self._max_parallel = max_parallel_tasks
        self._findings: List[Dict[str, Any]] = []

    def register_agent(self, name: str, specialization: str = "general") -> ResearchAgent:
        agent = ResearchAgent(name=name, specialization=specialization)
        self._agents[agent.id] = agent
        return agent

    def submit_task(self, topic: str, priority: int = 5) -> ResearchTask:
        task = ResearchTask(topic=topic, priority=priority)
        self._tasks[task.id] = task
        self._assign_task(task)
        return task

    def _assign_task(self, task: ResearchTask) -> None:
        available = [
            a for a in self._agents.values()
            if a.active_tasks < self._max_parallel
        ]
        if not available:
            task.status = "queued"
            return

        best = max(available, key=lambda a: a.reputation - a.active_tasks * 0.1)
        task.assigned_agent = best.id
        task.status = "in_progress"
        best.active_tasks += 1

    def complete_task(self, task_id: str, result: Dict[str, Any]) -> bool:
        task = self._tasks.get(task_id)
        if not task or task.status != "in_progress":
            return False
        task.result = result
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)

        if task.assigned_agent and task.assigned_agent in self._agents:
            agent = self._agents[task.assigned_agent]
            agent.active_tasks = max(0, agent.active_tasks - 1)
            agent.completed_tasks += 1
            quality = result.get("quality_score", 0.5)
            agent.reputation = min(1.0, agent.reputation * 0.9 + quality * 0.1)

        self._findings.append({"task_id": task_id, "topic": task.topic, **result})
        return True

    def aggregate_findings(self, topic_filter: Optional[str] = None) -> Dict[str, Any]:
        findings = self._findings
        if topic_filter:
            findings = [f for f in findings if topic_filter.lower() in f.get("topic", "").lower()]

        if not findings:
            return {"status": "no_findings"}

        evidence_scores = [f.get("evidence_score", 0.5) for f in findings]
        return {
            "total_findings": len(findings),
            "avg_evidence_score": sum(evidence_scores) / len(evidence_scores),
            "high_confidence": [f for f in findings if f.get("confidence", 0) > 0.8],
            "topics": list({f.get("topic") for f in findings}),
        }

    def get_coordination_status(self) -> Dict[str, Any]:
        return {
            "agents": len(self._agents),
            "tasks": {
                "total": len(self._tasks),
                "pending": sum(1 for t in self._tasks.values() if t.status == "pending"),
                "in_progress": sum(1 for t in self._tasks.values() if t.status == "in_progress"),
                "completed": sum(1 for t in self._tasks.values() if t.status == "completed"),
                "queued": sum(1 for t in self._tasks.values() if t.status == "queued"),
            },
            "findings": len(self._findings),
            "agents_list": [a.to_dict() for a in self._agents.values()],
        }
