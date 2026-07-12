from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class CounterfactualAnalysis:
    """Resultado da análise contrafactual."""
    what_if: str
    expected_outcome: float
    confidence: float
    reasoning: str
    assumptions: List[str] = field(default_factory=list)


class CounterfactualEngine:
    """
    Motor de análise contrafactual.

    Responde: 'E se tivesse sido diferente?'
    Aplica intervenções hipotéticas sobre dados históricos e estima o resultado alternativo.
    """

    def analyze(
        self,
        historical_data: Dict[str, Any],
        intervention: Dict[str, Any],
        model: Any = None,
    ) -> CounterfactualAnalysis:
        """
        Analisa cenários contrafactuais.

        Args:
            historical_data: Dados históricos com 'outcome' e opcionalmente 'variance'.
            intervention: Dicionário com 'description' e 'effect_multiplier'.
            model: Modelo preditivo opcional (reservado para implementações futuras).
        """
        baseline: float = float(historical_data.get("outcome", 0.0))
        effect_multiplier: float = float(intervention.get("effect_multiplier", 1.0))
        expected_outcome = baseline * effect_multiplier

        variance: float = float(historical_data.get("variance", 0.1))
        confidence = min(1.0 / (1.0 + variance), 0.95)

        description = intervention.get("description", "change")
        reasoning = (
            f"If {description} occurred, outcome would be {expected_outcome:.4f} "
            f"vs baseline {baseline:.4f} "
            f"(multiplier={effect_multiplier:.2f})"
        )

        return CounterfactualAnalysis(
            what_if=description,
            expected_outcome=expected_outcome,
            confidence=confidence,
            reasoning=reasoning,
            assumptions=[
                "Model is correctly specified",
                "No unobserved confounders",
                "Effect is stable over time",
            ],
        )
