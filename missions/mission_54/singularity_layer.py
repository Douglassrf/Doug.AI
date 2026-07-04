from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import uuid


@dataclass
class SingularityAlert:
    id: str = field(default_factory=lambda: f"sing_{uuid.uuid4().hex[:12]}")
    alert_type: str = ""   # loop | instability | hallucination | runaway | overcomplexity
    severity: int = 5      # 1-10
    description: str = ""
    evidence: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mitigated: bool = False
    mitigation_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "alert_type": self.alert_type, "severity": self.severity,
            "description": self.description, "evidence": self.evidence,
            "detected_at": self.detected_at.isoformat(),
            "mitigated": self.mitigated, "mitigation_action": self.mitigation_action,
        }


class IntelligenceSingularityLayer:
    """
    Camada de monitoramento de singularidade cognitiva.

    Detecta quando o sistema se torna instável, entra em loop,
    ou produz descobertas alucinatórias de alta complexidade sem evidência.
    """

    _LOOP_THRESHOLD = 5           # Hipóteses idênticas consecutivas
    _INSTABILITY_THRESHOLD = 0.8  # Score de instabilidade
    _COMPLEXITY_THRESHOLD = 10    # Nível de complexidade máximo seguro

    def __init__(self):
        self._alerts: List[SingularityAlert] = []
        self._recent_hypotheses: List[str] = []
        self._discovery_scores: List[float] = []

    def monitor(self, discovery_state: Dict[str, Any]) -> List[SingularityAlert]:
        """Monitora estado do Discovery Layer e emite alertas de singularidade."""
        new_alerts: List[SingularityAlert] = []

        loop_alert = self._detect_loop(discovery_state)
        if loop_alert:
            new_alerts.append(loop_alert)

        instability_alert = self._detect_instability(discovery_state)
        if instability_alert:
            new_alerts.append(instability_alert)

        hallucination_alert = self._detect_hallucination(discovery_state)
        if hallucination_alert:
            new_alerts.append(hallucination_alert)

        complexity_alert = self._detect_overcomplexity(discovery_state)
        if complexity_alert:
            new_alerts.append(complexity_alert)

        self._alerts.extend(new_alerts)
        return new_alerts

    def _detect_loop(self, state: Dict[str, Any]) -> Optional[SingularityAlert]:
        hyp = state.get("latest_hypothesis", "")
        if hyp:
            self._recent_hypotheses.append(hyp)
        if len(self._recent_hypotheses) >= self._LOOP_THRESHOLD:
            recent = self._recent_hypotheses[-self._LOOP_THRESHOLD:]
            if len(set(recent)) == 1:
                return SingularityAlert(
                    alert_type="loop",
                    severity=8,
                    description=f"Discovery stuck in loop: '{hyp}' repeated {self._LOOP_THRESHOLD}x",
                    evidence=recent,
                )
        return None

    def _detect_instability(self, state: Dict[str, Any]) -> Optional[SingularityAlert]:
        score = float(state.get("instability_score", 0.0))
        self._discovery_scores.append(score)
        if score > self._INSTABILITY_THRESHOLD:
            return SingularityAlert(
                alert_type="instability",
                severity=7,
                description=f"Instability score {score:.2f} exceeds threshold {self._INSTABILITY_THRESHOLD}",
                evidence=[f"score={score:.4f}"],
            )
        return None

    def _detect_hallucination(self, state: Dict[str, Any]) -> Optional[SingularityAlert]:
        confidence = float(state.get("confidence", 0.0))
        plausibility = float(state.get("plausibility", 1.0))
        if confidence > 0.95 and plausibility < 0.1:
            return SingularityAlert(
                alert_type="hallucination",
                severity=9,
                description=f"High confidence {confidence:.2f} with low plausibility {plausibility:.2f}",
                evidence=[f"confidence={confidence}", f"plausibility={plausibility}"],
            )
        return None

    def _detect_overcomplexity(self, state: Dict[str, Any]) -> Optional[SingularityAlert]:
        complexity = int(state.get("complexity_level", 0))
        if complexity > self._COMPLEXITY_THRESHOLD:
            return SingularityAlert(
                alert_type="overcomplexity",
                severity=6,
                description=f"Complexity level {complexity} exceeds safe threshold {self._COMPLEXITY_THRESHOLD}",
                evidence=[f"complexity={complexity}"],
            )
        return None

    def get_active_alerts(self, min_severity: int = 1) -> List[SingularityAlert]:
        return [a for a in self._alerts if not a.mitigated and a.severity >= min_severity]

    def mitigate(self, alert_id: str, action: str) -> bool:
        for alert in self._alerts:
            if alert.id == alert_id:
                alert.mitigated = True
                alert.mitigation_action = action
                return True
        return False
