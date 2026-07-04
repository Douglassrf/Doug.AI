from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any
import uuid


@dataclass
class DoubtAnalysis:
    id: str = field(default_factory=lambda: f"doubt_{uuid.uuid4().hex[:12]}")
    hypothesis_id: str = ""
    critical_questions: List[str] = field(default_factory=list)
    doubt_score: float = 0.0
    evidence_gaps: List[str] = field(default_factory=list)
    adversarial_arguments: List[str] = field(default_factory=list)
    recommendation: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "hypothesis_id": self.hypothesis_id,
            "critical_questions": self.critical_questions,
            "doubt_score": self.doubt_score, "evidence_gaps": self.evidence_gaps,
            "adversarial_arguments": self.adversarial_arguments,
            "recommendation": self.recommendation, "created_at": self.created_at.isoformat(),
        }


class DoubtEngine:
    """Motor de dúvida saudável — questiona hipóteses antes de qualquer promoção."""

    _QUESTION_TEMPLATES = [
        "What if the data is wrong?",
        "What alternative explanations exist?",
        "What would disprove this hypothesis?",
        "Is the effect size meaningful?",
        "Could this be due to randomness?",
        "What would a skeptic say?",
        "Is the methodology sound?",
        "Were there any confounders?",
        "Is this reproducible?",
        "What assumptions are being made?",
    ]

    def __init__(self):
        self._analyses: Dict[str, DoubtAnalysis] = {}

    def analyze(self, hypothesis: Dict[str, Any], evidence: Dict[str, Any]) -> DoubtAnalysis:
        questions = self._generate_critical_questions(hypothesis)
        gaps = self._identify_evidence_gaps(evidence)
        adversarial = self._generate_adversarial_arguments(hypothesis)
        doubt_score = self._calculate_doubt_score(len(gaps), len(adversarial), evidence)
        if doubt_score > 0.7:
            rec = "High doubt — require substantial additional evidence"
        elif doubt_score > 0.4:
            rec = "Moderate doubt — proceed with caution"
        else:
            rec = "Low doubt — continue evaluation"
        hyp_id = hypothesis.get("id", "")
        a = DoubtAnalysis(
            hypothesis_id=hyp_id, critical_questions=questions,
            doubt_score=doubt_score, evidence_gaps=gaps,
            adversarial_arguments=adversarial, recommendation=rec,
        )
        self._analyses[hyp_id] = a
        return a

    def _generate_critical_questions(self, hypothesis: Dict) -> List[str]:
        questions = list(self._QUESTION_TEMPLATES[:5])
        if "timeframe" in hypothesis:
            questions.append(f"Is {hypothesis['timeframe']} the right timeframe?")
        if "market_regime" in hypothesis:
            questions.append(f"Does this hold in {hypothesis['market_regime']}?")
        return questions[:10]

    def _identify_evidence_gaps(self, evidence: Dict) -> List[str]:
        gaps = []
        if evidence.get("sample_size", 0) <= 30: gaps.append("Small sample size")
        if not evidence.get("reproducible", False): gaps.append("No reproducibility evidence")
        if not evidence.get("independent_validation", False): gaps.append("No independent validation")
        if not evidence.get("peer_reviewed", False): gaps.append("No peer review")
        return gaps

    def _generate_adversarial_arguments(self, hypothesis: Dict) -> List[str]:
        args = []
        if hypothesis.get("confidence", 0) > 0.8: args.append("High confidence may be overoptimistic")
        if hypothesis.get("complexity", 0) > 5: args.append("Overly complex — may be overfitting")
        if "expected_effect" in hypothesis: args.append("Expected effect may be too strong")
        return args

    def _calculate_doubt_score(self, n_gaps: int, n_adversarial: int, evidence: Dict) -> float:
        score = n_gaps * 0.1 + n_adversarial * 0.1
        if evidence.get("quality", 1.0) < 0.5: score += 0.3
        return min(score, 1.0)

    def get_high_doubt_recommendations(self, threshold: float = 0.6) -> List[DoubtAnalysis]:
        return [a for a in self._analyses.values() if a.doubt_score > threshold]
