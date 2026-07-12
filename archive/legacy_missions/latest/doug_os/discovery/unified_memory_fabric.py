from typing import Dict, Any, List, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid
import numpy as np


class MemoryType:
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"
    TEMPORAL = "temporal"
    WORKING = "working"
    CONTEXT = "context"
    LONG_TERM = "long_term"


@dataclass
class MemoryEntry:
    id: str = field(default_factory=lambda: f"mem_{uuid.uuid4().hex[:12]}")
    memory_type: str = MemoryType.SEMANTIC
    key: str = ""
    value: Any = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    importance: float = 0.5
    access_count: int = 0
    last_access: Optional[datetime] = None
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "memory_type": self.memory_type, "key": self.key,
            "value": self.value, "timestamp": self.timestamp.isoformat(),
            "importance": self.importance, "access_count": self.access_count,
            "last_access": self.last_access.isoformat() if self.last_access else None,
            "tags": list(self.tags), "metadata": self.metadata,
        }


class UnifiedMemoryFabric:
    def __init__(self, max_working_memory: int = 100):
        self._memories: Dict[str, MemoryEntry] = {}
        self._index: Dict[str, Set[str]] = {}
        self._type_index: Dict[str, Set[str]] = {}
        self._tag_index: Dict[str, Set[str]] = {}
        self._working_memory: Dict[str, Any] = {}
        self._context_memory: Dict[str, Any] = {}
        self._max_working = max_working_memory
        self._temporal_order: List[str] = []

    def store(self, memory_type: str, key: str, value: Any, importance: float = 0.5,
              tags: Optional[Set[str]] = None, metadata: Optional[Dict[str, Any]] = None) -> MemoryEntry:
        entry = MemoryEntry(memory_type=memory_type, key=key, value=value,
                            importance=importance, tags=tags or set(), metadata=metadata or {})
        self._memories[entry.id] = entry
        self._index.setdefault(entry.key, set()).add(entry.id)
        self._type_index.setdefault(entry.memory_type, set()).add(entry.id)
        for tag in entry.tags:
            self._tag_index.setdefault(tag, set()).add(entry.id)
        self._temporal_order.append(entry.id)
        if memory_type == MemoryType.WORKING:
            self._working_memory[key] = value
            if len(self._working_memory) > self._max_working:
                oldest_id = min(self._temporal_order, key=lambda x: self._memories[x].timestamp)
                if oldest_id in self._memories:
                    self._working_memory.pop(self._memories[oldest_id].key, None)
                    self._memories.pop(oldest_id, None)
                    self._temporal_order.remove(oldest_id)
        return entry

    def retrieve(self, key: str) -> Optional[Any]:
        ids = self._index.get(key, set())
        if not ids: return None
        latest = max(ids, key=lambda x: self._memories[x].timestamp)
        entry = self._memories.get(latest)
        if entry:
            entry.access_count += 1
            entry.last_access = datetime.now(timezone.utc)
            return entry.value
        return None

    def retrieve_by_type(self, memory_type: str) -> List[MemoryEntry]:
        return [self._memories[mid] for mid in self._type_index.get(memory_type, set()) if mid in self._memories]

    def retrieve_by_tag(self, tag: str) -> List[MemoryEntry]:
        return [self._memories[mid] for mid in self._tag_index.get(tag, set()) if mid in self._memories]

    def retrieve_by_time_range(self, start: datetime, end: datetime) -> List[MemoryEntry]:
        return [e for e in self._memories.values() if start <= e.timestamp <= end]

    def search(self, query: str, max_results: int = 10) -> List[MemoryEntry]:
        q = query.lower()
        results = []
        for entry in self._memories.values():
            score = 0.0
            if q in entry.key.lower(): score += 0.4
            if isinstance(entry.value, str) and q in entry.value.lower(): score += 0.3
            if any(q in t.lower() for t in entry.tags): score += 0.2
            score += entry.importance * 0.1
            if score > 0: results.append({"entry": entry, "score": score})
        results.sort(key=lambda x: x["score"], reverse=True)
        return [r["entry"] for r in results[:max_results]]

    def update_context(self, context: Dict[str, Any]) -> None:
        self._context_memory.update(context)
        for key, value in context.items():
            self.store(MemoryType.CONTEXT, key, value, importance=0.7)

    def get_context(self) -> Dict[str, Any]:
        return self._context_memory.copy()

    def get_working_memory(self) -> Dict[str, Any]:
        return self._working_memory.copy()

    def forget(self, memory_id: str) -> bool:
        entry = self._memories.pop(memory_id, None)
        if not entry: return False
        self._index.get(entry.key, set()).discard(memory_id)
        self._type_index.get(entry.memory_type, set()).discard(memory_id)
        for tag in entry.tags:
            self._tag_index.get(tag, set()).discard(memory_id)
        if memory_id in self._temporal_order:
            self._temporal_order.remove(memory_id)
        return True

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_memories": len(self._memories),
            "by_type": {t: len(ids) for t, ids in self._type_index.items()},
            "working_memory_size": len(self._working_memory),
            "context_memory_size": len(self._context_memory),
            "avg_importance": float(np.mean([e.importance for e in self._memories.values()])) if self._memories else 0.0,
        }
