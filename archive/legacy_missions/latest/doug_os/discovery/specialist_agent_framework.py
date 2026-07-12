from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import time


@dataclass
class AgentExecution:
    id: str = field(default_factory=lambda: f"ae_{uuid.uuid4().hex[:12]}")
    agent_type: str = ""
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "agent_type": self.agent_type,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "status": self.status,
            "error": self.error,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
        }


class BaseSpecialistAgent:
    """Classe base para agentes especializados — execução sync, histórico, capacidades."""

    def __init__(self, name: str, agent_type: str) -> None:
        self.name = name
        self.agent_type = agent_type
        self._history: List[AgentExecution] = []
        self._capabilities: Set[str] = self._register_capabilities()

    def _register_capabilities(self) -> Set[str]:
        return {"base_processing"}

    def execute(self, input_data: Dict[str, Any]) -> AgentExecution:
        execution = AgentExecution(agent_type=self.agent_type, input_data=input_data)
        execution.started_at = datetime.now(timezone.utc)
        execution.status = "running"
        try:
            result = self._process(input_data)
            execution.output_data = result
            execution.status = "completed"
        except Exception as exc:
            execution.status = "failed"
            execution.error = str(exc)
        finally:
            execution.completed_at = datetime.now(timezone.utc)
            execution.duration_ms = (
                (execution.completed_at - execution.started_at).total_seconds() * 1000
            )
            self._history.append(execution)
        return execution

    def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"status": "processed", "data": input_data}

    def get_history(self, limit: int = 20) -> List[AgentExecution]:
        return self._history[-limit:]

    def get_capabilities(self) -> Set[str]:
        return self._capabilities


class MarketAgent(BaseSpecialistAgent):
    def __init__(self, name: str = "MarketAgent") -> None:
        super().__init__(name, "market")

    def _register_capabilities(self) -> Set[str]:
        return {"market_analysis", "trend_detection", "pattern_recognition"}

    def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "market_status": "analyzed",
            "trend": "bullish",
            "volatility": 0.3,
            "momentum": 0.6,
        }


class RiskAgent(BaseSpecialistAgent):
    def __init__(self, name: str = "RiskAgent") -> None:
        super().__init__(name, "risk")

    def _register_capabilities(self) -> Set[str]:
        return {"risk_assessment", "volatility_analysis", "exposure_calculation"}

    def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "risk_score": 0.25,
            "var_estimate": 0.05,
            "stress_scenario": "moderate",
            "recommendation": "proceed_with_caution",
        }


class DiscoveryAgent(BaseSpecialistAgent):
    def __init__(self, name: str = "DiscoveryAgent") -> None:
        super().__init__(name, "discovery")

    def _register_capabilities(self) -> Set[str]:
        return {"pattern_mining", "hypothesis_generation", "correlation_detection"}

    def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "discoveries": ["pattern_1", "pattern_2"],
            "hypotheses": ["hyp_1", "hyp_2"],
            "confidence": 0.7,
        }


class LearningAgent(BaseSpecialistAgent):
    def __init__(self, name: str = "LearningAgent") -> None:
        super().__init__(name, "learning")

    def _register_capabilities(self) -> Set[str]:
        return {"model_training", "parameter_optimization", "validation"}

    def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "model_updated": True,
            "accuracy_improvement": 0.05,
            "training_status": "completed",
        }


class AuditAgent(BaseSpecialistAgent):
    def __init__(self, name: str = "AuditAgent") -> None:
        super().__init__(name, "audit")

    def _register_capabilities(self) -> Set[str]:
        return {"audit_trail", "compliance_check", "anomaly_detection"}

    def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"audit_passed": True, "compliance_score": 0.95, "anomalies": []}


class ResearchAgent(BaseSpecialistAgent):
    def __init__(self, name: str = "ResearchAgent") -> None:
        super().__init__(name, "research")

    def _register_capabilities(self) -> Set[str]:
        return {"literature_search", "evidence_synthesis", "hypothesis_ranking"}

    def _process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"findings": [], "evidence_score": 0.6, "status": "researched"}
