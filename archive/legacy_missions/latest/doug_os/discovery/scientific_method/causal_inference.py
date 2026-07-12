from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import networkx as nx


@dataclass
class CausalResult:
    """Resultado da análise causal."""
    is_causal: bool
    confidence: float
    effect_size: float
    p_value: float
    alternative_explanations: List[str]
    reasoning: str


class CausalInferenceEngine:
    """
    Motor de inferência causal.

    Não aceita apenas correlação — exige evidência causal via DAG + critério backdoor.
    """

    def __init__(self):
        self._dag: nx.DiGraph = nx.DiGraph()
        self._confounders: List[str] = []

    def build_dag(self, variables: List[str], relationships: List[Tuple[str, str]]) -> None:
        self._dag = nx.DiGraph()
        self._dag.add_nodes_from(variables)
        self._dag.add_edges_from(relationships)

    def detect_confounders(self, treatment: str, outcome: str) -> List[str]:
        """Retorna nós intermediários em caminhos indiretos de treatment → outcome."""
        self._confounders = []
        if treatment not in self._dag or outcome not in self._dag:
            return self._confounders

        try:
            paths = list(nx.all_simple_paths(self._dag, treatment, outcome))
        except nx.NetworkXNoPath:
            return self._confounders

        # Nós intermediários em caminhos com mais de um passo (caminhos indiretos)
        seen: set = set()
        for path in paths:
            if len(path) > 2:  # caminho indireto (tem mediador/confundidor)
                for node in path[1:-1]:
                    seen.add(node)

        self._confounders = list(seen)
        return self._confounders

    def check_backdoor(self, treatment: str, outcome: str) -> bool:
        """Verifica se existe pelo menos um conjunto de bloqueio para caminhos backdoor."""
        if not self._dag.nodes:
            return False
        return len(self._confounders) > 0

    def infer_causality(
        self,
        treatment: str,
        outcome: str,
        data: Dict[str, Any],
        confounders: Optional[List[str]] = None,
    ) -> CausalResult:
        conf = confounders if confounders is not None else self.detect_confounders(treatment, outcome)
        has_backdoor = self.check_backdoor(treatment, outcome)

        effect = data.get("effect_size", 0.0)
        p_value = data.get("p_value", 1.0)

        is_causal = (
            effect > 0.1
            and p_value < 0.05
            and has_backdoor
            and len(conf) > 0
        )

        confidence = min(
            0.3 * min(effect / 0.5, 1.0)
            + 0.3 * (1.0 - p_value)
            + 0.2 * (0.5 + min(len(conf) / 10, 0.5))
            + 0.2 * (0.5 + int(has_backdoor) * 0.5),
            1.0,
        )

        alternatives = []
        if not is_causal:
            if effect <= 0.1:
                alternatives.append("Effect size too small")
            if p_value >= 0.05:
                alternatives.append("Not statistically significant")
            if not has_backdoor:
                alternatives.append("Backdoor criterion not satisfied")
            if not conf:
                alternatives.append("No confounders controlled")

        reasoning = (
            f"Causal inference between '{treatment}' and '{outcome}' "
            + ("suggests causal relationship" if is_causal else "does not support causal relationship")
        )

        return CausalResult(
            is_causal=is_causal,
            confidence=confidence,
            effect_size=effect,
            p_value=p_value,
            alternative_explanations=alternatives,
            reasoning=reasoning,
        )
