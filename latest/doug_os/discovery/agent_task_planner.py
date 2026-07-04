from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class PlanStep:
    id: str = field(default_factory=lambda: f"ps_{uuid.uuid4().hex[:12]}")
    name: str = ""
    capability: str = ""
    depends_on: List[str] = field(default_factory=list)
    payload: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Any = None
    estimated_duration_ms: float = 100.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "capability": self.capability,
            "depends_on": self.depends_on,
            "status": self.status,
            "result": self.result,
            "estimated_duration_ms": self.estimated_duration_ms,
        }


@dataclass
class AgentPlan:
    id: str = field(default_factory=lambda: f"plan_{uuid.uuid4().hex[:12]}")
    goal: str = ""
    steps: List[PlanStep] = field(default_factory=list)
    status: str = "created"
    priority: int = 5
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "status": self.status,
            "priority": self.priority,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AgentTaskPlanner:
    """Planejador de tarefas para agentes — decomposição de objetivos, dependências, execução."""

    def __init__(self) -> None:
        self._plans: Dict[str, AgentPlan] = {}

    def create_plan(self, goal: str, priority: int = 5) -> AgentPlan:
        plan = AgentPlan(goal=goal, priority=priority)
        self._plans[plan.id] = plan
        return plan

    def add_step(
        self,
        plan_id: str,
        name: str,
        capability: str,
        payload: Optional[Dict[str, Any]] = None,
        depends_on: Optional[List[str]] = None,
        estimated_duration_ms: float = 100.0,
    ) -> PlanStep:
        plan = self._plans.get(plan_id)
        if not plan:
            raise ValueError(f"Plan {plan_id} not found")
        step = PlanStep(
            name=name,
            capability=capability,
            payload=payload or {},
            depends_on=depends_on or [],
            estimated_duration_ms=estimated_duration_ms,
        )
        plan.steps.append(step)
        return step

    def get_ready_steps(self, plan_id: str) -> List[PlanStep]:
        plan = self._plans.get(plan_id)
        if not plan:
            return []
        completed_ids = {s.id for s in plan.steps if s.status == "completed"}
        return [
            s for s in plan.steps
            if s.status == "pending" and all(dep in completed_ids for dep in s.depends_on)
        ]

    def complete_step(self, plan_id: str, step_id: str, result: Any) -> bool:
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        for step in plan.steps:
            if step.id == step_id:
                step.status = "completed"
                step.result = result
                if all(s.status == "completed" for s in plan.steps):
                    plan.status = "completed"
                    plan.completed_at = datetime.now(timezone.utc)
                return True
        return False

    def fail_step(self, plan_id: str, step_id: str, error: str) -> bool:
        plan = self._plans.get(plan_id)
        if not plan:
            return False
        for step in plan.steps:
            if step.id == step_id:
                step.status = "failed"
                plan.status = "failed"
                return True
        return False

    def get_plan_progress(self, plan_id: str) -> Dict[str, Any]:
        plan = self._plans.get(plan_id)
        if not plan:
            return {}
        total = len(plan.steps)
        completed = sum(1 for s in plan.steps if s.status == "completed")
        return {
            "plan_id": plan_id,
            "goal": plan.goal,
            "status": plan.status,
            "total_steps": total,
            "completed_steps": completed,
            "progress_pct": completed / total * 100.0 if total else 0.0,
            "ready_steps": len(self.get_ready_steps(plan_id)),
        }

    def get_planner_dashboard(self) -> Dict[str, Any]:
        plans = list(self._plans.values())
        return {
            "total_plans": len(plans),
            "completed": sum(1 for p in plans if p.status == "completed"),
            "in_progress": sum(1 for p in plans if p.status == "created"),
            "failed": sum(1 for p in plans if p.status == "failed"),
        }
