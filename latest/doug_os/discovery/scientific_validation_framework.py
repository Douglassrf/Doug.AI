from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class ScientificDiscovery:
    id: str = field(default_factory=lambda: f"sd_{uuid.uuid4().hex[:12]}")
    title: str = ""
    description: str = ""
    hypothesis: str = ""
    evidence: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    p_value: float = 1.0
    effect_size: float = 0.0
    sample_size: int = 0
    replication_count: int = 0
    validation_score: float = 0.0
    status: str = "pending"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    validated_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "hypothesis": self.hypothesis,
            "evidence": self.evidence,
            "confidence": self.confidence,
            "p_value": self.p_value,
            "effect_size": self.effect_size,
            "sample_size": self.sample_size,
            "replication_count": self.replication_count,
            "validation_score": self.validation_score,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "validated_at": self.validated_at.isoformat() if self.validated_at else None,
        }


@dataclass
class ValidationResult:
    discovery_id: str = ""
    is_valid: bool = False
    score: float = 0.0
    confidence: float = 0.0
    reasons: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "discovery_id": self.discovery_id,
            "is_valid": self.is_valid,
            "score": self.score,
            "confidence": self.confidence,
            "reasons": self.reasons,
            "recommendations": self.recommendations,
            "created_at": self.created_at.isoformat(),
        }


class ScientificValidationFramework:
    """Framework de validação científica para descobertas do Doug.AI."""

    def __init__(self) -> None:
        self._discoveries: Dict[str, ScientificDiscovery] = {}
        self._validations: Dict[str, ValidationResult] = {}
        self._publication_queue: List[str] = []

    def register_discovery(
        self,
        title: str,
        description: str,
        hypothesis: str,
        evidence: List[Dict[str, Any]],
    ) -> ScientificDiscovery:
        discovery = ScientificDiscovery(
            title=title,
            description=description,
            hypothesis=hypothesis,
            evidence=evidence,
        )
        self._discoveries[discovery.id] = discovery
        return discovery

    def validate(self, discovery_id: str) -> ValidationResult:
        discovery = self._discoveries.get(discovery_id)
        if not discovery:
            raise ValueError(f"Discovery {discovery_id} not found")

        reasons: List[str] = []
        recommendations: List[str] = []
        score = 0.0

        stat = self._validate_statistical(discovery)
        reasons.extend(stat["reasons"])
        recommendations.extend(stat["recommendations"])
        score += stat["score"] * 0.3

        conf = self._validate_confidence(discovery)
        reasons.extend(conf["reasons"])
        recommendations.extend(conf["recommendations"])
        score += conf["score"] * 0.3

        repl = self._validate_replication(discovery)
        reasons.extend(repl["reasons"])
        recommendations.extend(repl["recommendations"])
        score += repl["score"] * 0.4

        composite_confidence = score * discovery.confidence
        is_valid = score > 0.6 and composite_confidence > 0.5

        if is_valid:
            discovery.status = "validated"
            discovery.validation_score = score
            discovery.validated_at = datetime.now(timezone.utc)
            self._publication_queue.append(discovery_id)

        result = ValidationResult(
            discovery_id=discovery_id,
            is_valid=is_valid,
            score=score,
            confidence=composite_confidence,
            reasons=reasons[:5],
            recommendations=recommendations[:5],
        )
        self._validations[discovery_id] = result
        return result

    # ------------------------------------------------------------------
    def _validate_statistical(self, d: ScientificDiscovery) -> Dict[str, Any]:
        score = 0.0
        reasons: List[str] = []
        recs: List[str] = []

        if d.p_value < 0.05:
            score += 0.4
        elif d.p_value < 0.1:
            score += 0.2
            reasons.append("P-value marginally significant")
            recs.append("Increase sample size")
        else:
            reasons.append("P-value not significant")
            recs.append("Review methodology")

        if d.effect_size > 0.2:
            score += 0.3
        elif d.effect_size > 0.1:
            score += 0.15
            reasons.append("Small effect size")
        else:
            reasons.append("Negligible effect size")

        if d.sample_size > 100:
            score += 0.3
        elif d.sample_size > 30:
            score += 0.15
            reasons.append("Sample size could be larger")
        else:
            reasons.append("Insufficient sample size")
            recs.append("Increase sample size")

        return {"score": min(score, 1.0), "reasons": reasons, "recommendations": recs}

    def _validate_confidence(self, d: ScientificDiscovery) -> Dict[str, Any]:
        bonus = min(d.replication_count / 10, 0.2)
        score = d.confidence * 0.8 + bonus
        reasons: List[str] = []
        recs: List[str] = []

        if d.confidence > 0.8:
            reasons.append("High confidence")
        elif d.confidence > 0.5:
            reasons.append("Moderate confidence")
            recs.append("Seek additional evidence")
        else:
            reasons.append("Low confidence")
            recs.append("Collect more evidence")

        return {"score": min(score, 1.0), "reasons": reasons, "recommendations": recs}

    def _validate_replication(self, d: ScientificDiscovery) -> Dict[str, Any]:
        score = min(d.replication_count / 3, 1.0)
        reasons: List[str] = []
        recs: List[str] = []

        if d.replication_count >= 3:
            reasons.append("Successfully replicated multiple times")
        elif d.replication_count >= 1:
            reasons.append("Replicated at least once")
            recs.append("Run additional replications")
        else:
            reasons.append("Not yet replicated")
            recs.append("Perform replication studies")

        return {"score": score, "reasons": reasons, "recommendations": recs}

    # ------------------------------------------------------------------
    def get_publication_queue(self) -> List[str]:
        return list(self._publication_queue)

    def publish(self, discovery_id: str) -> bool:
        discovery = self._discoveries.get(discovery_id)
        if not discovery or discovery.status != "validated":
            return False
        discovery.status = "published"
        if discovery_id in self._publication_queue:
            self._publication_queue.remove(discovery_id)
        return True

    def get_validation_result(self, discovery_id: str) -> Optional[ValidationResult]:
        return self._validations.get(discovery_id)

    def get_all_discoveries(self) -> List[ScientificDiscovery]:
        return list(self._discoveries.values())
