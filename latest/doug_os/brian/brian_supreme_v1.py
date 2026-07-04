"""Brian Supreme v1 (Missão 36).

Esta versão da camada supervisora Brian Supreme expande a funcionalidade
pré‑existente, fornecendo auditoria em tempo real das decisões
geradas pelos servos e engines do DougBrain.  A classe `BrianSupremeV1`
consome uma lista de `IntentVector` e verifica inconsistências entre
os sinais, calcula indicadores agregados e sugere ajustes quando
necessário.  Ela também constrói explicações humanamente legíveis para
facilitar a compreensão das decisões.

Funcionalidades principais:

* **Detecção de inconsistências:** identifica quando diferentes
  servos sugerem direções opostas (por exemplo, alguns pedem BUY e
  outros SELL) ou quando uma acção de BUY/SELL é proposta com risco
  elevado.
* **Sugestões de ajuste:** recomenda reduzir pesos de servos
  divergentes, rever parâmetros de risco ou optar por HOLD se o
  consenso estiver baixo.
* **Explicação de decisões:** compila as razões de cada servo em uma
  narrativa resumida, destacando os fatores mais influentes.

Future missions may extend this layer to incorporate machine
explanations, trace decision paths or interactively adjust weights.
"""

from __future__ import annotations

from collections import Counter
from typing import Iterable, Dict, List

from doug_os.core.intent_vector import IntentVector


class BrianSupremeV1:
    """Supervisory layer that audits and explains servo decisions."""

    def review(self, signals: Iterable[IntentVector]) -> Dict[str, List[str]]:
        """Analyse a collection of IntentVectors for inconsistencies and suggestions.

        Parameters
        ----------
        signals : iterable of IntentVector
            The signals produced by servos for a given market cycle.

        Returns
        -------
        dict
            A dictionary with keys ``inconsistencies``, ``suggestions`` and
            ``explanations``, each mapping to a list of strings.
        """
        vectors = list(signals)
        inconsistencies: List[str] = []
        suggestions: List[str] = []
        explanations: List[str] = []

        if not vectors:
            return {
                "inconsistencies": ["no_signals"],
                "suggestions": ["no_action"],
                "explanations": ["Nenhum sinal recebido"],
            }

        # Analyse directions across servos
        directions = [v.direction for v in vectors if v.direction != "HOLD"]
        if directions:
            direction_counts = Counter(directions)
            if len(direction_counts) > 1:
                inconsistencies.append(
                    f"directions_conflict: {', '.join(f'{d}={c}' for d, c in direction_counts.items())}"
                )
                suggestions.append("Considere aumentar pesos de servos defensivos ou optar por HOLD.")
        # High risk detection: if any vector proposes BUY/SELL with risk >= 80
        for v in vectors:
            if v.direction in ("BUY", "SELL") and v.risk >= 80.0:
                inconsistencies.append(
                    f"high_risk_action_from_{v.servo}: risk={v.risk}"
                )
                suggestions.append(
                    f"Reveja a decisão {v.direction} do servo {v.servo}; risco elevado. Considere HOLD ou ajuste de parâmetros."
                )
        # Build explanations: summarise reasons and scores
        for v in vectors:
            reason_str = ", ".join(v.reasons) if v.reasons else "sem razões"
            explanations.append(
                f"Servo {v.servo} → {v.direction} (conf={v.confidence}, risk={v.risk}, evidence={v.evidence_strength}): razões: {reason_str}"
            )

        return {
            "inconsistencies": inconsistencies,
            "suggestions": suggestions,
            "explanations": explanations,
        }
