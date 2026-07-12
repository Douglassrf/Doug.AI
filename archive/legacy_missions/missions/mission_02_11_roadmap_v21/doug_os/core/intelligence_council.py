from collections import defaultdict
from doug_os.core.intent_vector import IntentVector
from doug_os.core.regime_detector import RegimeDetector
from doug_os.core.dynamic_weights import DynamicWeights

class IntelligenceCouncil:
    def __init__(self):
        self.regime_detector = RegimeDetector()
        self.dynamic_weights = DynamicWeights()

    def decide(self, vectors: list[IntentVector], cycle_id: str) -> dict:
        accepted = []
        rejected = []

        for vector in vectors:
            if not isinstance(vector, IntentVector):
                rejected.append({"reason": "not_intent_vector", "vector": str(vector)})
                continue
            if vector.cycle_id != cycle_id:
                rejected.append({"reason": "wrong_cycle_id", "vector": vector.to_dict()})
                continue
            if not vector.validate():
                rejected.append({"reason": "invalid_vector", "vector": vector.to_dict()})
                continue
            accepted.append(vector)

        if not accepted:
            return {
                "cycle_id": cycle_id,
                "decision": "BLOCK",
                "reason": "no_valid_vectors",
                "confidence": 0,
                "regime": "SYSTEMIC_RISK",
                "weights": {},
                "accepted": [],
                "rejected": rejected,
            }

        for vector in accepted:
            if vector.servo == "risk_empire" and vector.is_blocking():
                return {
                    "cycle_id": cycle_id,
                    "decision": "BLOCK",
                    "reason": "critical_servo_block",
                    "blocked_by": vector.servo,
                    "confidence": vector.confidence,
                    "regime": "SYSTEMIC_RISK",
                    "weights": {},
                    "accepted": [v.to_dict() for v in accepted],
                    "rejected": rejected,
                }

        regime = self.regime_detector.detect(accepted)
        weights = self.dynamic_weights.get(regime)

        if regime == "WHITE_NOISE":
            return {
                "cycle_id": cycle_id,
                "decision": "HOLD",
                "reason": "white_noise_hibernation",
                "confidence": 0,
                "regime": regime,
                "weights": weights,
                "accepted": [v.to_dict() for v in accepted],
                "rejected": rejected,
            }

        scores = defaultdict(float)
        evidence_log = []

        for vector in accepted:
            weight = weights.get(vector.servo, 0.0)
            adjusted_score = (
                vector.confidence
                * (vector.evidence_strength / 100)
                * (vector.opportunity_score / 100)
                * (vector.reality_score / 100)
                * (1 - vector.risk / 100)
                * (1 - vector.manipulation_risk / 100)
                * (1 - vector.entropy_score / 100)
                * weight
            )
            scores[vector.direction] += adjusted_score
            evidence_log.append({
                "servo": vector.servo,
                "direction": vector.direction,
                "weight": weight,
                "adjusted_score": round(adjusted_score, 4),
                "reasons": vector.reasons,
                "warnings": vector.warnings,
            })

        final_decision = max(scores, key=scores.get)
        total_score = sum(scores.values()) or 1.0
        confidence = round((scores[final_decision] / total_score) * 100, 2)

        if final_decision != "HOLD" and confidence < 55:
            final_decision = "HOLD"
            reason = "low_consensus_confidence"
        else:
            reason = "consensus_approved"

        return {
            "cycle_id": cycle_id,
            "decision": final_decision,
            "reason": reason,
            "confidence": confidence,
            "regime": regime,
            "weights": weights,
            "scores": dict(scores),
            "evidence_log": evidence_log,
            "accepted": [v.to_dict() for v in accepted],
            "rejected": rejected,
        }
