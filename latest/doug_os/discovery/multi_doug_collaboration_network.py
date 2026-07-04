from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


@dataclass
class DougNode:
    id: str = field(default_factory=lambda: f"dn_{uuid.uuid4().hex[:12]}")
    name: str = ""
    version: str = "1.0.0"
    trust_score: float = 0.5
    shared_discoveries: List[Dict[str, Any]] = field(default_factory=list)
    shared_risks: List[Dict[str, Any]] = field(default_factory=list)
    last_contact: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "trust_score": self.trust_score,
            "shared_discoveries": self.shared_discoveries[-10:],
            "shared_risks": self.shared_risks[-10:],
            "last_contact": self.last_contact.isoformat(),
            "status": self.status,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CollaborationEvent:
    id: str = field(default_factory=lambda: f"ce_{uuid.uuid4().hex[:12]}")
    source_node: str = ""
    target_node: str = ""
    event_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    verified: bool = False
    conflict: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "source_node": self.source_node,
            "target_node": self.target_node,
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "verified": self.verified,
            "conflict": self.conflict,
        }


class MultiDougCollaborationNetwork:
    """Rede de colaboração Multi-Doug com trust score, partilha de descobertas e resolução de conflitos."""

    def __init__(self, trust_threshold: float = 0.6) -> None:
        self._nodes: Dict[str, DougNode] = {}
        self._events: List[CollaborationEvent] = []
        self._trust_threshold = trust_threshold

    def register_node(self, name: str, version: str = "1.0.0") -> DougNode:
        node = DougNode(name=name, version=version)
        self._nodes[node.id] = node
        return node

    def update_trust(self, node_id: str, delta: float) -> bool:
        node = self._nodes.get(node_id)
        if not node:
            return False
        node.trust_score = max(0.0, min(1.0, node.trust_score + delta))
        return True

    def share_discovery(self, source_id: str, discovery: Dict[str, Any]) -> List[CollaborationEvent]:
        source = self._nodes.get(source_id)
        if not source:
            return []

        events: List[CollaborationEvent] = []
        for nid, node in self._nodes.items():
            if nid == source_id or node.trust_score < self._trust_threshold:
                continue
            conflict = self._detect_conflict(discovery, node.shared_discoveries)
            event = CollaborationEvent(
                source_node=source_id,
                target_node=nid,
                event_type="discovery_share",
                payload=discovery,
                conflict=conflict,
                verified=not conflict,
            )
            if not conflict:
                node.shared_discoveries.append(discovery)
            events.append(event)
            self._events.append(event)
        return events

    def share_risk(self, source_id: str, risk: Dict[str, Any]) -> List[CollaborationEvent]:
        source = self._nodes.get(source_id)
        if not source:
            return []

        events: List[CollaborationEvent] = []
        for nid, node in self._nodes.items():
            if nid == source_id or node.trust_score < self._trust_threshold:
                continue
            event = CollaborationEvent(
                source_node=source_id,
                target_node=nid,
                event_type="risk_share",
                payload=risk,
                verified=True,
            )
            node.shared_risks.append(risk)
            events.append(event)
            self._events.append(event)
        return events

    def _detect_conflict(self, discovery: Dict, existing: List[Dict]) -> bool:
        d_dir = discovery.get("direction")
        for e in existing:
            e_dir = e.get("direction")
            if d_dir == "buy" and e_dir == "sell":
                return True
            if d_dir == "sell" and e_dir == "buy":
                return True
        return False

    def get_network_status(self) -> Dict[str, Any]:
        total = len(self._nodes)
        return {
            "total_nodes": total,
            "active_nodes": sum(1 for n in self._nodes.values() if n.status == "active"),
            "avg_trust": sum(n.trust_score for n in self._nodes.values()) / total if total else 0.0,
            "total_events": len(self._events),
            "conflicts_resolved": sum(1 for e in self._events if e.conflict),
            "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
        }
