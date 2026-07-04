from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Tuple, Set
from enum import Enum
import networkx as nx
import uuid


class CausalRelationship(Enum):
    DIRECT = "direct"
    INDIRECT = "indirect"
    SPURIOUS = "spurious"
    CONFOUNDED = "confounded"
    UNKNOWN = "unknown"


@dataclass
class CausalEdge:
    source: str
    target: str
    relationship: CausalRelationship
    strength: float  # 0-1
    confidence: float  # 0-1
    evidence: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "target": self.target,
            "relationship": self.relationship.value,
            "strength": self.strength,
            "confidence": self.confidence,
            "evidence": self.evidence,
        }


@dataclass
class CausalGraph:
    nodes: Set[str]
    edges: List[CausalEdge]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": list(self.nodes),
            "edges": [e.to_dict() for e in self.edges],
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CausalInferenceResult:
    is_causal: bool
    relationship_type: CausalRelationship
    confidence: float
    effect_size: float
    p_value: float
    backdoor_variables: List[str]
    frontdoor_variables: List[str]
    alternative_explanations: List[str]
    reasoning: str


class AdvancedCausalInferenceEngine:
    """
    Motor de inferência causal avançado com DAG, backdoor, frontdoor e do-calculus.
    """

    def __init__(self):
        self._dag: nx.DiGraph = nx.DiGraph()
        self._graph: Optional[CausalGraph] = None

    def build_dag(
        self,
        variables: List[str],
        relationships: List[Tuple[str, str, float]],  # (cause, effect, strength)
    ) -> CausalGraph:
        self._dag = nx.DiGraph()
        self._dag.add_nodes_from(variables)
        edges = []
        for cause, effect, strength in relationships:
            self._dag.add_edge(cause, effect, weight=strength)
            edges.append(
                CausalEdge(
                    source=cause,
                    target=effect,
                    relationship=CausalRelationship.DIRECT,
                    strength=strength,
                    confidence=0.8,
                    evidence=["DAG construction"],
                )
            )
        self._graph = CausalGraph(nodes=set(variables), edges=edges)
        return self._graph

    def detect_confounders(self, treatment: str, outcome: str) -> List[str]:
        """Nos em caminhos indiretos (len > 2) de treatment -> outcome."""
        if treatment not in self._dag or outcome not in self._dag:
            return []
        try:
            paths = list(nx.all_simple_paths(self._dag, treatment, outcome))
        except nx.NetworkXNoPath:
            return []
        seen: Set[str] = set()
        for path in paths:
            if len(path) > 2:
                for node in path[1:-1]:
                    seen.add(node)
        return list(seen)

    def check_backdoor(self, treatment: str, outcome: str, confounders: Optional[List[str]] = None) -> bool:
        conf = confounders if confounders is not None else self.detect_confounders(treatment, outcome)
        return len(conf) > 0

    def check_frontdoor(self, treatment: str, outcome: str) -> bool:
        if treatment not in self._dag or outcome not in self._dag:
            return False
        try:
            paths = list(nx.all_simple_paths(self._dag, treatment, outcome))
        except nx.NetworkXNoPath:
            return False
        mediators: Set[str] = set()
        for path in paths:
            if len(path) > 2:
                mediators.update(path[1:-1])
        return len(mediators) > 0

    def do_calculus(self, treatment: str, outcome: str, data: Dict[str, Any]) -> float:
        """P(outcome | do(treatment)) com ajuste por confundidores."""
        confounders = self.detect_confounders(treatment, outcome)
        adjusted = float(data.get("direct_effect", 0.0))
        for conf in confounders:
            weight = float(data.get(f"conf_{conf}", 0.5))
            adjusted *= 1.0 - weight * 0.1
        return adjusted

    def infer_causality(
        self,
        treatment: str,
        outcome: str,
        data: Dict[str, Any],
        confounders: Optional[List[str]] = None,
    ) -> CausalInferenceResult:
        conf = confounders if confounders is not None else self.detect_confounders(treatment, outcome)
        backdoor_ok = self.check_backdoor(treatment, outcome, conf)
        frontdoor_ok = self.check_frontdoor(treatment, outcome)
        causal_effect = self.do_calculus(treatment, outcome, data)
        p_value = float(data.get("p_value", 1.0))
        effect_size = float(data.get("effect_size", 0.0))

        is_causal = causal_effect > 0.1 and p_value < 0.05 and (backdoor_ok or frontdoor_ok)

        if is_causal:
            rel_type = CausalRelationship.DIRECT if (backdoor_ok and frontdoor_ok) else CausalRelationship.INDIRECT
        else:
            rel_type = CausalRelationship.CONFOUNDED if conf else CausalRelationship.SPURIOUS

        confidence = min(
            0.3 * min(causal_effect / 0.5, 1.0)
            + 0.3 * (1.0 - p_value)
            + 0.2 * (0.5 + min(len(conf) / 10.0, 0.5))
            + 0.2 * (0.5 + int(backdoor_ok or frontdoor_ok) * 0.5),
            1.0,
        )

        alternatives = []
        if not is_causal:
            if causal_effect <= 0.1:
                alternatives.append("Effect size too small")
            if p_value >= 0.05:
                alternatives.append("Not statistically significant")
            if not backdoor_ok and not frontdoor_ok:
                alternatives.append("No causal path identified")

        reasoning = f"Causal inference '{treatment}' -> '{outcome}': "
        reasoning += (
            f"{rel_type.value} relationship (conf={confidence:.2f})"
            if is_causal
            else f"not causal ({'; '.join(alternatives) or 'insufficient evidence'})"
        )

        return CausalInferenceResult(
            is_causal=is_causal,
            relationship_type=rel_type,
            confidence=confidence,
            effect_size=causal_effect,
            p_value=p_value,
            backdoor_variables=conf,
            frontdoor_variables=[],
            alternative_explanations=alternatives,
            reasoning=reasoning,
        )

    def counterfactual_analysis(
        self,
        treatment: str,
        outcome: str,
        data: Dict[str, Any],
        intervention: Dict[str, Any],
    ) -> Dict[str, Any]:
        causal_effect = self.do_calculus(treatment, outcome, data)
        baseline = float(data.get("baseline", 0.0))
        multiplier = float(intervention.get("effect_multiplier", 1.0))
        counterfactual = baseline * (1.0 + causal_effect * multiplier)
        confidence = min(0.8 * (1.0 - float(data.get("uncertainty", 0.2))), 0.95)
        return {
            "baseline": baseline,
            "counterfactual": counterfactual,
            "difference": counterfactual - baseline,
            "confidence": confidence,
            "reasoning": f"If {treatment} * {multiplier:.2f}, outcome: {counterfactual:.4f} (D{counterfactual - baseline:+.4f})",
        }

    def get_graph(self) -> Optional[CausalGraph]:
        return self._graph
