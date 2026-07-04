from statistics import mean
from typing import Iterable
from doug_os.core.intent_vector import IntentVector

class RegimeDetector:
    """Classify the current market regime based on aggregated intent vectors.

    Thresholds for classification are sourced from
    :mod:`doug_os.config.REGIME_THRESHOLDS` to allow central tuning.
    """

    def detect(self, vectors: Iterable[IntentVector]) -> str:
        vectors = list(vectors)
        if not vectors:
            # In absence of information, assume high systemic risk
            return "SYSTEMIC_RISK"

        from doug_os.config import REGIME_THRESHOLDS as T

        avg_manipulation = mean(v.manipulation_risk for v in vectors)
        avg_entropy = mean(v.entropy_score for v in vectors)
        avg_risk = mean(v.risk for v in vectors)
        avg_confidence = mean(v.confidence for v in vectors)
        avg_evidence = mean(v.evidence_strength for v in vectors)

        # Evaluate conditions in order of severity
        if avg_manipulation >= T["manipulation"]:
            return "MANIPULATED"
        if avg_entropy >= T["entropy_chaotic"]:
            return "CHAOTIC"
        if avg_risk >= T["risk_systemic"]:
            return "SYSTEMIC_RISK"
        if avg_entropy >= T["entropy_whitenoise"] and avg_confidence <= T["confidence_whitenoise"]:
            return "WHITE_NOISE"
        if avg_confidence >= T["confidence_trending"] and avg_evidence >= T["evidence_trending"]:
            return "TRENDING"
        if avg_risk >= T["risk_volatile"]:
            return "VOLATILE"
        return "NORMAL"
