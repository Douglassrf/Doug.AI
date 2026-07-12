from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class ExperimentDesign(Enum):
    OBSERVATIONAL = "observational"
    A_B_TESTING = "a_b_testing"
    MULTI_ARM = "multi_arm"
    FACTORIAL = "factorial"
    TIME_SERIES = "time_series"
    CROSS_VALIDATION = "cross_validation"
    BOOTSTRAP = "bootstrap"
    MONTE_CARLO = "monte_carlo"


@dataclass
class ExperimentProtocol:
    """Protocolo detalhado de experimento. Define como a hipótese será testada."""

    id: str = field(default_factory=lambda: f"exp_proto_{uuid.uuid4().hex[:12]}")
    scientific_protocol_id: str = ""
    name: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    design: ExperimentDesign = ExperimentDesign.OBSERVATIONAL
    sample_size: int = 30
    iterations: int = 100
    confidence_level: float = 0.95

    control_group: Optional[Dict[str, Any]] = None
    treatment_group: Optional[Dict[str, Any]] = None

    primary_metric: str = ""
    secondary_metrics: List[str] = field(default_factory=list)
    filters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "scientific_protocol_id": self.scientific_protocol_id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "design": self.design.value,
            "sample_size": self.sample_size,
            "iterations": self.iterations,
            "confidence_level": self.confidence_level,
            "control_group": self.control_group,
            "treatment_group": self.treatment_group,
            "primary_metric": self.primary_metric,
            "secondary_metrics": self.secondary_metrics,
            "filters": self.filters,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentProtocol":
        return cls(
            id=data["id"],
            scientific_protocol_id=data.get("scientific_protocol_id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            design=ExperimentDesign(data.get("design", "observational")),
            sample_size=data.get("sample_size", 30),
            iterations=data.get("iterations", 100),
            confidence_level=data.get("confidence_level", 0.95),
            control_group=data.get("control_group"),
            treatment_group=data.get("treatment_group"),
            primary_metric=data.get("primary_metric", ""),
            secondary_metrics=data.get("secondary_metrics", []),
            filters=data.get("filters", {}),
        )

    def is_valid(self) -> bool:
        return all([
            self.scientific_protocol_id,
            self.design,
            self.sample_size > 0,
            self.iterations > 0,
            0 < self.confidence_level < 1,
            self.primary_metric,
        ])
