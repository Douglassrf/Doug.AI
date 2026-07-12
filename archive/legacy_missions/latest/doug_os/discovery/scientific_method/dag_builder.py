from typing import List, Tuple, Dict, Any, Optional
from dataclasses import dataclass, field
import networkx as nx


@dataclass
class DAGNode:
    name: str
    node_type: str = "variable"  # "treatment" | "outcome" | "confounder" | "variable"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DAGEdge:
    source: str
    target: str
    weight: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class DAGBuilder:
    """
    Construtor de grafos acíclicos direcionados (DAG) para análise causal.

    Garante acyclicidade e oferece utilitários de inspeção de estrutura.
    """

    def __init__(self):
        self._graph: nx.DiGraph = nx.DiGraph()
        self._nodes: Dict[str, DAGNode] = {}
        self._edges: List[DAGEdge] = []

    def add_node(self, node: DAGNode) -> "DAGBuilder":
        self._nodes[node.name] = node
        self._graph.add_node(node.name, **node.metadata)
        return self

    def add_edge(self, edge: DAGEdge) -> "DAGBuilder":
        if edge.source not in self._graph:
            self._graph.add_node(edge.source)
        if edge.target not in self._graph:
            self._graph.add_node(edge.target)

        self._graph.add_edge(edge.source, edge.target, weight=edge.weight, **edge.metadata)

        if not nx.is_directed_acyclic_graph(self._graph):
            self._graph.remove_edge(edge.source, edge.target)
            raise ValueError(
                f"Adding edge {edge.source} → {edge.target} would create a cycle"
            )

        self._edges.append(edge)
        return self

    def build(self) -> nx.DiGraph:
        return self._graph.copy()

    def get_ancestors(self, node: str) -> List[str]:
        return list(nx.ancestors(self._graph, node))

    def get_descendants(self, node: str) -> List[str]:
        return list(nx.descendants(self._graph, node))

    def get_paths(self, source: str, target: str) -> List[List[str]]:
        try:
            return list(nx.all_simple_paths(self._graph, source, target))
        except (nx.NodeNotFound, nx.NetworkXNoPath):
            return []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [
                {"name": n.name, "type": n.node_type, "metadata": n.metadata}
                for n in self._nodes.values()
            ],
            "edges": [
                {"source": e.source, "target": e.target, "weight": e.weight}
                for e in self._edges
            ],
        }
