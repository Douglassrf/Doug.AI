from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import hashlib


@dataclass
class MemoryNode:
    id: str = field(default_factory=lambda: f"mn_{uuid.uuid4().hex[:12]}")
    name: str = ""
    host: str = ""
    port: int = 0
    status: str = "active"
    replicas: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
    last_sync: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "status": self.status,
            "replicas": self.replicas,
            "last_sync": self.last_sync.isoformat(),
            "created_at": self.created_at.isoformat(),
        }


class DistributedMemoryFabric:
    """Tecido de memória distribuída com replicação consistente e hash routing."""

    def __init__(self, replication_factor: int = 2) -> None:
        self._nodes: Dict[str, MemoryNode] = {}
        self._replication_factor = replication_factor

    def add_node(self, name: str, host: str, port: int) -> MemoryNode:
        node = MemoryNode(name=name, host=host, port=port)
        self._nodes[node.id] = node
        return node

    def set(self, key: str, value: Any) -> bool:
        primary_id = self._get_node_for_key(key)
        if not primary_id:
            return False
        primary = self._nodes[primary_id]
        primary.data[key] = value
        self._replicate(key, value, primary_id)
        return True

    def get(self, key: str) -> Optional[Any]:
        node_id = self._get_node_for_key(key)
        if not node_id:
            return None
        return self._nodes[node_id].data.get(key)

    def delete(self, key: str) -> bool:
        if not self._nodes:
            return False
        found = False
        for node in self._nodes.values():
            if key in node.data:
                del node.data[key]
                found = True
        return found

    def _get_node_for_key(self, key: str) -> Optional[str]:
        if not self._nodes:
            return None
        node_ids = sorted(self._nodes.keys())
        hash_val = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
        return node_ids[hash_val % len(node_ids)]

    def _replicate(self, key: str, value: Any, primary_id: str) -> None:
        replicas: List[str] = []
        for nid, node in self._nodes.items():
            if nid != primary_id and len(replicas) < self._replication_factor:
                node.data[key] = value
                replicas.append(nid)
        primary = self._nodes[primary_id]
        primary.replicas = replicas
        primary.last_sync = datetime.now(timezone.utc)

    def sync_all(self) -> None:
        all_data: Dict[str, Any] = {}
        for node in self._nodes.values():
            all_data.update(node.data)
        now = datetime.now(timezone.utc)
        for node in self._nodes.values():
            node.data = dict(all_data)
            node.last_sync = now

    def get_cluster_status(self) -> Dict[str, Any]:
        return {
            "total_nodes": len(self._nodes),
            "active_nodes": sum(1 for n in self._nodes.values() if n.status == "active"),
            "total_keys": sum(len(n.data) for n in self._nodes.values()),
            "replication_factor": self._replication_factor,
            "nodes": {nid: n.to_dict() for nid, n in self._nodes.items()},
        }
