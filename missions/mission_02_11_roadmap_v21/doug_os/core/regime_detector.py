from statistics import mean
from doug_os.core.intent_vector import IntentVector

class RegimeDetector:
    def detect(self, vectors: list[IntentVector]) -> str:
        if not vectors:
            return "SYSTEMIC_RISK"

        avg_manipulation = mean(v.manipulation_risk for v in vectors)
        avg_entropy = mean(v.entropy_score for v in vectors)
        avg_risk = mean(v.risk for v in vectors)
        avg_confidence = mean(v.confidence for v in vectors)
        avg_evidence = mean(v.evidence_strength for v in vectors)

        if avg_manipulation >= 70:
            return "MANIPULATED"
        if avg_entropy >= 80:
            return "CHAOTIC"
        if avg_risk >= 80:
            return "SYSTEMIC_RISK"
        if avg_entropy >= 65 and avg_confidence <= 45:
            return "WHITE_NOISE"
        if avg_confidence >= 70 and avg_evidence >= 65:
            return "TRENDING"
        if avg_risk >= 60:
            return "VOLATILE"
        return "NORMAL"
