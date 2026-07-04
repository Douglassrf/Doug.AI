from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
import uuid
import networkx as nx


@dataclass
class GraphNode:
    id: str = field(default_factory=lambda: f"gn_{uuid.uuid4().hex[:12]}")
    type: str = ""
    label: str = ""
    description: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    importance: float = 0.5
    confidence: float = 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "type": self.type, "label": self.label,
            "description": self.description, "properties": self.properties,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance, "confidence": self.confidence,
        }


@dataclass
class GraphEdge:
    id: str = field(default_factory=lambda: f"ge_{uuid.uuid4().hex[:12]}")
    source: str = ""
    target: str = ""
    relationship: str = ""
    weight: float = 1.0
    confidence: float = 0.5
    properties: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "source": self.source, "target": self.target,
            "relationship": self.relationship, "weight": self.weight,
            "confidence": self.confidence, "properties": self.properties,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class GraphQueryResult:
    nodes: List[GraphNode] = field(default_factory=list)
    edges: List[GraphEdge] = field(default_factory=list)
    paths: List[List[str]] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
            "paths": self.paths,
            "confidence": self.confidence,
            "created_at": self.created_at.isoformat(),
        }


class MarketMemoryGraphEngine:
    def __init__(self):
        self._graph = nx.MultiDiGraph()
        self._nodes: Dict[str, GraphNode] = {}
        self._edges: Dict[str, GraphEdge] = {}
        self._node_index: Dict[str, Set[str]] = {}
        self._relationship_index: Dict[str, Set[str]] = {}
        self._temporal_index: Dict[str, List[str]] = {}

    def add_node(self, node: GraphNode) -> None:
        self._nodes[node.id] = node
        self._graph.add_node(node.id, **node.to_dict())
        self._node_index.setdefault(node.type, set()).add(node.id)
        date_key = node.timestamp.strftime("%Y-%m-%d")
        self._temporal_index.setdefault(date_key, []).append(node.id)

    def add_edge(self, edge: GraphEdge) -> None:
        if edge.source not in self._nodes or edge.target not in self._nodes:
            raise ValueError("Source or target node not found")
        self._edges[edge.id] = edge
        self._graph.add_edge(edge.source, edge.target, key=edge.id, **edge.to_dict())
        self._relationship_index.setdefault(edge.relationship, set()).add(edge.id)

    def add_market_event(
        self, event_type: str, description: str,
        properties: Dict[str, Any], importance: float = 0.5
    ) -> GraphNode:
        node = GraphNode(type="market_event", label=event_type,
                         description=description, properties=properties, importance=importance)
        self.add_node(node)
        return node

    def add_decision(
        self, decision: str, properties: Dict[str, Any], confidence: float = 0.5
    ) -> GraphNode:
        node = GraphNode(type="decision", label=decision,
                         properties=properties, confidence=confidence)
        self.add_node(node)
        return node

    def add_causal_relationship(
        self, cause_id: str, effect_id: str, description: str = "", weight: float = 1.0
    ) -> GraphEdge:
        edge = GraphEdge(source=cause_id, target=effect_id, relationship="causes",
                         weight=weight, properties={"description": description})
        self.add_edge(edge)
        return edge

    def add_temporal_relationship(
        self, before_id: str, after_id: str, description: str = ""
    ) -> GraphEdge:
        edge = GraphEdge(source=before_id, target=after_id, relationship="precedes",
                         properties={"description": description})
        self.add_edge(edge)
        return edge

    def query_events_by_type(self, event_type: str) -> List[GraphNode]:
        return [self._nodes[nid] for nid in self._node_index.get(event_type, set())
                if nid in self._nodes]

    def query_relationships(self, relationship: str) -> List[GraphEdge]:
        return [self._edges[eid] for eid in self._relationship_index.get(relationship, set())
                if eid in self._edges]

    def query_path(
        self, source_id: str, target_id: str, max_depth: int = 5
    ) -> GraphQueryResult:
        result = GraphQueryResult()
        if source_id not in self._graph or target_id not in self._graph:
            return result
        try:
            paths = list(nx.all_simple_paths(self._graph, source_id, target_id, cutoff=max_depth))
            result.paths = paths
            seen_nodes: Set[str] = set()
            seen_edges: Set[str] = set()
            for path in paths[:5]:
                for nid in path:
                    if nid in self._nodes and nid not in seen_nodes:
                        result.nodes.append(self._nodes[nid])
                        seen_nodes.add(nid)
                for i in range(len(path) - 1):
                    edge_data = self._graph.get_edge_data(path[i], path[i + 1])
                    if edge_data:
                        for eid in edge_data:
                            if eid in self._edges and eid not in seen_edges:
                                result.edges.append(self._edges[eid])
                                seen_edges.add(eid)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            pass
        result.confidence = 0.5 if result.paths else 0.0
        return result

    def search_similar_events(self, description: str, max_results: int = 10) -> List[GraphNode]:
        results = []
        desc_lower = description.lower()
        for node in self._nodes.values():
            if node.type != "market_event":
                continue
            score = 0.0
            if desc_lower in node.description.lower():
                score += 0.5
            if desc_lower in node.label.lower():
                score += 0.3
            for v in node.properties.values():
                if isinstance(v, str) and desc_lower in v.lower():
                    score += 0.2
                    break
            if score > 0:
                results.append((node, score))
        results.sort(key=lambda x: x[1], reverse=True)
        return [r[0] for r in results[:max_results]]

    def get_historical_context(self, timestamp: datetime, window_days: int = 7) -> GraphQueryResult:
        result = GraphQueryResult()
        start_date = timestamp - timedelta(days=window_days)
        for date_key, node_ids in self._temporal_index.items():
            try:
                date = datetime.strptime(date_key, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if start_date <= date <= timestamp:
                for nid in node_ids:
                    if nid in self._nodes:
                        result.nodes.append(self._nodes[nid])
        result.confidence = min(len(result.nodes) / 100, 1.0)
        return result

    def get_graph_statistics(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self._nodes),
            "total_edges": len(self._edges),
            "node_types": {t: len(ids) for t, ids in self._node_index.items()},
            "relationship_types": {r: len(ids) for r, ids in self._relationship_index.items()},
            "avg_importance": (sum(n.importance for n in self._nodes.values()) / len(self._nodes)
                               if self._nodes else 0.0),
            "avg_confidence": (sum(n.confidence for n in self._nodes.values()) / len(self._nodes)
                               if self._nodes else 0.0),
        }
