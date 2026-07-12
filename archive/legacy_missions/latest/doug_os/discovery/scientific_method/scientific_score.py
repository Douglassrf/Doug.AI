from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class ScientificScore:
    """Score científico completo. Avalia a qualidade científica de uma descoberta."""

    hypothesis_score: float = 0.0
    evidence_score: float = 0.0
    reproducibility_score: float = 0.0
    robustness_score: float = 0.0
    novelty_score: float = 0.0
    overall_score: float = 0.0

    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

    def calculate_overall(self) -> float:
        weights = {
            "hypothesis": 0.20,
            "evidence": 0.25,
            "reproducibility": 0.20,
            "robustness": 0.20,
            "novelty": 0.15,
        }
        self.overall_score = (
            self.hypothesis_score * weights["hypothesis"]
            + self.evidence_score * weights["evidence"]
            + self.reproducibility_score * weights["reproducibility"]
            + self.robustness_score * weights["robustness"]
            + self.novelty_score * weights["novelty"]
        )
        return self.overall_score

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hypothesis_score": self.hypothesis_score,
            "evidence_score": self.evidence_score,
            "reproducibility_score": self.reproducibility_score,
            "robustness_score": self.robustness_score,
            "novelty_score": self.novelty_score,
            "overall_score": self.overall_score,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "recommendations": self.recommendations,
        }


class ScientificScoreCalculator:
    """Calcula scores científicos ponderados."""

    def calculate(self, protocol_data: Dict[str, Any], results: Dict[str, Any]) -> ScientificScore:
        score = ScientificScore()
        score.hypothesis_score = self._calculate_hypothesis_score(protocol_data)
        score.evidence_score = self._calculate_evidence_score(results)
        score.reproducibility_score = self._calculate_reproducibility_score(results)
        score.robustness_score = self._calculate_robustness_score(results)
        score.novelty_score = self._calculate_novelty_score(protocol_data)
        score.calculate_overall()
        score.recommendations = self._generate_recommendations(score)
        return score

    def _calculate_hypothesis_score(self, data: Dict) -> float:
        score = 0.0
        if data.get("question"):
            score += 0.2
        if data.get("hypothesis_formulation"):
            score += 0.3
        if data.get("independent_variables"):
            score += 0.2
        if data.get("dependent_variables"):
            score += 0.2
        if data.get("success_criteria"):
            score += 0.1
        return min(score, 1.0)

    def _calculate_evidence_score(self, results: Dict) -> float:
        score = 0.0
        if results.get("effect_size", 0) > 0.1:
            score += 0.3
        if results.get("p_value", 1.0) < 0.05:
            score += 0.3
        if results.get("confidence_level", 0) > 0.9:
            score += 0.2
        if results.get("sample_size", 0) > 100:
            score += 0.2
        return min(score, 1.0)

    def _calculate_reproducibility_score(self, results: Dict) -> float:
        score = 0.0
        repetitions = results.get("repetitions", 1)
        if repetitions > 1:
            score += min(repetitions / 5, 0.4)
        if results.get("consistency", 0) > 0.8:
            score += 0.3
        if results.get("variance", 1.0) < 0.2:
            score += 0.3
        return min(score, 1.0)

    def _calculate_robustness_score(self, results: Dict) -> float:
        score = 0.0
        stress = results.get("stress_tests_passed", 0)
        if stress > 0:
            score += min(stress / 5, 0.5)
        if results.get("sensitivity", 0) > 0.7:
            score += 0.3
        if results.get("conditions_tested", 0) > 3:
            score += 0.2
        return min(score, 1.0)

    def _calculate_novelty_score(self, data: Dict) -> float:
        score = 0.0
        if data.get("novel_combination", False):
            score += 0.3
        if data.get("novel_variables", []):
            score += 0.3
        if data.get("novel_approach", False):
            score += 0.2
        if data.get("contribution", ""):
            score += 0.2
        return min(score, 1.0)

    def _generate_recommendations(self, score: ScientificScore) -> List[str]:
        recs = []
        if score.hypothesis_score < 0.7:
            recs.append("Refine hypothesis formulation")
        if score.evidence_score < 0.7:
            recs.append("Collect more evidence or improve experimental design")
        if score.reproducibility_score < 0.7:
            recs.append("Run more replications to confirm results")
        if score.robustness_score < 0.7:
            recs.append("Test robustness under different conditions")
        if score.overall_score < 0.7:
            recs.append("Consider redesigning the experiment")
        return recs
