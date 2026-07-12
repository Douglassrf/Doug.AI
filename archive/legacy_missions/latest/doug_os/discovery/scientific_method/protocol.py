from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class ScientificStatus(Enum):
    FORMULATING = "formulating"
    PROPOSED = "proposed"
    VALIDATING = "validating"
    APPROVED = "approved"
    REJECTED = "rejected"
    TESTING = "testing"
    COMPLETED = "completed"


class EvidenceLevel(Enum):
    ANECDOTAL = 1
    OBSERVATIONAL = 2
    CORRELATIONAL = 3
    CAUSAL = 4
    EXPERIMENTAL = 5
    REPLICATED = 6

    def label(self) -> str:
        return self.name.lower()

    @classmethod
    def from_label(cls, label: str) -> "EvidenceLevel":
        mapping = {e.label(): e for e in cls}
        if label not in mapping:
            raise ValueError(f"Unknown evidence level: {label}")
        return mapping[label]


@dataclass
class ScientificProtocol:
    """Protocolo científico completo. Nenhum experimento pode existir sem protocolo."""

    id: str = field(default_factory=lambda: f"proto_{uuid.uuid4().hex[:12]}")
    hypothesis_id: str = ""
    title: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    question: str = ""
    hypothesis_formulation: str = ""
    null_hypothesis: str = ""
    alternative_hypothesis: str = ""

    independent_variables: List[str] = field(default_factory=list)
    dependent_variables: List[str] = field(default_factory=list)
    control_variables: List[str] = field(default_factory=list)
    confounding_variables: List[str] = field(default_factory=list)

    success_criteria: Dict[str, Any] = field(default_factory=dict)
    rejection_criteria: Dict[str, Any] = field(default_factory=dict)
    minimum_evidence_level: EvidenceLevel = EvidenceLevel.CORRELATIONAL

    minimum_sample_size: int = 30
    confidence_threshold: float = 0.95
    p_value_threshold: float = 0.05
    effect_size_minimum: float = 0.1

    status: ScientificStatus = ScientificStatus.FORMULATING
    evidence_level: EvidenceLevel = EvidenceLevel.ANECDOTAL
    replication_count: int = 0

    findings: List[Dict[str, Any]] = field(default_factory=list)
    rejected_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "hypothesis_id": self.hypothesis_id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "question": self.question,
            "hypothesis_formulation": self.hypothesis_formulation,
            "null_hypothesis": self.null_hypothesis,
            "alternative_hypothesis": self.alternative_hypothesis,
            "independent_variables": self.independent_variables,
            "dependent_variables": self.dependent_variables,
            "control_variables": self.control_variables,
            "confounding_variables": self.confounding_variables,
            "success_criteria": self.success_criteria,
            "rejection_criteria": self.rejection_criteria,
            "minimum_evidence_level": self.minimum_evidence_level.label(),
            "minimum_sample_size": self.minimum_sample_size,
            "confidence_threshold": self.confidence_threshold,
            "p_value_threshold": self.p_value_threshold,
            "effect_size_minimum": self.effect_size_minimum,
            "status": self.status.value,
            "evidence_level": self.evidence_level.label(),
            "replication_count": self.replication_count,
            "findings": self.findings,
            "rejected_at": self.rejected_at.isoformat() if self.rejected_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ScientificProtocol":
        return cls(
            id=data["id"],
            hypothesis_id=data.get("hypothesis_id", ""),
            title=data.get("title", ""),
            description=data.get("description", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            question=data.get("question", ""),
            hypothesis_formulation=data.get("hypothesis_formulation", ""),
            null_hypothesis=data.get("null_hypothesis", ""),
            alternative_hypothesis=data.get("alternative_hypothesis", ""),
            independent_variables=data.get("independent_variables", []),
            dependent_variables=data.get("dependent_variables", []),
            control_variables=data.get("control_variables", []),
            confounding_variables=data.get("confounding_variables", []),
            success_criteria=data.get("success_criteria", {}),
            rejection_criteria=data.get("rejection_criteria", {}),
            minimum_evidence_level=EvidenceLevel.from_label(
                data.get("minimum_evidence_level", "correlational")
            ),
            minimum_sample_size=data.get("minimum_sample_size", 30),
            confidence_threshold=data.get("confidence_threshold", 0.95),
            p_value_threshold=data.get("p_value_threshold", 0.05),
            effect_size_minimum=data.get("effect_size_minimum", 0.1),
            status=ScientificStatus(data.get("status", "formulating")),
            evidence_level=EvidenceLevel.from_label(data.get("evidence_level", "anecdotal")),
            replication_count=data.get("replication_count", 0),
            findings=data.get("findings", []),
            rejected_at=datetime.fromisoformat(data["rejected_at"]) if data.get("rejected_at") else None,
            approved_at=datetime.fromisoformat(data["approved_at"]) if data.get("approved_at") else None,
        )

    def is_valid(self) -> bool:
        return all([
            self.hypothesis_id,
            self.question,
            self.hypothesis_formulation,
            self.null_hypothesis,
            self.alternative_hypothesis,
            self.independent_variables,
            self.dependent_variables,
            self.success_criteria,
            self.rejection_criteria,
        ])

    def promote_evidence(self, new_level: EvidenceLevel) -> "ScientificProtocol":
        """Promove nível de evidência (só avança, nunca retrocede)."""
        if new_level.value > self.evidence_level.value:
            self.evidence_level = new_level
            self.updated_at = datetime.now(timezone.utc)
        return self
