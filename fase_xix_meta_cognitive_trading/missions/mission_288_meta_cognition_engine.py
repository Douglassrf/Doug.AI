# ============================================================
# MISSÃO 288 — META-COGNITION ENGINE
# Padrão Doug.AI — Nota 10
# ============================================================

from typing import Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


@dataclass
class CognitiveAudit:
    """Auditoria cognitiva."""
    id: str = field(default_factory=lambda: f"ca_{uuid.uuid4().hex[:12]}")
    decision_id: str = ""
    reasoning_quality: float = 0.0
    logic_consistency: float = 0.0
    bias_score: float = 0.0
    confidence_calibration: float = 0.0
    self_consistency: float = 0.0
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "reasoning_quality": self.reasoning_quality,
            "logic_consistency": self.logic_consistency,
            "bias_score": self.bias_score,
            "confidence_calibration": self.confidence_calibration,
            "self_consistency": self.self_consistency,
            "recommendation": self.recommendation,
            "created_at": self.created_at.isoformat(),
        }


class MetaCognitionEngine:
    """
    Motor de meta-cognição.

    Implementa:
    - Self Reasoning Analyzer
    - Logic Consistency
    - Decision Confidence Review
    - Bias Detection
    - Internal Audit
    - Cognitive Integrity
    - Decision Explanation
    - Confidence Calibration
    - Self Review Dashboard
    - Meta Learning Report
    """

    def __init__(self):
        self._audits: Dict[str, List[CognitiveAudit]] = {}
        self._bias_patterns = {
            "recency": 0.0,
            "confirmation": 0.0,
            "overconfidence": 0.0,
            "regime": 0.0,
        }

    def audit_decision(
        self,
        decision_id: str,
        reasoning_chain: List[Dict[str, Any]],
        confidence: float,
        evidence: Dict[str, Any],
    ) -> CognitiveAudit:
        """Audita uma decisão."""
        reasoning_quality = self._analyze_reasoning(reasoning_chain)
        logic_consistency = self._check_logic_consistency(reasoning_chain)
        bias_score = self._detect_biases(reasoning_chain, evidence)
        confidence_calibration = self._calibrate_confidence(confidence, evidence)
        self_consistency = self._check_self_consistency(reasoning_chain)
        recommendation = self._generate_recommendation(
            reasoning_quality,
            logic_consistency,
            bias_score,
            confidence_calibration,
        )

        audit = CognitiveAudit(
            decision_id=decision_id,
            reasoning_quality=reasoning_quality,
            logic_consistency=logic_consistency,
            bias_score=bias_score,
            confidence_calibration=confidence_calibration,
            self_consistency=self_consistency,
            recommendation=recommendation,
        )

        if decision_id not in self._audits:
            self._audits[decision_id] = []
        self._audits[decision_id].append(audit)

        return audit

    def _analyze_reasoning(self, chain: List[Dict]) -> float:
        """Analisa qualidade do raciocínio."""
        if not chain:
            return 0.0

        steps = len(chain)
        if steps < 3:
            return 0.4

        if not any(step.get("type") == "conclusion" for step in chain):
            return 0.5

        return min(0.5 + steps * 0.05, 1.0)

    def _check_logic_consistency(self, chain: List[Dict]) -> float:
        """Verifica consistência lógica."""
        if len(chain) < 2:
            return 0.5

        contradictions = 0
        premises = [step.get("premise") for step in chain if step.get("premise")]

        for i in range(len(premises)):
            for j in range(i + 1, len(premises)):
                if premises[i] and premises[j]:
                    if "increase" in premises[i] and "decrease" in premises[j]:
                        contradictions += 1
                    if "buy" in premises[i] and "sell" in premises[j]:
                        contradictions += 1

        if contradictions > 0:
            return max(0.2, 1 - contradictions * 0.2)

        return min(0.8 + len(chain) * 0.02, 1.0)

    def _detect_biases(self, chain: List[Dict], evidence: Dict) -> float:
        """Detecta vieses no raciocínio."""
        bias_score = 0.0
        total_bias = 0

        if chain and len(chain) > 5:
            recent = chain[-3:]
            if all(step.get("source") == "recent" for step in recent):
                bias_score += 0.2
                total_bias += 1

        if evidence:
            expected = evidence.get("expected_outcome", "")
            actual = evidence.get("actual_outcome", "")
            if expected and actual and expected == actual:
                bias_score += 0.1
                total_bias += 1

        if len(chain) < 3 and len(evidence) > 5:
            bias_score += 0.2
            total_bias += 1

        return bias_score / max(total_bias, 1) if total_bias > 0 else 0.0

    def _calibrate_confidence(self, confidence: float, evidence: Dict) -> float:
        """Calibra confiança baseada em evidência."""
        evidence_quality = evidence.get("quality", 0.5)
        sample_size = evidence.get("sample_size", 10)
        calibrated = confidence * evidence_quality * min(sample_size / 50, 1.0)
        return min(calibrated, 1.0)

    def _check_self_consistency(self, chain: List[Dict]) -> float:
        """Verifica auto-consistência."""
        if len(chain) < 2:
            return 0.5

        conclusions = [step.get("conclusion") for step in chain if step.get("conclusion")]
        if not conclusions:
            return 0.5

        unique = set(conclusions)
        return len(unique) / len(conclusions) if conclusions else 0.5

    def _generate_recommendation(
        self, reasoning: float, logic: float, bias: float, confidence: float
    ) -> str:
        """Gera recomendação."""
        if reasoning < 0.4 or logic < 0.4:
            return "INSUFFICIENT: Decision lacks reasoning quality or logic consistency"
        if bias > 0.5:
            return "BIAS_WARNING: Significant bias detected in reasoning process"
        if confidence < 0.5:
            return "LOW_CONFIDENCE: Decision confidence below threshold"
        if reasoning > 0.7 and logic > 0.7 and bias < 0.3:
            return "APPROVED: Decision passes cognitive audit"
        return "REVIEW: Decision requires additional scrutiny"

    def get_meta_dashboard(self) -> Dict[str, Any]:
        """Retorna dashboard meta-cognitivo."""
        total_audits = sum(len(audits) for audits in self._audits.values())

        if total_audits == 0:
            return {"status": "no_data"}

        all_audits = [a for audits in self._audits.values() for a in audits]

        return {
            "total_audits": total_audits,
            "avg_reasoning_quality": np.mean([a.reasoning_quality for a in all_audits]),
            "avg_logic_consistency": np.mean([a.logic_consistency for a in all_audits]),
            "avg_bias_score": np.mean([a.bias_score for a in all_audits]),
            "avg_confidence_calibration": np.mean([a.confidence_calibration for a in all_audits]),
            "recommendations": {
                "approved": sum(1 for a in all_audits if "APPROVED" in a.recommendation),
                "warning": sum(1 for a in all_audits if "WARNING" in a.recommendation),
                "review": sum(1 for a in all_audits if "REVIEW" in a.recommendation),
            },
            "recent_audits": [a.to_dict() for a in all_audits[-5:]],
        }
