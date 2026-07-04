from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import networkx as nx


@dataclass
class KnowledgeNode:
    id: str = field(default_factory=lambda: f"kn_{uuid.uuid4().hex[:12]}")
    type: str = ""
    name: str = ""
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    confidence: float = 0.5
    source: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "type": self.type, "name": self.name,
            "description": self.description, "properties": self.properties,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "confidence": self.confidence, "source": self.source,
        }


@dataclass
class KnowledgeEdge:
    id: str = field(default_factory=lambda: f"ke_{uuid.uuid4().hex[:12]}")
    source_id: str = ""
    target_id: str = ""
    relationship: str = ""
    weight: float = 1.0
    confidence: float = 0.5
    properties: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "source_id": self.source_id, "target_id": self.target_id,
            "relationship": self.relationship, "weight": self.weight,
            "confidence": self.confidence, "properties": self.properties,
            "created_at": self.created_at.isoformat(),
        }


class GlobalKnowledgeGraph:
    def __init__(self):
        self._graph = nx.MultiDiGraph()
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._edges: Dict[str, KnowledgeEdge] = {}
        self._node_index: Dict[str, Set[str]] = {}
        self._relationship_index: Dict[str, Set[str]] = {}

    def add_node(self, node: KnowledgeNode) -> None:
        self._nodes[node.id] = node
        self._graph.add_node(node.id, **node.to_dict())
        self._node_index.setdefault(node.type, set()).add(node.id)

    def add_edge(self, edge: KnowledgeEdge) -> None:
        if edge.source_id not in self._nodes or edge.target_id not in self._nodes:
            raise ValueError("Source or target node not found")
        self._edges[edge.id] = edge
        self._graph.add_edge(edge.source_id, edge.target_id, key=edge.id, **edge.to_dict())
        self._relationship_index.setdefault(edge.relationship, set()).add(edge.id)

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        return self._nodes.get(node_id)

    def get_nodes_by_type(self, node_type: str) -> List[KnowledgeNode]:
        return [self._nodes[nid] for nid in self._node_index.get(node_type, set()) if nid in self._nodes]

    def traverse(self, start_id: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        if start_id not in self._graph:
            return []
        result, visited, queue = [], set(), [(start_id, 0)]
        while queue:
            node_id, depth = queue.pop(0)
            if node_id in visited or depth > max_depth:
                continue
            visited.add(node_id)
            node = self._nodes.get(node_id)
            if node:
                result.append({"node": node.to_dict(), "depth": depth,
                                "neighbors": list(self._graph.neighbors(node_id))})
            for nb in self._graph.neighbors(node_id):
                if nb not in visited:
                    queue.append((nb, depth + 1))
        return result

    def semantic_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        q = query.lower()
        results = []
        for node in self._nodes.values():
            score = 0.0
            if q in node.name.lower(): score += 0.5
            if q in node.description.lower(): score += 0.3
            for v in node.properties.values():
                if isinstance(v, str) and q in v.lower():
                    score += 0.2
                    break
            if score > 0:
                results.append({"node": node.to_dict(), "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:max_results]

    def find_path(self, source_id: str, target_id: str) -> List[str]:
        if source_id not in self._graph or target_id not in self._graph:
            return []
        try:
            return nx.shortest_path(self._graph, source_id, target_id)
        except nx.NetworkXNoPath:
            return []

    def get_relationship_edges(self, relationship: str) -> List[KnowledgeEdge]:
        return [self._edges[eid] for eid in self._relationship_index.get(relationship, set()) if eid in self._edges]

    def get_connected_nodes(self, node_id: str, relationship: Optional[str] = None) -> List[KnowledgeNode]:
        if node_id not in self._graph:
            return []
        neighbors = []
        for nb_id in self._graph.neighbors(node_id):
            if relationship:
                edges = self._graph.get_edge_data(node_id, nb_id)
                if edges and any(e.get("relationship") == relationship for e in edges.values()):
                    neighbors.append(self._nodes[nb_id])
            else:
                neighbors.append(self._nodes[nb_id])
        return [n for n in neighbors if n is not None]

    def get_temporal_graph(self, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        nodes = [n for n in self._nodes.values() if start_date <= n.created_at <= end_date]
        edges = [e for e in self._edges.values() if start_date <= e.created_at <= end_date]
        return {"nodes": [n.to_dict() for n in nodes], "edges": [e.to_dict() for e in edges]}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
            "edges": {eid: e.to_dict() for eid, e in self._edges.items()},
        }
